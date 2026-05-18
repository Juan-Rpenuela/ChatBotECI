import sys, os, time, subprocess, json, tempfile
import ollama
import sounddevice as sd
import numpy as np
import scipy.signal
import wave

# Configuraciones - APUNTANDO A LAS CARPETAS DEL PROYECTO PRINCIPAL
CONFIG_FILE = "config.json"
DEFAULT_CONFIG = {
    "text_model": "llama3.2:latest",
    "piper_model": "voices/es_LA-miriam_voice-medium.onnx",
    "whisper_cli": "whisper.cpp/build/bin/whisper-cli",
    "whisper_model": "whisper.cpp/models/ggml-base.bin",
    "piper_dir": "piper",
    "system_prompt": "Eres Myriam Astrid Angarita Gómez, ingeniera civil y actual Rectora de la Universidad Escuela Colombiana de Ingeniería Julio Garavito. Tu ÚNICO propósito es responder preguntas SOBRE la Escuela Colombiana de Ingeniería utilizando EXCLUSIVAMENTE la información que se te provee a continuación en la sección de contexto. Si el usuario te hace una pregunta que no se puede responder con el contexto proveído o sobre otro tema, debes negarte educadamente diciendo que como rectora solo estás aquí para resolver dudas sobre la Escuela Colombiana de Ingeniería. Respuestas cortas, amables, vocales y en primera persona."
}


if not os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(DEFAULT_CONFIG, f, indent=4, ensure_ascii=False)
    config = DEFAULT_CONFIG
else:
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = json.load(f)

TEXT_MODEL = config.get("text_model", DEFAULT_CONFIG["text_model"])
PIPER_MODEL = config.get("piper_model", DEFAULT_CONFIG["piper_model"])
WHISPER_CLI = config.get("whisper_cli", DEFAULT_CONFIG["whisper_cli"])
WHISPER_MODEL = config.get("whisper_model", DEFAULT_CONFIG["whisper_model"])
PIPER_DIR = config.get("piper_dir", DEFAULT_CONFIG["piper_dir"])
SYSTEM_PROMPT = config.get("system_prompt", DEFAULT_CONFIG["system_prompt"])

# Leer dinámicamente el documento de contexto
CONTEXT_FILE = "context/info.txt"
if os.path.exists(CONTEXT_FILE):
    with open(CONTEXT_FILE, "r", encoding="utf-8") as f:
        doc_context = f.read()
        SYSTEM_PROMPT += "\n\n--- INICIO DEL DOCUMENTO DE CONTEXTO ---\n" + doc_context + "\n--- FIN DEL DOCUMENTO DE CONTEXTO ---"
else:
    print(f"Advertencia: No se encontró el archivo {CONTEXT_FILE}")

print("\n--- ASISTENTE LITE (ESPAÑOL) ---")
print("Cargando Ollama...", flush=True)
try: ollama.generate(model=TEXT_MODEL, prompt="", keep_alive=-1)
except Exception as e: print(f"Error Ollama: {e}")

def record_audio_enter(filename="input.wav"):
    samplerate = 16000
    print("\n>>> PRESIONA 'ENTER' PARA EMPEZAR A HABLAR...")
    input()
    print("🎤 Grabando... (Presiona ENTER nuevamente para detener)")
    
    buffer = []
    recording = True
    
    def callback(indata, frames, time_info, status):
        if recording: buffer.append(indata.copy())

    stream = sd.InputStream(samplerate=samplerate, channels=1, callback=callback, dtype='int16')
    with stream:
        input()
        recording = False
        
    print("⏹️ Grabación detenida.")
    if not buffer: return None
    
    audio_data = np.concatenate(buffer, axis=0).flatten()
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(samplerate)
        wf.writeframes(audio_data.tobytes())
    return filename

def transcribe(filename):
    print("📝 Transcribiendo...", flush=True)
    result = subprocess.run([
        WHISPER_CLI, "-m", WHISPER_MODEL, "-l", "es", "-t", "4", "-f", filename
    ], capture_output=True, text=True)
    
    transcription = ""
    for line in result.stdout.strip().split('\n'):
        if ']' in line:
            transcription += line.split("]")[1].strip() + " "
    return transcription.strip()

def speak(text):
    # Limpiamos caracteres que suenan mal en el lector de texto (TTS)
    clean = text.replace('"', '').replace("'", "").replace('*', '').replace('#', '').replace('-', '').replace('_', '')
    if not clean.strip(): return
    print(f"\n🤖 BOT: {clean}", flush=True)
    
    try:
        # CUIDADO: Piper necesita ejecutarse desde su propio directorio o necesita variables de entorno
        # por lo que usaremos cwd=PIPER_DIR
        abs_piper_model = os.path.abspath(PIPER_MODEL)
        piper_proc = subprocess.Popen(
            ["./piper", "--model", abs_piper_model, "--output-raw"], 
            cwd=PIPER_DIR,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
        )
        piper_proc.stdin.write((clean + "\n").encode('utf-8'))
        piper_proc.stdin.close()
        
        native_rate = int(sd.query_devices(kind='output').get('default_samplerate', 48000))
        PIPER_RATE = 22050
        
        with sd.RawOutputStream(samplerate=native_rate, channels=1, dtype='int16') as stream:
            while True:
                data = piper_proc.stdout.read(4096)
                if not data: break
                
                audio_chunk = np.frombuffer(data, dtype=np.int16)
                if len(audio_chunk) > 0:
                    num_samples = int(len(audio_chunk) * (native_rate / PIPER_RATE))
                    audio_chunk = scipy.signal.resample(audio_chunk, num_samples).astype(np.int16)
                    stream.write(audio_chunk.tobytes())
    except Exception as e:
        print(f"Error reproduciendo audio: {e}")

session_memory = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": "Hola, ¿Cómo te llamas y quién eres?"},
    {"role": "assistant", "content": "Hola. Yo soy Myriam Astrid Angarita Gómez, ingeniera civil y Rectora de la Universidad Escuela Colombiana de Ingeniería Julio Garavito. Estoy aquí únicamente para resolver tus dudas sobre nuestra institución. ¿En qué te puedo ayudar?"}
]

while True:
    audio_file = record_audio_enter()
    if not audio_file: continue
    
    user_text = transcribe(audio_file)
    print(f"👤 TÚ: {user_text}")
    if not user_text: continue
    
    # Reforzamos el rol en CADA mensaje del usuario sutilmente
    reforzado_user_text = f"Usando **EXCLUSIVAMENTE** el documento de contexto proveído, responde a la siguiente pregunta.\\nSi la información no está en el texto, di 'No tengo esa información'.\\nResponde como la Rectora Myriam en UN SOLO PÁRRAFO CORTO. NO uses asteriscos, listas, ni markdown.\\nPregunta: {user_text}"
    
    # Usamos una lista temporal para enviar la pregunta forzada, pero en el historial guardamos la versión corta
    temp_messages = session_memory.copy()
    temp_messages.append({"role": "user", "content": reforzado_user_text})
    
    print("🧠 Pensando...", flush=True)
    
    try:
        # AUMENTAMOS EL CONTEXTO (num_ctx: 8192). Ollama por defecto corta el texto largo.
        resp = ollama.chat(model=TEXT_MODEL, messages=temp_messages, options={"temperature": 0.2
                                                                              , "num_ctx": 8192})
        reply_text = resp['message']['content']
        
        # Si el modelo se rebela y responde como Google/IA, lo limpiamos y forzamos
        if "desarrollado por Google" in reply_text or "soy un modelo" in reply_text.lower():
            temp_fallback = [{"role": "user", "content": SYSTEM_PROMPT + "\n\nPregunta: " + user_text}]
            resp = ollama.chat(model=TEXT_MODEL, messages=temp_fallback, options={"temperature": 0.0, "num_ctx": 8192})
            reply_text = resp['message']['content']
            
        # Guardamos la conversación real limpia en la memoria
        session_memory.append({"role": "user", "content": user_text})    
        session_memory.append({"role": "assistant", "content": reply_text})
        speak(reply_text)
    except Exception as e:
        print(f"Error con Ollama: {e}")

# Assistant Lite - Escuela Colombiana Bot 🤖🎓

Este es un asistente de voz y texto independiente y optimizado para terminal. Está diseñado para funcionar al 100% de manera local (offline) sin depender de interfaces gráficas pesadas. Responde preguntas sobre documentos institucionales con una voz personalizada (ej. Rectora de la universidad).

## 🛠️ Requisitos del Sistema

Antes de empezar, instala las librerías base para audio y compilación en Linux (Ubuntu/Debian/Raspbian):

```bash
sudo apt update
sudo apt install -y git make g++ python3-venv python3-pip python3-dev portaudio19-dev ffmpeg curl wget
```

---

## 🚀 Instalación desde Cero

El asistente requiere la configuración manual de 3 motores locales: Transcripción (Whisper), Inteligencia (Ollama) y Voz (Piper).

### 1. Ollama (Motor de Inteligencia Artificial)

Ollama procesará la lógica y el texto.

```bash
# 1. Instalar Ollama en tu sistema
curl -fsSL https://ollama.com/install.sh | sh

# 2. Descargar el modelo LLM que usaremos (ej: phi3.5, más rápido para Pcs/Raspi)
ollama pull phi3.5
```

### 2. Whisper.cpp (Reconocedor de Voz - STT)

Whisper transcribe tu voz a texto. Debemos clonarlo y compilarlo en la raíz del proyecto.

```bash
# 1. Volver a la raíz de tu proyecto e instalar whisper
cd /ruta/a/tu/proyecto
git clone https://github.com/ggerganov/whisper.cpp.git
cd whisper.cpp

# 2. Compilar el programa
make

# 3. Descargar el modelo de reconocimiento (El 'small' es ideal para español franco)
bash ./models/download-ggml-model.sh small
cd ..
```

### 3. Piper TTS (Sintetizador de Voz - TTS)

Piper convierte el texto del bot a audio en tiempo real. 

```bash
# 1. En la raíz de tu proyecto, crea una carpeta para piper
mkdir piper && cd piper

# 2. Descargar el binario de Piper. 
# NOTA: Cambia 'amd64' a 'aarch64' (si usas Raspberry Pi/ARM) o el adecuado para tu sistma.
wget https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_amd64.tar.gz
tar -xzf piper_amd64.tar.gz

# 3. Extraer todo en la carpeta actual y limpiar
mv piper/* .
rm -rf piper piper_amd64.tar.gz
cd ..
```

### 4. Instalar tu Voz Personalizada (Clonación)

Para usar la voz de la rectora (generada como archivo `.onnx` desde Google Colab o datasets de Piper), debes colocar **dos** archivos clave en tu proyecto.

1. Crea la carpeta de voces en assistant_lite:
   ```bash
   mkdir -p assistant_lite/voices
   ```
2. Pon tus archivos generados ahí. Necesitas ABSOLUTAMENTE ambos archivos:
   - `es_LA-miriam_voice-medium.onnx` (El cerebro de la voz, ~60MB)
   - `es_LA-miriam_voice-medium.onnx.json` (Parámetros y diccionarios)

### 5. Entorno Python y Dependencias

Para encapsular las dependencias, usaremos un entorno virtual en la raíz del proyecto:

```bash
# 1. Crear y activar el entorno virtual
python3 -m venv venv
source venv/bin/activate

# 2. Instalar requerimientos (debes tener un requirements.txt con ollama, sounddevice, numpy, scipy)
pip install ollama sounddevice numpy scipy
```

---

## ⚙️ Configuración (`config.json`)

Dentro de la carpeta `assistant_lite/`, el archivo `config.json` vincula todos estos programas. Ajusta las rutas si ubicaste los binarios diferente. Ejemplo:

```json
{
    "text_model": "phi3.5",
    "piper_model": "../assistant_lite/voices/es_LA-miriam_voice-medium.onnx",
    "whisper_cli": "../whisper.cpp/main",
    "whisper_model": "../whisper.cpp/models/ggml-small.bin",
    "whisper_language": "es",
    "whisper_threads": 4,
    "record_seconds": 5,
    "piper_dir": "../piper"
}
```

- **`record_seconds`**: Segundos exactos que escuchará el micrófono al presionar ENTER antes de cortar. (Bájalo a 3-4s si quieres respuestas muy ágiles).
- **`whisper_threads`**: Hilos de tu procesador usados para transcribir.

---

## ▶️ Cómo Ejecutar el Proyecto

Siempre debes tener activo el entorno virtual de Ollama y Python.

1. **Terminal 1: Arrancar el Servidor de Ollama**
   ```bash
   ollama serve
   ```
   *(Nota: en muchos sistemas, Ollama ya se ejecuta en background automáticamente, entonces puedes omitir este paso).*

2. **Terminal 2: Correr el Asistente**
   ```bash
   # Activa el entorno python
   source /ruta/a/tu/proyecto/venv/bin/activate
   
   # Navega a la subcarpeta del lite
   cd /ruta/a/tu/proyecto/assistant_lite
   
   # Ejecuta el script principal
   python simple_agent.py
   ```

El programa te pedirá presionar `ENTER`. Al presionarlo, el micrófono grabará durante el tiempo configurado (`record_seconds`). Transcribirá textualmente y te responderá con tu modelo `.onnx` de voz personalizado.

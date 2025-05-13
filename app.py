# app.py
import os
from dotenv import load_dotenv
from flask import Flask, render_template, request
import json
from transcriber import Transcriber
from llm import LLM # Tu clase LLM actualizada
from tts import TTS
from character import Char

load_dotenv()
elevenlabs_key = os.getenv('ELEVENLABS_API_KEY') # Necesario para TTS

app = Flask(__name__)
llm_processor = LLM() # Inicializa el LLM una vez

@app.route("/")
def index():
    return render_template("recorder.html")

@app.route("/audio", methods=["POST"])
def audio_route():
    audio_file_storage = request.files.get("audio")
    
    transcribed_text_or_error = Transcriber().transcribe(audio_file_storage)

    if transcribed_text_or_error.startswith("Error:") or \
       transcribed_text_or_error.startswith("No se pudo") or \
       transcribed_text_or_error.startswith("Transcripción bloqueada"):
        print(f"Fallo en la transcripción: {transcribed_text_or_error}")
        tts_file = TTS().process(transcribed_text_or_error)
        return {"result": "error", "text": transcribed_text_or_error, "file": tts_file}

    user_question = transcribed_text_or_error
    print(f"Pregunta transcrita para LLM (Contexto ECI): {user_question}")

    function_name, args, llm_response_or_text = llm_processor.process_question_with_context(user_question)

    final_response_text = llm_response_or_text if not function_name else llm_processor.process_response_after_function(
        original_user_question=user_question,
        gemini_response_object_with_fc=llm_response_or_text,
        function_name=function_name,
        function_response_content_str=""
    )

    print(f"Respuesta final para TTS: {final_response_text}")
    tts_file = TTS().process(final_response_text)

    if not tts_file:
        return {"result": "error", "text": "Error al generar el audio.", "file": None}

    character = Char()
    character_id = character.process(final_response_text)  # Obtener el ID del video
    if not character_id:
       return {"result": "error", "text": "Error al generar el video.", "file": tts_file, "char_file": None}

    char_file = character.obtain(character_id)  # Obtener el archivo de video
    if not char_file:
        return {"result": "error", "text": "Error al descargar el video.", "file": tts_file, "char_file": None}

    return {"result": "ok", "text": final_response_text, "file": tts_file, "char_file": f"/static/{char_file}"}

if __name__ == "__main__":
    app.run(debug=True)
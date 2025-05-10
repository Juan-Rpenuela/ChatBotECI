# app.py
import os
from dotenv import load_dotenv
from flask import Flask, render_template, request
import json
from transcriber import Transcriber
from llm import LLM # Tu clase LLM actualizada
from tts import TTS

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

    # Llamar al nuevo método del LLM
    function_name, args, llm_response_or_text = llm_processor.process_question_with_context(user_question)

    final_response_text = ""

    if function_name:
        print(f"Función detectada: {function_name}, Argumentos: {args}")
        function_execution_result_str = "" # Resultado de la ejecución de la función como string JSON

        # --- Implementa la lógica para tus funciones (tools) aquí ---
        if function_name == "get_official_website":
            # Esta función no toma argumentos según la definición.
            website_info = {"website": "El sitio web oficial es www.escuelaing.edu.co"}
            function_execution_result_str = json.dumps(website_info)
        # Agrega más 'elif' para otras funciones que definas en self.tools
        # elif function_name == "otra_funcion_eci":
        #     # Lógica para otra_funcion_eci
        #     # ...
        #     function_execution_result_str = json.dumps(resultado_de_la_funcion)
        else:
            print(f"Función desconocida: {function_name}")
            function_execution_result_str = json.dumps({"error": f"Función '{function_name}' no reconocida."})

        # Obtener la respuesta final del LLM después de ejecutar la función
        # 'llm_response_or_text' aquí es el objeto de respuesta completo de Gemini que contenía la FunctionCall
        final_response_text = llm_processor.process_response_after_function(
            original_user_question=user_question,
            gemini_response_object_with_fc=llm_response_or_text, # Pasar el objeto completo
            function_name=function_name,
            function_response_content_str=function_execution_result_str
        )
    else:
        # No se llamó a ninguna función, llm_response_or_text es la respuesta directa (string)
        if isinstance(llm_response_or_text, str):
            final_response_text = llm_response_or_text
        # Si llm_response_or_text fuera un objeto de respuesta de Gemini sin FunctionCall (poco probable con la lógica actual de llm.py)
        elif hasattr(llm_response_or_text, 'text') and llm_response_or_text.text:
             final_response_text = llm_response_or_text.text
        else:
            final_response_text = "No pude procesar tu pregunta completamente, pero no se identificó una acción específica."
            print(f"Respuesta inesperada del LLM (sin función): {llm_response_or_text}")


    print(f"Respuesta final para TTS: {final_response_text}")
    tts_file = TTS().process(final_response_text)
    return {"result": "ok", "text": final_response_text, "file": tts_file}

if __name__ == "__main__":
    app.run(debug=True)
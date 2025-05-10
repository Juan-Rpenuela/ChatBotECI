# transcriber.py

import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

if not GEMINI_API_KEY:
    print("Advertencia: GEMINI_API_KEY no encontrada. La transcripción con Gemini fallará.")
else:
    genai.configure(api_key=GEMINI_API_KEY)

class Transcriber:
    def __init__(self, model_name="gemini-1.5-flash"):
        if not GEMINI_API_KEY:
            self.model = None
            print("Error: No se puede inicializar el modelo Gemini para transcripción sin API key.")
            return
        
        try:
            self.model = genai.GenerativeModel(model_name)
        except Exception as e:
            self.model = None
            print(f"Error al inicializar el modelo Gemini ({model_name}): {e}")

    def transcribe(self, audio_file_storage):
        if not self.model:
            return "Error: El modelo de transcripción Gemini no está inicializado."

        # El nombre del archivo temporal. La extensión aquí es solo para nuestra conveniencia;
        # lo importante es el mime_type que enviamos a Gemini.
        temp_audio_path = "temp_audio_for_transcription.audio" 
        
        try:
            audio_file_storage.save(temp_audio_path)
            audio_bytes = open(temp_audio_path, 'rb').read()

            # --- MODIFICACIÓN IMPORTANTE AQUÍ ---
            # Intenta con un tipo MIME específico soportado por Gemini.
            # Los más comunes que podrías estar recibiendo del navegador son 'audio/webm' o 'audio/ogg' (con codec opus).
            # Si estás seguro de que es MP3, usa 'audio/mpeg'.
            # Si es WAV, usa 'audio/wav'.
            # Vamos a probar con 'audio/webm' ya que es un default común de MediaRecorder.
            # Si esto no funciona, necesitarás averiguar el formato exacto que envía tu recorder.js
            # o convertir el audio a un formato conocido en el backend.

            # Intenta primero con el mimetype original si es específico, sino usa un default razonable.
            detected_mimetype = audio_file_storage.mimetype
            print(f"MIME type detectado desde Flask: {detected_mimetype}")

            # Lista de MIME types de audio comunes que Gemini podría soportar
            # (consulta la documentación de Gemini para la lista exacta y actualizada)
            # Ejemplos: "audio/mpeg", "audio/wav", "audio/ogg", "audio/flac", "audio/webm"
            
            # Si el mimetype detectado es genérico, probamos con uno más específico.
            # El formato de salida de MediaRecorder puede variar. `audio/webm` con `codecs=opus` es muy común.
            # `audio/mp4` o `audio/mp3` también podrían ser, dependiendo del navegador y si se especifica.
            # Si tu MediaRecorder está por defecto, `audio/webm` es una buena suposición.
            # Si el archivo se llama .mp3 en el frontend, y realmente es mp3, usa 'audio/mpeg'.
            # Vamos a asumir que el contenido podría ser webm si el mimetype es application/octet-stream
            # o si el mimetype es específico pero no lo reconocemos bien.

            # Determinar el mime_type a usar:
            # Si el nombre del archivo original (del cliente) sugiere un formato:
            original_filename = audio_file_storage.filename.lower() if audio_file_storage.filename else ""

            if original_filename.endswith(".mp3"):
                mime_type_to_use = "audio/mpeg"
            elif original_filename.endswith(".wav"):
                mime_type_to_use = "audio/wav"
            elif original_filename.endswith(".webm"):
                mime_type_to_use = "audio/webm"
            elif original_filename.endswith(".ogg"):
                mime_type_to_use = "audio/ogg" # Generalmente con codec opus o vorbis
            elif detected_mimetype and detected_mimetype != "application/octet-stream":
                mime_type_to_use = detected_mimetype # Confiar en el mimetype detectado si no es genérico
            else:
                # Si sigue siendo genérico, hacemos una suposición basada en la extensión del archivo temporal
                # o un default común como webm. Como nombramos el temp file .audio, esto no ayuda mucho.
                # El recorder.js probablemente envía webm por defecto.
                print("MIME type detectado es genérico o no reconocido, intentando con 'audio/webm'.")
                mime_type_to_use = "audio/webm" # O 'audio/mpeg' si estás más seguro que es mp3

            print(f"Usando MIME type para Gemini: {mime_type_to_use}")
            audio_part = {"mime_type": mime_type_to_use, "data": audio_bytes}
            # --- FIN DE LA MODIFICACIÓN IMPORTANTE ---

            prompt = "Por favor, transcribe el siguiente audio."
            
            print("Generando transcripción con Gemini...")
            response = self.model.generate_content([prompt, audio_part])
            
            if response and response.text:
                transcribed_text = response.text
                print(f"Texto transcrito por Gemini: {transcribed_text}")
                return transcribed_text
            elif response and response.parts:
                 all_text = "".join(part.text for part in response.parts if hasattr(part, 'text'))
                 if all_text:
                    print(f"Texto transcrito por Gemini (desde parts): {all_text}")
                    return all_text
            
            # Si llegamos aquí, la respuesta no tuvo el formato esperado
            print(f"Respuesta inesperada de Gemini (sin texto directo): {response}")
            # Intenta acceder a `response.prompt_feedback` si existe para más info del error
            if hasattr(response, 'prompt_feedback') and response.prompt_feedback:
                print(f"Feedback del prompt de Gemini: {response.prompt_feedback}")
                block_reason = response.prompt_feedback.block_reason
                if block_reason:
                    return f"Transcripción bloqueada por Gemini. Razón: {block_reason}. Revisa las safety settings o el contenido."

            return "No se pudo obtener la transcripción del audio (respuesta inesperada o vacía)."

        except Exception as e:
            error_message = f"Error durante la transcripción con Gemini: {str(e)}"
            print(error_message)
            # Si 'e' es una google.api_core.exceptions.GoogleAPIError, podría tener más detalles.
            if hasattr(e, 'message'): # A veces el error de la API está en e.message
                 print(f"Detalle del error de API: {e.message}")
            return error_message # Devolvemos el mensaje de error para que `app.py` lo maneje
        finally:
            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)
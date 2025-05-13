import os
from dotenv import load_dotenv
import requests
import time

class Char():
    def __init__(self):
        load_dotenv()
        self.key = os.getenv('D_ID_API_KEY')
        print(f"[DEBUG] Clave de ElevenLabs cargada: {self.key}")

    def process(self, text):
        url = "https://api.d-id.com/talks"

        payload = {
            "source_url": "https://i.postimg.cc/CKFnRbJ8/Chat-GPT-Image-May-8-2025-11-30-44-PM.png",
            "script": {
                "type": "text",
                "provider": {
                    "type": "elevenlabs",
                    "voice_id": "x5IDPSl4ZUbhosMmVFTk",
                    "voice_config": {
                        "stability": 0.55,
                        "similarity_boost": 0.55,
                        "model_id": "eleven_multilingual_v2"
                    },
                },
                "input": text,
                "ssml": "false"
            },
            "config": {
                "fluent": "false",
                "driver_expressions": { "expressions": [
                        {
                            "expression": "happy",
                            "start_frame": 0,
                            "intensity": 0.5
                        }
                    ] },
                "stitch": False,
                "result_format": "mp4"
            }
        }
        headers = {
            "accept": "application/json",
            "elevenlabs" : "sk_0101b21ca1b59e062326f3de73b27c91eef3c0e6e406bd1e",
            "content-type": "application/json",
            "Authorization": "Basic " + self.key,
        }

        print("[DEBUG] Enviando solicitud a D-ID API con el siguiente payload:")
        print(payload)

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code != 200:
            print(f"[ERROR] Error en la API de D-ID: {response.status_code}, {response.text}")
        else:
            print(f"[DEBUG] Respuesta exitosa de la API de D-ID: {response.json()}")

        response_json = response.json()

        return response_json.get("id")


    def obtain(self, id):
        url = f"https://api.d-id.com/talks/{id}"
        print(f"[DEBUG] Solicitando video con ID: {id} desde {url}")
        
        headers = {
            "accept": "application/json",
            "Authorization": "Basic " + self.key,
        }
        
        # Esperar hasta que el video esté listo
        for attempt in range(10):  # Intentar hasta 10 veces
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                print(f"[ERROR] Error al obtener detalles del video: {response.status_code}, {response.text}")
                return None
    
            response_json = response.json()
            print(f"[DEBUG] Detalles del video: {response_json}")
            
            status = response_json.get("status")
            print(f"[DEBUG] Estado del video: {status}")
            if status == "done":
                result_url = response_json.get("result_url")
                if not result_url:
                    print("[ERROR] No se encontró 'result_url' en la respuesta.")
                    return None
                print(f"[DEBUG] URL del video: {result_url}")
                break
            elif status in ["created", "started"]:
                print(f"[DEBUG] El video aún no está listo (estado: {status}). Esperando...")
                time.sleep(5)  # Esperar 5 segundos antes de volver a intentar
            else:
                print(f"[ERROR] Estado inesperado del video: {status}")
                return None
        else:
            print("[ERROR] El video no estuvo listo después de varios intentos.")
            return None
    
        # Descargar el archivo desde 'result_url'
        video_response = requests.get(result_url, stream=True)
        
        if video_response.status_code != 200:
            print(f"[ERROR] Error al descargar el video: {video_response.status_code}")
            return None
    
        file_name = "response.mp4"
        file_path = os.path.join("static", file_name)
        print(f"[DEBUG] Guardando video en: {file_path}")
    
        # Guardar el contenido del video en un archivo
        try:
            with open(file_path, 'wb') as f:
                for chunk in video_response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            print(f"[DEBUG] Video guardado exitosamente en: {file_path}")
            return file_name
        except Exception as e:
            print(f"[ERROR] Error al guardar el video: {e}")
            return None
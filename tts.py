import os
from dotenv import load_dotenv
import requests

#Texto a voz. Esta impl utiliza ElevenLabs
class TTS():
    def __init__(self):
        load_dotenv()
        self.key = os.getenv('ELEVENLABS_API_KEY')
        print (f"Clave de ElevenLabs: {self.key}")

    def process(self, text):
        CHUNK_SIZE = 1024
        url = "https://api.elevenlabs.io/v1/text-to-speech/x5IDPSl4ZUbhosMmVFTk"
    
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": "sk_0101b21ca1b59e062326f3de73b27c91eef3c0e6e406bd1e"
        }
    
        data = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.55,
                "similarity_boost": 0.55
            }
        }
    
        response = requests.post(url, json=data, headers=headers)
    
        if response.status_code != 200:
            print(f"Error en la API de ElevenLabs: {response.text}")
            return None
    
        file_name = "response.mp3"
        with open("static/" + file_name, 'wb') as f:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                if chunk:
                    f.write(chunk)
    
        return file_name
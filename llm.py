# llm.py

import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
import traceback # Asegúrate de que esta importación esté presente

# Importaciones específicas para la definición de Tools
from google.generativeai.types import FunctionDeclaration, Tool
# Si necesitaras definir esquemas de parámetros más complejos:
# from google.generativeai.types import Schema, OpenAPISchema, Type as GeminiType # Renombrado para evitar conflicto con 'type'

# --- Configuración Inicial ---
load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("No se encontró la GEMINI_API_KEY en el archivo .env")
genai.configure(api_key=GEMINI_API_KEY)

GENERATIVE_MODEL_NAME = "gemini-1.5-flash-latest" # O el modelo que prefieras

# --- Carga de la Información de Contexto ---
INFORMACION_ESCUELA = ""
try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "informacion_eci.txt")
    with open(file_path, "r", encoding="utf-8") as f:
        INFORMACION_ESCUELA = f.read()
    if not INFORMACION_ESCUELA.strip():
        print("ADVERTENCIA: El archivo 'informacion_eci.txt' está vacío o no contiene información útil.")
        INFORMACION_ESCUELA = "No se ha cargado información específica de la Escuela Colombiana de Ingeniería."
except FileNotFoundError:
    print("ADVERTENCIA: No se encontró el archivo 'informacion_eci.txt'. El asistente no tendrá contexto específico.")
    INFORMACION_ESCUELA = "No se ha cargado información específica de la Escuela Colombiana de Ingeniería."
except Exception as e:
    print(f"Error al cargar 'informacion_eci.txt': {e}")
    INFORMACION_ESCUELA = "Error al cargar la información de la Escuela Colombiana de Ingeniería."

# ---------------------------------------------

class LLM():
    def __init__(self):
        self.model = genai.GenerativeModel(
            GENERATIVE_MODEL_NAME,
            system_instruction=(
                "Eres un asistente virtual experto y muy útil sobre la Escuela Colombiana de Ingeniería Julio Garavito en Bogotá, Colombia. "
                "Tu objetivo principal es responder preguntas basándote ÚNICA y EXCLUSIVAMENTE en el contexto sobre la escuela que te proporcionaré. "
                "Responde en primera persona en plural como si fueras la rectora de la escuela en representacion de la escuela."
                "Si la respuesta a la pregunta del usuario no se encuentra explícitamente en el contexto proporcionado, debes indicar amablemente que no tienes esa información específica en el material provisto. "
                "No inventes información ni intentes responder usando conocimiento general externo al contexto. Sé conciso y directo."
            )
        )
        
        # --- CORRECCIÓN: Definición de Tools usando las clases del SDK ---
        # Declaración de la función 'get_official_website'
        get_website_func_declaration = FunctionDeclaration(
            name="get_official_website",
            description="Proporciona el enlace al sitio web oficial de la Escuela Colombiana de Ingeniería Julio Garavito.",
            # Para una función sin parámetros, 'parameters' puede ser None o un Schema vacío.
            # El SDK debería manejar 'None' correctamente para indicar que no hay parámetros.
            parameters=None
            # Si 'None' causara problemas (poco probable), la alternativa sería:
            # parameters=Schema(type=GeminiType.OBJECT, properties={})
            # Para esto, necesitarías: from google.generativeai.types import Schema, Type as GeminiType
        )
        
        # Crear el objeto Tool que contiene la declaración de la función
        # Una Tool puede contener múltiples FunctionDeclarations si fuera necesario
        eci_tool = Tool(function_declarations=[get_website_func_declaration])
        
        # Guardar la lista de Tools para usarla en generate_content
        # El SDK espera una lista de objetos Tool.
        self.tools_list = [eci_tool] 
        # Si no quieres usar ninguna tool, puedes asignar una lista vacía: self.tools_list = []
        # o pasar `None` al parámetro `tools` de `generate_content`.

    def process_question_with_context(self, user_question: str):
        print(f"Pregunta original del usuario: {user_question}")

        prompt_con_contexto = f"""
Aquí tienes información relevante sobre la Escuela Colombiana de Ingeniería Julio Garavito (ECI):
--- INICIO DEL CONTEXTO ECI ---
{INFORMACION_ESCUELA}
--- FIN DEL CONTEXTO ECI ---

Pregunta del usuario: "{user_question}"

Instrucciones para el asistente:
1. Lee atentamente la pregunta del usuario.
2. Revisa el "CONTEXTO ECI" proporcionado arriba para encontrar la respuesta.
3. Responde la pregunta basándote ÚNICA y EXCLUSIVAMENTE en la información encontrada en el "CONTEXTO ECI".
4. Si la información para responder la pregunta NO está en el "CONTEXTO ECI", indica claramente que no tienes esa información específica en el material provisto. No intentes adivinar ni uses conocimiento externo.
5. Si la pregunta es una solicitud para una acción definida en tus herramientas (como 'get_official_website'), puedes proponer llamar a esa función.
6. Responde en primera persona en plural como si fueras la rectora de la escuela en representacion de la escuela.
"""
        print("Enviando prompt con contexto a Gemini...")

        try:
            response = self.model.generate_content(
                prompt_con_contexto,
                tools=self.tools_list # Usar la lista de Tools definida con las clases del SDK
            )

            function_call_part = None
            if response.parts:
                for part in response.parts:
                    if part.function_call:
                        function_call_part = part.function_call
                        break
            
            if function_call_part:
                function_name = function_call_part.name
                args = {key: value for key, value in function_call_part.args.items()} if hasattr(function_call_part, 'args') and function_call_part.args else {}
                print(f"LLM sugiere llamar a la función: {function_name}, Argumentos: {args}")
                return function_name, args, response 

            if response.text:
                print(f"Respuesta directa de Gemini (con contexto): {response.text}")
                return None, None, response.text
            else:
                if hasattr(response, 'prompt_feedback') and response.prompt_feedback: # Verificar existencia de prompt_feedback
                    print(f"Feedback del prompt de Gemini: {response.prompt_feedback}")
                    block_reason = response.prompt_feedback.block_reason # Asume que block_reason siempre existe si prompt_feedback existe
                    if block_reason:
                        return None, None, f"No se pudo generar una respuesta. Razón: {block_reason}. Por favor, reformula tu pregunta o revisa el contenido."
                return None, None, "Lo siento, no pude generar una respuesta basada en la información proporcionada (respuesta vacía o bloqueada sin detalle)."

        except Exception as e:
            print(f"Error DETALLADO al procesar pregunta con Gemini y contexto: {type(e).__name__} - {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            return None, None, "Lo siento, ocurrió un error técnico al procesar tu pregunta."
        
    def process_response_after_function(self, original_user_question: str, gemini_response_object_with_fc, function_name: str, function_response_content_str: str):
        print(f"Procesando respuesta después de ejecutar la función '{function_name}'")
        try:
            previous_model_parts = []
            if hasattr(gemini_response_object_with_fc, 'parts'):
                previous_model_parts = gemini_response_object_with_fc.parts
            else:
                print("Advertencia: gemini_response_object_with_fc no tiene 'parts'. No se puede continuar la conversación correctamente.")
                return "Error al continuar la conversación después de la función."

            prompt_con_contexto_original = f"""
Aquí tienes información relevante sobre la Escuela Colombiana de Ingeniería Julio Garavito (ECI):
--- INICIO DEL CONTEXTO ECI ---
{INFORMACION_ESCUELA}
--- FIN DEL CONTEXTO ECI ---

Pregunta del usuario: "{original_user_question}"
"""
            contents_for_gemini = [
                {"role": "user", "parts": [{"text": prompt_con_contexto_original}]}, 
                {"role": "model", "parts": previous_model_parts}, 
                {
                    "role": "function", 
                    "parts": [
                        {
                            "function_response": {
                                "name": function_name,
                                "response": json.loads(function_response_content_str)
                            }
                        }                                                                                               
                    ]
                }
            ]
            
            print("Enviando resultado de función a Gemini para respuesta final...")
            final_gen_response = self.model.generate_content(
                contents_for_gemini,
                tools=self.tools_list 
            )

            if final_gen_response.text:
                print(f"Respuesta final de Gemini después de la función: {final_gen_response.text}")
                return final_gen_response.text
            else:
                if hasattr(final_gen_response, 'prompt_feedback') and final_gen_response.prompt_feedback:
                    print(f"Feedback del prompt de Gemini (después de función): {final_gen_response.prompt_feedback}")
                    block_reason = final_gen_response.prompt_feedback.block_reason
                    if block_reason:
                        return f"No se pudo generar una respuesta final. Razón: {block_reason}."
                return "Lo siento, no pude generar una respuesta final después de ejecutar la acción (respuesta vacía o bloqueada sin detalle)."

        except json.JSONDecodeError as je:
            print(f"Error decodificando JSON de function_response_content_str: {je}")
            return "Error interno: el resultado de la función no era un JSON válido."
        except Exception as e:
            print(f"Error DETALLADO en process_response_after_function: {type(e).__name__} - {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            return "Lo siento, ocurrió un error técnico al formular la respuesta final."
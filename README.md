# Asistente Virtual - Escuela Colombiana de Ingeniería Julio Garavito

Este repositorio contiene el código para un chatbot diseñado específicamente para la Escuela Colombiana de Ingeniería Julio Garavito. El asistente virtual está enfocado en responder preguntas relacionadas con la institución, utilizando un modelo de lenguaje avanzado y herramientas de procesamiento de voz.

Actualmente, el proyecto utiliza la API de **Gemini AI** para el procesamiento de lenguaje natural, pero está diseñado de manera modular, lo que permite adaptarlo fácilmente a otras APIs de inteligencia artificial según las necesidades del usuario.

## Configuración
Para ejecutar el proyecto, sigue estos pasos:

1. **Descargar el repositorio**:
   - Clona este repositorio en tu máquina local.

2. **Opcional: Crear un ambiente virtual**:
   - Se recomienda crear un ambiente virtual para evitar conflictos de dependencias.

3. **Instalar las dependencias**:
   - Ejecuta el siguiente comando:
     ```bash
     pip install -r requirements.txt
     ```

4. **Crear un archivo `.env`**:
   - En el archivo `.env`, coloca las claves necesarias para los servicios utilizados. Por ejemplo:
     ```
     OPENAI_API_KEY=XXXXXX
     ELEVENLABS_API_KEY=XXXXXX
     ```

5. **Agregar información de contexto**:
   - Crea un archivo llamado `informacion_eci.txt` en el directorio raíz del proyecto. Este archivo debe contener información relevante sobre la Escuela Colombiana de Ingeniería Julio Garavito.

## Ejecución
Este proyecto utiliza Flask como framework web. Para ejecutar el servidor:

1. Levanta el servidor en modo debug con el siguiente comando:
   ```bash
   flask --app app run --debug

2. Abre tu navegador y ve a http://localhost:5000

3. Da clic para comenzar a grabar (el navegador pedirá permiso para usar el micrófono). Da clic nuevamente para detener la grabación.

4. Espera la respuesta del asistente virtual.

## Créditos
Este proyecto está basado en el repositorio del Asistente Virtual desarrollado por Ringa Tech. Puedes ver el video original en el siguiente enlace:  
[https://youtu.be/-0tIy8wWtzE](https://youtu.be/-0tIy8wWtzE)

## Licencias
- Imagen de micrófono por Freepik.

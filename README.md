# Assistant Lite - Escuela Colombiana Bot

Assistant Lite is an independent voice and text assistant optimized for terminal environments. It is designed to run entirely locally (offline), without relying on heavy graphical interfaces. The assistant answers questions about institutional documents using a custom voice (e.g., the university's Rector).

## System Requirements

Before getting started, install the required system libraries for audio processing and compilation on Linux (Ubuntu/Debian/Raspberry Pi OS):

```bash
sudo apt update
sudo apt install -y git make g++ python3-venv python3-pip python3-dev portaudio19-dev ffmpeg curl wget
```

---

## Installation from Scratch

The assistant requires the manual setup of three local engines:

* **Whisper** (Speech-to-Text)
* **Ollama** (LLM Inference)
* **Piper** (Text-to-Speech)

### 1. Ollama (AI Engine)

Ollama handles the language model inference and text generation.

```bash
# 1. Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 2. Download the LLM model (phi3.5 is recommended for PCs and Raspberry Pi)
ollama pull phi3.5
```

---

### 2. Whisper.cpp (Speech-to-Text)

Whisper transcribes spoken audio into text.

```bash
# 1. Go to your project root and clone whisper.cpp
cd /path/to/your/project
git clone https://github.com/ggerganov/whisper.cpp.git
cd whisper.cpp

# 2. Build the project
make

# 3. Download the speech recognition model
# The "small" model offers a good balance between speed and accuracy.
bash ./models/download-ggml-model.sh small

cd ..
```

---

### 3. Piper TTS (Text-to-Speech)

Piper converts the assistant's responses into speech in real time.

```bash
# 1. Create a folder for Piper
mkdir piper && cd piper

# 2. Download the appropriate Piper binary.
# NOTE: Replace "amd64" with "aarch64" if you're using a Raspberry Pi or another ARM-based device.
wget https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_amd64.tar.gz

tar -xzf piper_amd64.tar.gz

# 3. Extract everything into the current directory and clean up
mv piper/* .
rm -rf piper piper_amd64.tar.gz

cd ..
```

---

### 4. Install Your Custom Voice

To use a cloned voice (such as the Rector's voice generated with Google Colab or Piper datasets), place **both** required files into the project.

1. Create the voices directory:

```bash
mkdir -p assistant_lite/voices
```

2. Copy the following files into that folder:

* `es_LA-miriam_voice-medium.onnx` *(Voice model, approximately 60 MB)*
* `es_LA-miriam_voice-medium.onnx.json` *(Voice configuration and dictionaries)*

Both files are required for Piper to synthesize speech correctly.

---

### 5. Python Virtual Environment

To isolate project dependencies, create a virtual environment in the project root.

```bash
# Create and activate the virtual environment
python3 -m venv venv
source venv/bin/activate

# Install the required Python packages
pip install ollama sounddevice numpy scipy
```

---

## Configuration (`config.json`)

Inside the `assistant_lite/` directory, edit `config.json` so it points to the correct binaries and models.

Example:

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

### Configuration Options

* **`record_seconds`**: Number of seconds the microphone records after pressing **ENTER**. Reduce it to **3–4 seconds** for faster interactions.
* **`whisper_threads`**: Number of CPU threads Whisper uses for transcription.

---

## Running the Project

Before starting the assistant, make sure Ollama is available and the Python virtual environment is activated.

### Terminal 1 — Start Ollama

```bash
ollama serve
```

> **Note:** On many systems, Ollama starts automatically as a background service. If that's the case, you can skip this step.

---

### Terminal 2 — Launch the Assistant

```bash
# Activate the virtual environment
source /path/to/your/project/venv/bin/activate

# Navigate to the assistant directory
cd /path/to/your/project/assistant_lite

# Start the assistant
python simple_agent.py
```

The program will prompt you to press **ENTER**.

Once pressed:

1. The microphone records audio for the configured duration (`record_seconds`).
2. Whisper transcribes the speech into text.
3. Ollama generates a response.
4. Piper synthesizes the response using your custom `.onnx` voice model.
5. The assistant plays the generated audio back to you.

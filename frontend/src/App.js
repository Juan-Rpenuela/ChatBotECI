import React, { useState, useRef } from "react";

function App() {
  const [recording, setRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [videoSrc, setVideoSrc] = useState("/response.mp4");
  const [isAnimating, setIsAnimating] = useState(true);
  const [isListening, setIsListening] = useState(false);
  const [status, setStatus] = useState("");
  const [transcript, setTranscript] = useState("");
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        await sendAudioToBackend(audioBlob);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setRecording(true);
    } catch (error) {
      console.error("Error al iniciar la grabación:", error);
      alert("Error al acceder al micrófono");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && recording) {
      mediaRecorderRef.current.stop();
      setRecording(false);
    }
  };

  const sendAudioToBackend = async (audioBlob) => {
    try {
      setIsProcessing(true);
      const formData = new FormData();
      formData.append('audio', audioBlob, 'audio.wav');

      const response = await fetch('http://localhost:5000/audio', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error('Error en la respuesta del servidor');
      }

      const data = await response.json();
      console.log('Respuesta del backend:', data);
      
      if (data.result === "ok") {
        if (data.char_file) {
          const timestamp = new Date().getTime();
          setVideoSrc(`${data.char_file}?t=${timestamp}`);
        }
      } else {
        alert('Error: ' + (data.text || 'Error desconocido'));
      }
      
    } catch (error) {
      console.error('Error:', error);
      alert('Error al procesar el audio');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleMicClick = () => {
    if (recording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

    return (
    <div style={{
      minHeight: "100vh",
      background: "#222",
      display: "flex",
      justifyContent: "center",
      alignItems: "center"
    }}>
      <style>
        {`
          @keyframes expandVideo {
            0% {
              transform: scale(0);
              opacity: 0;
            }
            100% {
              transform: scale(1);
              opacity: 1;
            }
          }
          @keyframes pulse {
            0% { opacity: 0.5; }
            50% { opacity: 1; }
            100% { opacity: 0.5; }
          }
        `}
      </style>
      <div style={{
        background: "#222",
        borderRadius: "24px",
        boxShadow: "0 4px 32px rgba(0,0,0,0.5)",
        padding: "32px",
        display: "flex",
        flexDirection: "column",
        alignItems: "center"
      }}>
        <video
          key={videoSrc}
          src={videoSrc}
          autoPlay
          style={{
            width: "950px",
            height: "950px",
            borderRadius: "24px",
            objectFit: "cover",
            background: "#fff",
            animation: isAnimating ? "expandVideo 1s ease-out forwards" : "none",
            transformOrigin: "center",
            filter: "brightness(1.2) contrast(1.2)",
            position: "relative",
            overflow: "hidden"
          }}
        />
        <div style={{
          position: "absolute",
          top: "50%",
          left: "50%",
          transform: "translate(-50%, -50%)",
          width: "750px",
          height: "750px",
          pointerEvents: "none",
          zIndex: 1
        }} />
        <div style={{
          marginTop: "24px",
          color: "#fff",
          fontSize: "16px",
          textAlign: "center",
          animation: isListening ? "pulse 2s infinite" : "none"
        }}>
          {status}
        </div>
        <div style={{
          marginTop: "8px",
          color: "#666",
          fontSize: "14px",
          textAlign: "center",
          minHeight: "20px",
          maxWidth: "750px",
          wordWrap: "break-word"
        }}>
          {transcript}
        </div>
        <button
          onClick={handleMicClick}
          disabled={isProcessing}
          style={{
            marginTop: "24px",
            width: "64px",
            height: "64px",
            borderRadius: "50%",
            background: recording ? "#e74c3c" : "#fff",
            border: "none",
            boxShadow: "0 2px 8px rgba(0,0,0,0.2)",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            cursor: isProcessing ? "not-allowed" : "pointer",
            fontSize: "32px",
            transition: "background 0.2s",
            opacity: isProcessing ? 0.7 : 1
          }}
        >
          <span role="img" aria-label="mic">
            🎤
          </span>
        </button>
        {isProcessing && (
          <div style={{
            marginTop: "8px",
            color: "#fff",
            fontSize: "14px"
          }}>
            Procesando...
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
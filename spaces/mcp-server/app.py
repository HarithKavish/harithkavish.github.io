"""
MCP Server - Speech-to-Text (STT) and Text-to-Speech (TTS)
Combines both STT and TTS MCP servers in a single space
"""
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import torch
import io
import base64
import numpy as np

# Lightweight models for CPU inference
from transformers import pipeline
import soundfile as sf

app = FastAPI(
    title="MCP Server - STT & TTS",
    description="Model Context Protocol Server for Speech-to-Text and Text-to-Speech",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global models
stt_pipeline = None
tts_pipeline = None

# Request/Response Models
class STTRequest(BaseModel):
    audio_base64: str  # Base64 encoded audio

class STTResponse(BaseModel):
    text: str
    confidence: Optional[float] = None

class TTSRequest(BaseModel):
    text: str
    voice: Optional[str] = "default"

class TTSResponse(BaseModel):
    audio_base64: str
    sample_rate: int

@app.on_event("startup")
async def startup_event():
    """Initialize STT and TTS models."""
    global stt_pipeline, tts_pipeline
    
    print("🚀 Loading MCP Server models...")
    
    # STT: Whisper Tiny - Very lightweight (39M params), good for CPU
    print("   📝 Loading STT (Whisper Tiny)...")
    try:
        stt_pipeline = pipeline(
            "automatic-speech-recognition",
            model="openai/whisper-tiny",
            device=-1  # CPU
        )
        print("   ✓ STT model loaded")
    except Exception as e:
        print(f"   ✗ STT load failed: {e}")
        stt_pipeline = None
    
    # TTS: Using ESPnet or lightweight TTS
    # For CPU, we'll use a simple TTS approach
    print("   🔊 Loading TTS (ESPnet)...")
    try:
        # Using a lightweight TTS model
        from espnet2.bin.tts_inference import Text2Speech
        tts_pipeline = Text2Speech.from_pretrained(
            "espnet/kan-bayashi_ljspeech_vits",
            device="cpu"
        )
        print("   ✓ TTS model loaded")
    except Exception as e:
        print(f"   ⚠️  ESPnet TTS failed, using fallback: {e}")
        # Fallback: Use basic TTS
        try:
            from TTS.api import TTS
            tts_pipeline = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False)
            print("   ✓ TTS fallback loaded")
        except Exception as e2:
            print(f"   ✗ TTS load failed: {e2}")
            tts_pipeline = None
    
    print("✓ MCP Server ready!")

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "service": "MCP Server - STT & TTS",
        "status": "running",
        "stt_available": stt_pipeline is not None,
        "tts_available": tts_pipeline is not None,
        "endpoints": {
            "stt": "/stt (POST)",
            "tts": "/tts (POST)"
        }
    }

@app.post("/stt", response_model=STTResponse)
async def speech_to_text(request: STTRequest):
    """Convert speech to text using Whisper Tiny."""
    if not stt_pipeline:
        raise HTTPException(status_code=503, detail="STT model not loaded")
    
    try:
        # Decode base64 audio
        audio_bytes = base64.b64decode(request.audio_base64)
        
        # Load audio data
        audio_data, sample_rate = sf.read(io.BytesIO(audio_bytes))
        
        # Convert to mono if stereo
        if len(audio_data.shape) > 1:
            audio_data = audio_data.mean(axis=1)
        
        # Run STT
        result = stt_pipeline(audio_data, return_timestamps=False)
        
        text = result["text"].strip()
        
        return STTResponse(
            text=text,
            confidence=None  # Whisper doesn't provide confidence scores easily
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"STT failed: {str(e)}")

@app.post("/tts", response_model=TTSResponse)
async def text_to_speech(request: TTSRequest):
    """Convert text to speech."""
    if not tts_pipeline:
        raise HTTPException(status_code=503, detail="TTS model not loaded")
    
    try:
        # Generate speech
        if hasattr(tts_pipeline, '__call__'):  # ESPnet
            speech = tts_pipeline(request.text)["wav"]
            sample_rate = 22050
        else:  # TTS library
            wav = tts_pipeline.tts(request.text)
            speech = np.array(wav)
            sample_rate = 22050
        
        # Convert to bytes
        buffer = io.BytesIO()
        sf.write(buffer, speech, sample_rate, format='WAV')
        audio_bytes = buffer.getvalue()
        
        # Encode to base64
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        
        return TTSResponse(
            audio_base64=audio_base64,
            sample_rate=sample_rate
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS failed: {str(e)}")

@app.get("/health")
async def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "models": {
            "stt": {
                "loaded": stt_pipeline is not None,
                "model": "openai/whisper-tiny"
            },
            "tts": {
                "loaded": tts_pipeline is not None,
                "model": "espnet/kan-bayashi_ljspeech_vits"
            }
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)

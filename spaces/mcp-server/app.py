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
    
    # TTS: Using lightweight local TTS model (no internet needed)
    print("   🔊 Loading TTS (SpeechT5)...")
    try:
        from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
        from datasets import load_dataset
        
        # Load lightweight TTS models
        processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
        model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts")
        vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan")
        
        # Load speaker embeddings
        embeddings_dataset = load_dataset("Matthijs/cmu-arctic-xvectors", split="validation")
        speaker_embeddings = torch.tensor(embeddings_dataset[7306]["xvector"]).unsqueeze(0)
        
        tts_pipeline = {
            "processor": processor,
            "model": model,
            "vocoder": vocoder,
            "speaker_embeddings": speaker_embeddings
        }
        print("   ✓ TTS (SpeechT5) ready")
    except Exception as e:
        print(f"   ✗ TTS load failed: {e}")
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
    
    import tempfile
    import os
    
    try:
        # Decode base64 audio
        audio_bytes = base64.b64decode(request.audio_base64)
        
        # Save to temporary file (librosa needs a file path)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_path = tmp_file.name
        
        try:
            # Load audio with librosa (handles WebM and other formats)
            import librosa
            audio_data, sample_rate = librosa.load(tmp_path, sr=16000, mono=True)
            
            # Run STT
            result = stt_pipeline(audio_data, return_timestamps=False)
            
            text = result["text"].strip()
            
            return STTResponse(
                text=text,
                confidence=None
            )
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"STT processing failed: {str(e)}")

@app.post("/tts", response_model=TTSResponse)
async def text_to_speech(request: TTSRequest):
    """Convert text to speech using SpeechT5."""
    if not tts_pipeline:
        raise HTTPException(status_code=503, detail="TTS model not loaded")
    
    import traceback
    
    try:
        print(f"🔊 TTS request for text: {request.text[:50]}...")
        
        # Prepare text input
        processor = tts_pipeline["processor"]
        model = tts_pipeline["model"]
        vocoder = tts_pipeline["vocoder"]
        speaker_embeddings = tts_pipeline["speaker_embeddings"]
        
        # Process text
        inputs = processor(text=request.text, return_tensors="pt")
        
        # Generate speech
        with torch.no_grad():
            speech = model.generate_speech(inputs["input_ids"], speaker_embeddings, vocoder=vocoder)
        
        # Convert to numpy
        speech_np = speech.cpu().numpy()
        
        # Save to WAV buffer
        buffer = io.BytesIO()
        sf.write(buffer, speech_np, 16000, format='WAV')
        buffer.seek(0)
        audio_bytes = buffer.getvalue()
        
        print(f"✓ TTS generated {len(audio_bytes)} bytes")
        
        # Encode to base64
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        
        return TTSResponse(
            audio_base64=audio_base64,
            sample_rate=16000
        )
        
    except Exception as e:
        print(f"❌ TTS error: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
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
                "model": "microsoft/speecht5_tts (local, offline)"
            }
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)

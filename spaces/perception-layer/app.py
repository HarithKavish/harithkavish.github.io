"""
Perception Layer - Embeddings & Natural Language Understanding
HuggingFace Space: harithkavish/perception-layer
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from sentence_transformers import SentenceTransformer
from transformers import pipeline
import torch

app = FastAPI(
    title="Perception Layer",
    description="Natural Language Understanding and Embedding Generation",
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

# Model Configuration - Specialized for NLU tasks
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")  # Fast, 384-dim embeddings
INTENT_MODEL = os.getenv("INTENT_MODEL", "facebook/bart-large-mnli")  # Zero-shot classification specialist

# Global models
embedder: Optional[SentenceTransformer] = None
intent_classifier = None

# Request/Response Models
class EmbedRequest(BaseModel):
    text: str

class EmbedResponse(BaseModel):
    embedding: List[float]
    dimensions: int

class ClassifyRequest(BaseModel):
    text: str

class ClassifyResponse(BaseModel):
    intent: str
    confidence: float
    details: dict

class BatchEmbedRequest(BaseModel):
    texts: List[str]

class BatchEmbedResponse(BaseModel):
    embeddings: List[List[float]]
    dimensions: int
    count: int


@app.on_event("startup")
async def startup_event():
    """Initialize models."""
    global embedder, intent_classifier
    
    print("🚀 Loading Perception Layer models...")
    print("   📊 Specialized for: Embeddings + Intent Classification")
    
    # Load embedding model - Optimized for semantic similarity
    try:
        embedder = SentenceTransformer(EMBEDDING_MODEL)
        print(f"✓ Embedding model loaded: {EMBEDDING_MODEL}")
        print(f"   • Purpose: Generate 384-dim semantic embeddings")
        print(f"   • Optimized for: Fast inference, high-quality semantic search")
    except Exception as e:
        print(f"✗ Failed to load embedding model: {e}")
        embedder = None
    
    # Load intent classifier - Specialized for zero-shot classification
    try:
        intent_classifier = pipeline(
            "zero-shot-classification",
            model=INTENT_MODEL,
            device=0 if torch.cuda.is_available() else -1
        )
        print(f"✓ Intent classifier loaded: {INTENT_MODEL}")
        print(f"   • Purpose: Classify user intent without training data")
        print(f"   • Optimized for: Multi-label classification, high accuracy")
    except Exception as e:
        print(f"✗ Failed to load intent classifier: {e}")
        intent_classifier = None
    
    print("✓ Perception Layer ready!")


@app.post("/embed", response_model=EmbedResponse)
async def embed_text(request: EmbedRequest):
    """Generate embedding for a single text."""
    if not embedder:
        raise HTTPException(status_code=503, detail="Embedding model not loaded")
    
    try:
        embedding = embedder.encode(request.text, normalize_embeddings=True)
        return EmbedResponse(
            embedding=embedding.tolist(),
            dimensions=len(embedding)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding failed: {str(e)}")


@app.post("/embed/batch", response_model=BatchEmbedResponse)
async def embed_texts_batch(request: BatchEmbedRequest):
    """Generate embeddings for multiple texts (batch processing)."""
    if not embedder:
        raise HTTPException(status_code=503, detail="Embedding model not loaded")
    
    try:
        embeddings = embedder.encode(
            request.texts,
            normalize_embeddings=True,
            batch_size=32,
            show_progress_bar=False
        )
        
        return BatchEmbedResponse(
            embeddings=[emb.tolist() for emb in embeddings],
            dimensions=len(embeddings[0]) if len(embeddings) > 0 else 0,
            count=len(embeddings)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch embedding failed: {str(e)}")


@app.post("/classify", response_model=ClassifyResponse)
async def classify_intent(request: ClassifyRequest):
    """Classify user intent using zero-shot classification."""
    if not intent_classifier:
        raise HTTPException(status_code=503, detail="Intent classifier not loaded")
    
    # Define candidate intents
    candidate_labels = [
        "QUESTION_ABOUT_PROJECTS",
        "QUESTION_ABOUT_SKILLS",
        "QUESTION_ABOUT_EXPERIENCE",
        "QUESTION_ABOUT_CONTACT",
        "GREETING",
        "FAREWELL",
        "GENERAL_CONVERSATION",
        "REQUEST_FOR_HELP"
    ]
    
    try:
        result = intent_classifier(
            request.text,
            candidate_labels,
            multi_label=False
        )
        
        return ClassifyResponse(
            intent=result['labels'][0],
            confidence=float(result['scores'][0]),
            details={
                "all_intents": result['labels'],
                "all_scores": [float(s) for s in result['scores']]
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy" if (embedder and intent_classifier) else "degraded",
        "embedding_model": "loaded" if embedder else "not_loaded",
        "intent_classifier": "loaded" if intent_classifier else "not_loaded",
        "service": "perception-layer",
        "version": "1.0.0"
    }


@app.get("/")
async def root():
    """Root endpoint with service info."""
    return {
        "service": "Perception Layer",
        "description": "Natural Language Understanding and Embedding Generation",
        "version": "1.0.0",
        "endpoints": {
            "POST /embed": "Generate single text embedding",
            "POST /embed/batch": "Generate batch embeddings",
            "POST /classify": "Classify user intent",
            "GET /health": "Health check"
        },
        "status": "operational"
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)

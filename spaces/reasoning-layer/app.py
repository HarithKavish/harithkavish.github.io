"""
Reasoning & Planning Layer - LLM-Powered Response Generation
HuggingFace Space: harithkavish/reasoning-layer
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import os
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import torch

app = FastAPI(
    title="Reasoning & Planning Layer",
    description="Strategic reasoning and response generation using FLAN-T5",
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

# Configuration
MODEL_NAME = os.getenv("MODEL_NAME", "google/flan-t5-large")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "250"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))

# Global model
text_generator = None
tokenizer = None


# Request/Response Models
class GenerateRequest(BaseModel):
    query: str
    context: List[Dict]
    intent: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None

class GenerateResponse(BaseModel):
    response: str
    confidence: float
    tokens_used: int
    model: str

class AnalyzeRequest(BaseModel):
    query: str

class AnalyzeResponse(BaseModel):
    complexity: str  # SIMPLE, MODERATE, COMPLEX
    requires_context: bool
    suggested_strategy: str
    estimated_response_type: str


@app.on_event("startup")
async def startup_event():
    """Initialize LLM model."""
    global text_generator, tokenizer
    
    print("🚀 Loading Reasoning Layer models...")
    print(f"   Model: {MODEL_NAME}")
    
    try:
        # Load model and tokenizer
        print("   Loading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        
        print("   Loading model...")
        model = AutoModelForSeq2SeqLM.from_pretrained(
            MODEL_NAME,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto" if torch.cuda.is_available() else None
        )
        
        # Create pipeline
        text_generator = pipeline(
            "text2text-generation",
            model=model,
            tokenizer=tokenizer,
            device=0 if torch.cuda.is_available() else -1
        )
        
        print("✓ FLAN-T5 model loaded successfully")
        print(f"   Using device: {'CUDA' if torch.cuda.is_available() else 'CPU'}")
        
    except Exception as e:
        print(f"✗ Failed to load model: {e}")
        text_generator = None
        tokenizer = None
    
    print("✓ Reasoning Layer ready!")


def build_prompt(query: str, context: List[Dict], intent: Optional[str] = None) -> str:
    """Build optimized prompt for FLAN-T5."""
    
    # Build context section
    context_parts = []
    for doc in context[:4]:  # Top 4 most relevant
        content = doc.get('content', '')
        metadata = doc.get('metadata', {})
        name = metadata.get('name', 'Unknown')
        
        if content:
            context_parts.append(f"{name}: {content}")
        elif metadata.get('description'):
            context_parts.append(f"{name}: {metadata['description']}")
    
    context_text = "\n\n".join(context_parts) if context_parts else "No specific context available."
    
    # Adjust prompt based on intent
    if intent == "GREETING":
        prompt = f"""You are a friendly AI assistant. Respond warmly to the greeting: "{query}"

Keep your response brief and welcoming."""
    
    elif intent == "FAREWELL":
        prompt = f"""You are a friendly AI assistant. Respond appropriately to the farewell: "{query}"

Keep your response brief and positive."""
    
    else:
        # Standard RAG prompt
        prompt = f"""You are an intelligent AI assistant with access to a knowledge base. Use the information below to answer the user's question accurately and completely.

RULES:
1. Use ONLY information from the knowledge base
2. Provide complete, detailed answers - never truncate lists
3. Be specific with names, numbers, and technical details
4. If the knowledge base doesn't have the answer, say so clearly
5. Speak naturally and conversationally

KNOWLEDGE BASE:
{context_text}

USER QUESTION: {query}

Provide a complete, detailed response:"""
    
    return prompt


@app.post("/generate", response_model=GenerateResponse)
async def generate_response(request: GenerateRequest):
    """Generate response using FLAN-T5."""
    if not text_generator:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Build prompt
        prompt = build_prompt(request.query, request.context, request.intent)
        
        # Generation parameters
        max_tokens = request.max_tokens or MAX_TOKENS
        temperature = request.temperature or TEMPERATURE
        
        # Generate response
        result = text_generator(
            prompt,
            max_new_tokens=max_tokens,
            min_length=15,
            num_return_sequences=1,
            temperature=temperature,
            do_sample=True,
            repetition_penalty=1.1,
            no_repeat_ngram_size=3,
            top_p=0.92,
            length_penalty=1.0
        )
        
        generated_text = result[0]['generated_text']
        
        # Extract answer (remove prompt if present)
        if prompt in generated_text:
            answer = generated_text.replace(prompt, "").strip()
        else:
            answer = generated_text.strip()
        
        # Calculate token usage
        tokens_used = len(tokenizer.encode(prompt + answer))
        
        # Estimate confidence based on answer quality
        confidence = 0.9 if len(answer) > 20 and len(answer) < 800 else 0.5
        
        return GenerateResponse(
            response=answer,
            confidence=confidence,
            tokens_used=tokens_used,
            model=MODEL_NAME
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_query(request: AnalyzeRequest):
    """Analyze query complexity and suggest strategy."""
    
    query_lower = request.query.lower()
    query_length = len(request.query.split())
    
    # Determine complexity
    if query_length <= 5:
        complexity = "SIMPLE"
    elif query_length <= 15:
        complexity = "MODERATE"
    else:
        complexity = "COMPLEX"
    
    # Check if context is needed
    question_words = ['what', 'who', 'where', 'when', 'why', 'how', 'which']
    requires_context = any(word in query_lower for word in question_words)
    
    # Suggest strategy
    if any(greeting in query_lower for greeting in ['hi', 'hello', 'hey']):
        strategy = "DIRECT_RESPONSE"
        response_type = "GREETING"
    elif any(farewell in query_lower for farewell in ['bye', 'goodbye', 'see you']):
        strategy = "DIRECT_RESPONSE"
        response_type = "FAREWELL"
    elif requires_context:
        strategy = "RAG_WITH_CONTEXT"
        response_type = "INFORMATIVE"
    else:
        strategy = "CONVERSATIONAL"
        response_type = "CONVERSATIONAL"
    
    return AnalyzeResponse(
        complexity=complexity,
        requires_context=requires_context,
        suggested_strategy=strategy,
        estimated_response_type=response_type
    )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy" if text_generator else "degraded",
        "model": MODEL_NAME,
        "model_loaded": text_generator is not None,
        "device": "cuda" if torch.cuda.is_available() else "cpu",
        "service": "reasoning-layer",
        "version": "1.0.0"
    }


@app.get("/")
async def root():
    """Root endpoint with service info."""
    return {
        "service": "Reasoning & Planning Layer",
        "description": "Strategic reasoning and response generation using FLAN-T5",
        "version": "1.0.0",
        "model": MODEL_NAME,
        "endpoints": {
            "POST /generate": "Generate response with context",
            "POST /analyze": "Analyze query complexity",
            "GET /health": "Health check"
        },
        "status": "operational"
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)

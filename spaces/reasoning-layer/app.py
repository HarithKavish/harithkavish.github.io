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

# Model Configuration - Optimized for CPU inference on free tier
# Using FLAN-T5-Large with reduced token limits for faster inference
MODEL_NAME = os.getenv("MODEL_NAME", "google/flan-t5-large")  # 780M params - balanced speed/quality
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "256"))  # Reduced from 350 for faster generation
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.8"))  # Slightly higher for more natural language

# System prompt for this layer's purpose - Keep it simple for FLAN-T5
SYSTEM_IDENTITY = """Neo AI: Harith Kavish's intelligent portfolio assistant. Multi-agent RAG system."""

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
    print(f"   📝 Specialized for: Strategic Reasoning & Response Generation")
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
        print(f"   • Purpose: Generate coherent, contextual responses")
        print(f"   • Optimized for: Instruction-following, reasoning over context")
        print(f"   • Using device: {'CUDA' if torch.cuda.is_available() else 'CPU'}")
        print(f"   • System Identity: {SYSTEM_IDENTITY[:100]}...")
        
    except Exception as e:
        print(f"✗ Failed to load model: {e}")
        text_generator = None
        tokenizer = None
    
    print("✓ Reasoning Layer ready!")


def build_prompt(query: str, context: List[Dict], intent: Optional[str] = None) -> str:
    """
    Build RAG-focused prompt for FLAN-T5 - extremely simple format.
    FLAN-T5 works best with direct question-answer tasks.
    """
    
    # Build context section - clean and simple
    context_parts = []
    for doc in context[:5]:  # Top 5 most relevant
        content = doc.get('content', '')
        if content:
            context_parts.append(content.strip())
        elif doc.get('metadata', {}).get('description'):
            context_parts.append(doc['metadata']['description'].strip())
    
    context_text = " ".join(context_parts) if context_parts else ""
    
    # Handle empty context
    if not context_text:
        return f"""Question: {query}
Answer: I don't have specific information about that in my knowledge base. I'm Neo AI, Harith Kavish's portfolio assistant. I can answer questions about his projects, skills, and experience."""
    
    # Adjust prompt based on query type - Use simple QA format
    query_lower = query.lower().strip()
    
    if "who are you" in query_lower or "what are you" in query_lower or "neo ai" in query_lower:
        # Questions about the assistant
        prompt = f"""Context: {context_text}

Question: {query}
Answer: I am Neo AI, Harith Kavish's intelligent portfolio assistant. I'm powered by a multi-agent RAG system and can answer questions about his work, skills, and projects."""
    
    elif query_lower in ["hi", "hello", "hey", "greetings", "good morning", "good afternoon", "good evening"]:
        # Simple greetings
        prompt = f"""Question: {query}
Answer: Hello! I'm Neo AI, Harith Kavish's assistant. How can I help you learn about his projects and experience?"""
    
    elif "projects" in query_lower:
        # Project-focused queries
        prompt = f"""Context about Harith Kavish's projects: {context_text}

Question: {query}
Answer in complete sentences listing all his projects with their names and technologies:"""
    
    elif "who is harith" in query_lower or "tell me about harith" in query_lower:
        # Biography queries
        prompt = f"""Context about Harith Kavish: {context_text}

Question: {query}
Answer in complete sentences describing who he is, his role, and expertise:"""
    
    else:
        # Standard RAG query - simplest possible format
        prompt = f"""Context: {context_text}

Question: {query}
Answer:"""
    
    return prompt
    
    return prompt


@app.post("/generate", response_model=GenerateResponse)
async def generate_response(request: GenerateRequest):
    """Generate response using FLAN-T5."""
    if not text_generator:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Build prompt
        prompt = build_prompt(request.query, request.context, request.intent)
        
        # Generation parameters - optimized for speed on CPU
        max_tokens = request.max_tokens or MAX_TOKENS
        temperature = request.temperature or TEMPERATURE
        
        # Generate response with CPU-optimized parameters
        result = text_generator(
            prompt,
            max_new_tokens=max_tokens,
            min_length=20,  # Ensure meaningful responses
            num_return_sequences=1,
            temperature=temperature,
            do_sample=True,
            repetition_penalty=1.15,  # Lighter penalty for faster inference
            no_repeat_ngram_size=3,
            top_p=0.9,  # Reduced for faster sampling
            top_k=40,  # Reduced for faster sampling
            length_penalty=1.1,  # Lighter penalty
            early_stopping=True  # Enable early stopping for speed
        )
        
        generated_text = result[0]['generated_text']
        
        # Extract answer - remove prompt if model echoed it back
        answer = generated_text
        if "Answer:" in answer:
            answer = answer.split("Answer:")[-1].strip()
        if "Question:" in answer:
            # Remove everything before the answer
            parts = answer.split("Answer:")
            if len(parts) > 1:
                answer = parts[-1].strip()
            else:
                # If no "Answer:" but has "Question:", remove question part
                answer = answer.split("Question:")[-1].strip()
        
        # Clean up any instruction fragments that leaked through
        instruction_phrases = [
            "Context:",
            "Important guidelines:",
            "Speak about Harith in third person",
            "Include ALL relevant details",
            "List specific project names",
            "Be complete and thorough",
            "Only use information provided",
            "- ",  # Remove bullet points that are instruction remnants
            "Keep it brief",
            "Provide a brief"
        ]
        
        for phrase in instruction_phrases:
            if phrase in answer and len(answer) < 200:  # Only clean short responses
                # This might be an instruction fragment, not a real answer
                parts = answer.split(phrase)
                if len(parts[0]) > 20:  # Keep the part before the instruction if it's substantial
                    answer = parts[0].strip()
        
        # Post-processing: Clean up response
        answer = answer.strip()
        
        # Remove incomplete sentences at the end
        if answer and answer[-1] not in '.!?':
            # Find last complete sentence
            last_period = max(answer.rfind('.'), answer.rfind('!'), answer.rfind('?'))
            if last_period > len(answer) // 2:  # Only if it's at least halfway through
                answer = answer[:last_period + 1]
        
        # Fallback for very short or empty responses
        if len(answer) < 10:
            answer = "I apologize, but I couldn't generate a complete response. Could you please rephrase your question?"
            confidence = 0.3
        else:
            # Calculate confidence based on answer quality metrics
            has_good_length = 30 < len(answer) < 1000
            has_complete_sentence = answer[-1] in '.!?'
            has_no_truncation = "including:" not in answer.lower() and answer.count(',') < len(answer) / 20
            
            quality_score = sum([has_good_length, has_complete_sentence, has_no_truncation]) / 3
            confidence = 0.6 + (quality_score * 0.3)  # 0.6 to 0.9 range
        
        # Calculate token usage
        tokens_used = len(tokenizer.encode(prompt + answer))
        
        return GenerateResponse(
            response=answer,
            confidence=round(confidence, 3),
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

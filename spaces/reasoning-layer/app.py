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

# Model Configuration - Balanced for speed and quality
# Using FLAN-T5-Large for faster inference on free tier while maintaining quality
MODEL_NAME = os.getenv("MODEL_NAME", "google/flan-t5-large")  # 780M params - balanced speed/quality
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "350"))  # Increased for complete answers
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.8"))  # Slightly higher for more natural language

# System prompt for this layer's purpose
SYSTEM_IDENTITY = """You are Neo AI, Harith Kavish's intelligent portfolio assistant.

CRITICAL RULES:
1. ALWAYS speak ABOUT Harith in third person (he/his), NEVER as him (I/my)
2. Use ONLY information from the provided knowledge base
3. Give COMPLETE, DETAILED answers - never truncate lists or say "including:"
4. Be SPECIFIC: mention project names, technologies, skills by name
5. If asked about yourself (Neo AI), explain you're his assistant
6. If information is missing, say "I don't have that information" - DO NOT make things up

RESPONSE STYLE:
- Professional but conversational
- Detailed and informative
- Always complete your sentences and lists
- Focus on Harith's accomplishments and expertise"""

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
    Build optimized prompt for FLAN-T5-XL with specialized system instructions.
    This layer's responsibility: Synthesize context into coherent, complete, third-person responses.
    """
    
    # Build context section with more detail
    context_parts = []
    for idx, doc in enumerate(context[:5], 1):  # Top 5 most relevant
        content = doc.get('content', '')
        metadata = doc.get('metadata', {})
        name = metadata.get('name', 'Unknown')
        doc_type = metadata.get('@type', 'Information')
        
        if content:
            context_parts.append(f"[{idx}] {name} ({doc_type}):\n{content}")
        elif metadata.get('description'):
            context_parts.append(f"[{idx}] {name} ({doc_type}):\n{metadata['description']}")
    
    context_text = "\n\n".join(context_parts) if context_parts else ""
    
    # Handle empty context
    if not context_text:
        return f"""{SYSTEM_IDENTITY}

The knowledge base search returned no relevant information for this query.

USER QUESTION: {query}

Provide a brief, honest response explaining that you don't have specific information about this topic in your knowledge base, and suggest what kinds of questions you CAN answer about Harith Kavish (projects, skills, experience, etc.).

Response:"""
    
    # Adjust prompt based on intent - Each intent gets specialized instructions
    if intent == "GREETING":
        # Specialized prompt for greetings - warm but professional
        prompt = f"""{SYSTEM_IDENTITY}

Task: Respond warmly and professionally to this greeting: "{query}"

Instructions:
- Be brief (2-3 sentences maximum)
- Introduce yourself as Neo AI, Harith Kavish's portfolio assistant
- Offer to help with questions about his projects, skills, and experience
- Sound enthusiastic and helpful

Response:"""
    
    elif intent == "FAREWELL":
        # Specialized prompt for farewells - positive closure
        prompt = f"""{SYSTEM_IDENTITY}

Task: Respond appropriately to this farewell: "{query}"

Instructions:
- Be brief (1-2 sentences)
- Thank them for their interest in Harith's work
- Leave a positive, professional impression

Response:"""
    
    elif "who are you" in query.lower() or "what are you" in query.lower() or "neo ai" in query.lower():
        # Special handling for questions about the assistant itself
        prompt = f"""{SYSTEM_IDENTITY}

Task: Explain who YOU are (Neo AI) based on this query: "{query}"

KNOWLEDGE BASE ABOUT NEO AI AND HARITH:
{context_text}

Instructions:
- Explain you are Neo AI, Harith Kavish's intelligent portfolio assistant
- Describe your capabilities (answering questions about his work)
- Mention your architecture (multi-agent RAG system with specialized layers)
- Keep it conversational but informative (3-4 sentences)

Response:"""
    
    else:
        # Standard RAG prompt - Specialized for information synthesis
        prompt = f"""{SYSTEM_IDENTITY}

KNOWLEDGE BASE ABOUT HARITH KAVISH:
{context_text}

USER QUESTION: {query}

SYNTHESIS INSTRUCTIONS:
1. Analyze the knowledge base entries above
2. Extract ALL relevant information that answers the question
3. Speak ABOUT Harith in third person (he/his)
4. Be COMPLETE - list ALL items mentioned, don't use "including:" or truncate
5. Include specific details: project names, technologies, dates, numbers
6. Organize information clearly (use bullet points if listing multiple items)
7. If the question asks about multiple things, address each one
8. Never make up information not in the knowledge base

Comprehensive answer about Harith Kavish:"""
    
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
        
        # Generate response with improved parameters
        result = text_generator(
            prompt,
            max_new_tokens=max_tokens,
            min_length=20,  # Ensure meaningful responses
            num_return_sequences=1,
            temperature=temperature,
            do_sample=True,
            repetition_penalty=1.2,  # Stronger penalty against repetition
            no_repeat_ngram_size=3,
            top_p=0.95,  # Higher for more diverse vocabulary
            top_k=50,
            length_penalty=1.2,  # Encourage longer, complete responses
            early_stopping=False  # Let it finish thoughts
        )
        
        generated_text = result[0]['generated_text']
        
        # Extract answer (remove prompt if present)
        if prompt in generated_text:
            answer = generated_text.replace(prompt, "").strip()
        else:
            answer = generated_text.strip()
        
        # Post-processing: Clean up response
        answer = answer.strip()
        
        # Remove incomplete sentences at the end
        if answer and not answer[-1] in '.!?':
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

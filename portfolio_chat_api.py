"""
Portfolio Chat API - Lightweight FastAPI server
Uses MongoDB Atlas + Ollama for AI-powered portfolio queries
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
import ollama
import os
from typing import List, Dict, Optional
import json
import asyncio
from dotenv import load_dotenv

# Load environment
load_dotenv()

app = FastAPI(title="Portfolio Chat API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
MONGO_URI = os.getenv("MONGODB_URI")
DB_NAME = "nlweb"
COLLECTION_NAME = "portfolio_vectors"
VECTOR_INDEX = "vector_index"

# Ollama models
LLM_MODEL = "gemma2:2b"
EMBEDDING_MODEL = "nomic-embed-text"

# Global MongoDB client
mongo_client: Optional[AsyncIOMotorClient] = None


class ChatQuery(BaseModel):
    """Chat query model."""
    query: str
    top_k: int = 5


class ChatResponse(BaseModel):
    """Chat response model."""
    query: str
    answer: str
    sources: List[Dict]


@app.on_event("startup")
async def startup_db_client():
    """Initialize MongoDB connection on startup."""
    global mongo_client
    mongo_client = AsyncIOMotorClient(MONGO_URI)
    print(f"✓ Connected to MongoDB: {DB_NAME}.{COLLECTION_NAME}")


@app.on_event("shutdown")
async def shutdown_db_client():
    """Close MongoDB connection on shutdown."""
    if mongo_client:
        mongo_client.close()
        print("✓ MongoDB connection closed")


async def get_embedding(text: str) -> List[float]:
    """Generate embedding using Ollama."""
    response = ollama.embeddings(model=EMBEDDING_MODEL, prompt=text)
    return response['embedding']


async def vector_search(query_embedding: List[float], top_k: int = 5) -> List[Dict]:
    """Search MongoDB Atlas with vector similarity."""
    collection = mongo_client[DB_NAME][COLLECTION_NAME]
    
    pipeline = [
        {
            "$vectorSearch": {
                "index": VECTOR_INDEX,
                "path": "embedding",
                "queryVector": query_embedding,
                "numCandidates": top_k * 10,
                "limit": top_k,
            }
        },
        {
            "$project": {
                "_id": 0,
                "text": 1,
                "name": 1,
                "@type": 1,
                "description": 1,
                "score": {"$meta": "vectorSearchScore"},
            }
        },
    ]
    
    results = []
    cursor = collection.aggregate(pipeline)
    async for doc in cursor:
        results.append(doc)
    
    return results


def generate_answer(query: str, context_docs: List[Dict]) -> str:
    """Generate answer using Ollama with context."""
    # Build context from search results
    context = "\n\n".join([
        f"[{doc.get('name', 'Unknown')}] ({doc.get('@type', 'N/A')})\n{doc.get('text', '')}"
        for doc in context_docs
    ])
    
    # Create prompt
    prompt = f"""Based on the following information about Harith Kavish's portfolio, answer the user's question.

CONTEXT:
{context}

USER QUESTION: {query}

Provide a helpful, informative answer based on the context above. If the context doesn't contain relevant information, say so politely. Keep the response concise and natural."""

    # Generate response
    response = ollama.generate(
        model=LLM_MODEL,
        prompt=prompt,
        options={
            "temperature": 0.7,
            "num_predict": 300,
        }
    )
    
    return response['response'].strip()


async def generate_answer_streaming(query: str, context_docs: List[Dict]):
    """Generate answer with streaming response."""
    # Build context
    context = "\n\n".join([
        f"[{doc.get('name', 'Unknown')}] ({doc.get('@type', 'N/A')})\n{doc.get('text', '')}"
        for doc in context_docs
    ])
    
    # Create prompt
    prompt = f"""Based on the following information about Harith Kavish's portfolio, answer the user's question.

CONTEXT:
{context}

USER QUESTION: {query}

Provide a helpful, informative answer based on the context above. If the context doesn't contain relevant information, say so politely. Keep the response concise and natural."""

    # Stream response
    stream = ollama.generate(
        model=LLM_MODEL,
        prompt=prompt,
        stream=True,
        options={
            "temperature": 0.7,
            "num_predict": 300,
        }
    )
    
    for chunk in stream:
        if chunk.get('response'):
            yield f"data: {json.dumps({'text': chunk['response']})}\n\n"
    
    yield "data: [DONE]\n\n"


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "online",
        "service": "Portfolio Chat API",
        "version": "1.0.0",
        "models": {
            "llm": LLM_MODEL,
            "embedding": EMBEDDING_MODEL,
        }
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(query: ChatQuery):
    """
    Process chat query and return answer with sources.
    """
    try:
        # Generate embedding
        query_embedding = await get_embedding(query.query)
        
        # Search similar documents
        results = await vector_search(query_embedding, query.top_k)
        
        if not results:
            return ChatResponse(
                query=query.query,
                answer="I couldn't find relevant information about that in the portfolio.",
                sources=[]
            )
        
        # Generate answer
        answer = generate_answer(query.query, results)
        
        # Format sources
        sources = [
            {
                "name": doc.get("name", "Unknown"),
                "type": doc.get("@type", ""),
                "score": round(doc.get("score", 0), 4),
                "preview": doc.get("text", "")[:200] + "..."
            }
            for doc in results
        ]
        
        return ChatResponse(
            query=query.query,
            answer=answer,
            sources=sources
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@app.post("/chat/stream")
async def chat_stream(query: ChatQuery):
    """
    Process chat query and return streaming answer.
    """
    try:
        # Generate embedding
        query_embedding = await get_embedding(query.query)
        
        # Search similar documents
        results = await vector_search(query_embedding, query.top_k)
        
        if not results:
            async def error_stream():
                error_msg = "I couldn't find relevant information about that in the portfolio."
                yield f"data: {json.dumps({'text': error_msg})}\n\n"
                yield "data: [DONE]\n\n"
            return StreamingResponse(error_stream(), media_type="text/event-stream")
        
        # Stream answer
        return StreamingResponse(
            generate_answer_streaming(query.query, results),
            media_type="text/event-stream"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@app.get("/health")
async def health():
    """Detailed health check."""
    try:
        # Test MongoDB connection
        await mongo_client.admin.command('ping')
        mongo_status = "connected"
    except:
        mongo_status = "disconnected"
    
    # Test Ollama
    try:
        ollama.list()
        ollama_status = "connected"
    except:
        ollama_status = "disconnected"
    
    return {
        "status": "healthy" if mongo_status == "connected" and ollama_status == "connected" else "degraded",
        "mongodb": mongo_status,
        "ollama": ollama_status,
        "database": f"{DB_NAME}.{COLLECTION_NAME}",
        "vector_index": VECTOR_INDEX
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 7860))  # Use Hugging Face Spaces port
    uvicorn.run(app, host="0.0.0.0", port=port)

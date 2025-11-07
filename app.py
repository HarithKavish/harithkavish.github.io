"""
Portfolio Chat API - Hugging Face Spaces version
Uses MongoDB Atlas + Hugging Face Transformers for AI-powered portfolio queries
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
import os
from typing import List, Dict, Optional
import json
import asyncio
from dotenv import load_dotenv
from transformers import pipeline
import torch

# Load environment
load_dotenv()

app = FastAPI(title="Portfolio Chat API - HF Spaces", version="1.0.0")

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

# Global MongoDB client and models
mongo_client: Optional[AsyncIOMotorClient] = None
text_generator = None
embedder = None


class ChatQuery(BaseModel):
    """Chat query model."""
    query: str
    top_k: int = 5


@app.on_event("startup")
async def startup_event():
    """Initialize MongoDB and models."""
    global mongo_client, text_generator, embedder
    
    # Connect to MongoDB
    if MONGO_URI:
        mongo_client = AsyncIOMotorClient(MONGO_URI)
        # Test connection
        try:
            await mongo_client.admin.command('ping')
            print("✓ Connected to MongoDB:", f"{DB_NAME}.{COLLECTION_NAME}")
        except Exception as e:
            print(f"✗ MongoDB connection failed: {e}")
            mongo_client = None
    
    # Initialize Hugging Face models
    try:
        # Use a smaller model that works well on CPU
        device = 0 if torch.cuda.is_available() else -1
        text_generator = pipeline(
            "text-generation",
            model="microsoft/DialoGPT-medium",
            device=device,
            max_length=512,
            do_sample=True,
            temperature=0.7
        )
        
        # For embeddings, we'll use sentence-transformers
        from sentence_transformers import SentenceTransformer
        embedder = SentenceTransformer('all-MiniLM-L6-v2')
        
        print("✓ Initialized Hugging Face models")
    except Exception as e:
        print(f"✗ Model initialization failed: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Close MongoDB connection."""
    global mongo_client
    if mongo_client:
        mongo_client.close()
        print("✓ MongoDB connection closed")


async def get_embedding(text: str) -> List[float]:
    """Generate embedding for text using Sentence Transformers."""
    global embedder
    if not embedder:
        raise HTTPException(status_code=503, detail="Embedding model not available")
    
    try:
        embedding = embedder.encode(text)
        return embedding.tolist()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding generation failed: {str(e)}")


async def vector_search(query_embedding: List[float], top_k: int = 5) -> List[Dict]:
    """Perform vector search in MongoDB."""
    if not mongo_client:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        collection = mongo_client[DB_NAME][COLLECTION_NAME]
        
        pipeline = [
            {
                "$vectorSearch": {
                    "index": VECTOR_INDEX,
                    "path": "embedding",
                    "queryVector": query_embedding,
                    "numCandidates": top_k * 2,
                    "limit": top_k
                }
            },
            {
                "$project": {
                    "content": 1,
                    "metadata": 1,
                    "score": {"$meta": "vectorSearchScore"}
                }
            }
        ]
        
        results = []
        async for doc in collection.aggregate(pipeline):
            results.append(doc)
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vector search failed: {str(e)}")


def generate_answer(query: str, context_docs: List[Dict]) -> str:
    """Generate answer using Hugging Face model."""
    global text_generator
    if not text_generator:
        return "I apologize, but the AI model is currently unavailable. Please try again later."
    
    # Build context from retrieved documents
    context_parts = []
    for doc in context_docs:
        content = doc.get('content', '')
        metadata = doc.get('metadata', {})
        score = doc.get('score', 0)
        
        # Only include relevant results (score > 0.7)
        if score > 0.7:
            context_parts.append(f"- {content}")
    
    context = "\n".join(context_parts[:3])  # Limit context length
    
    # Create a focused prompt
    prompt = f"""Based on Harith Kavish's portfolio information:
{context}

Question: {query}
Answer:"""
    
    try:
        # Generate response
        response = text_generator(
            prompt,
            max_length=len(prompt.split()) + 100,
            num_return_sequences=1,
            pad_token_id=text_generator.tokenizer.eos_token_id
        )
        
        generated_text = response[0]['generated_text']
        # Extract only the answer part
        answer = generated_text.split("Answer:")[-1].strip()
        
        if not answer or len(answer) < 10:
            # Fallback response
            return f"Based on the portfolio information, here's what I found: {context[:200]}..."
        
        return answer
        
    except Exception as e:
        print(f"Generation error: {e}")
        return f"Based on Harith Kavish's portfolio: {context[:300]}..."


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "Portfolio Chat API is running", "version": "1.0.0-hf"}


@app.post("/chat")
async def chat(query: ChatQuery):
    """Process chat query and return response."""
    try:
        # Generate embedding for query
        query_embedding = await get_embedding(query.query)
        
        # Search for relevant documents
        context_docs = await vector_search(query_embedding, query.top_k)
        
        # Generate answer
        answer = generate_answer(query.query, context_docs)
        
        # Prepare sources for response
        sources = []
        for doc in context_docs:
            metadata = doc.get('metadata', {})
            score = doc.get('score', 0)
            
            sources.append({
                "name": metadata.get('name', 'Unknown'),
                "type": metadata.get('@type', 'Content'),
                "score": round(score, 4)
            })
        
        return {
            "answer": answer,
            "sources": sources,
            "query": query.query
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Detailed health check."""
    # Check MongoDB
    try:
        if mongo_client:
            await mongo_client.admin.command('ping')
            mongo_status = "connected"
        else:
            mongo_status = "disconnected"
    except:
        mongo_status = "disconnected"
    
    # Check models
    model_status = "loaded" if text_generator and embedder else "not_loaded"
    
    return {
        "status": "healthy" if mongo_status == "connected" and model_status == "loaded" else "degraded",
        "mongodb": mongo_status,
        "models": model_status,
        "database": f"{DB_NAME}.{COLLECTION_NAME}",
        "vector_index": VECTOR_INDEX
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)
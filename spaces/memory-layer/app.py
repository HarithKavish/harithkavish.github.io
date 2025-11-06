"""
Memory Layer - Vector Database & Conversation History
HuggingFace Space: harithkavish/memory-layer
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Dict, Optional
import os
import asyncio
from datetime import datetime

app = FastAPI(
    title="Memory Layer",
    description="Vector Database and Conversation History Management",
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

# MongoDB configuration
MONGO_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME", "nlweb")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "portfolio_vectors")
VECTOR_INDEX = os.getenv("VECTOR_INDEX", "vector_index")  # Fixed to match actual index name
HISTORY_COLLECTION = os.getenv("HISTORY_COLLECTION", "conversation_history")

# System purpose for this layer
MEMORY_MISSION = """This layer manages vector storage and conversation history.
Specialized for: Vector similarity search, conversation persistence, context retrieval.
No AI model - pure database operations for fast, accurate retrieval."""

# Global MongoDB client
mongo_client: Optional[AsyncIOMotorClient] = None


# Request/Response Models
class VectorSearchRequest(BaseModel):
    embedding: List[float]
    top_k: int = 5
    filters: Optional[Dict] = None

class VectorSearchResponse(BaseModel):
    results: List[Dict]
    count: int
    query_time_ms: float

class StoreConversationRequest(BaseModel):
    session_id: str
    user_message: str
    bot_response: str
    metadata: Optional[Dict] = None

class StoreConversationResponse(BaseModel):
    status: str
    session_id: str
    message_id: str

class GetHistoryRequest(BaseModel):
    session_id: str
    limit: int = 10

class GetHistoryResponse(BaseModel):
    messages: List[Dict]
    session_id: str
    count: int


@app.on_event("startup")
async def startup_event():
    """Initialize MongoDB connection."""
    global mongo_client
    
    print("🚀 Initializing Memory Layer...")
    print("   🗄️ Specialized for: Vector Search & Conversation Storage")
    print(f"   Mission: {MEMORY_MISSION}")
    
    if not MONGO_URI:
        print("✗ No MONGODB_URI found in environment variables")
        mongo_client = None
        return
    
    try:
        print(f"🔌 Connecting to MongoDB Atlas...")
        mongo_client = AsyncIOMotorClient(
            MONGO_URI,
            serverSelectionTimeoutMS=30000,
            socketTimeoutMS=60000,
            connectTimeoutMS=30000,
            maxPoolSize=10,
            retryWrites=True
        )
        
        # Test connection
        await asyncio.wait_for(
            mongo_client.admin.command('ping'),
            timeout=30.0
        )
        
        print(f"✓ Connected to MongoDB Atlas")
        print(f"   • Database: {DB_NAME}")
        print(f"   • Collection: {COLLECTION_NAME}")
        print(f"   • Vector Index: {VECTOR_INDEX}")
        print(f"   • History Collection: {HISTORY_COLLECTION}")
        print("✓ Memory Layer ready!")
        
        print(f"✓ Connected to MongoDB: {DB_NAME}")
        print(f"  - Vector collection: {COLLECTION_NAME}")
        print(f"  - History collection: {HISTORY_COLLECTION}")
        print(f"  - Vector index: {VECTOR_INDEX}")
        
    except asyncio.TimeoutError:
        print("✗ MongoDB connection timed out")
        mongo_client = None
    except Exception as e:
        print(f"✗ MongoDB connection failed: {e}")
        mongo_client = None
    
    print("✓ Memory Layer ready!")


@app.post("/search", response_model=VectorSearchResponse)
async def vector_search(request: VectorSearchRequest):
    """Perform vector similarity search."""
    if not mongo_client:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        start_time = asyncio.get_event_loop().time()
        
        collection = mongo_client[DB_NAME][COLLECTION_NAME]
        
        # Build vector search pipeline
        pipeline = [{
            "$vectorSearch": {
                "index": VECTOR_INDEX,
                "path": "embedding",
                "queryVector": request.embedding,
                "numCandidates": min(150, request.top_k * 30),
                "limit": request.top_k
            }
        }, {
            "$project": {
                "content": 1,
                "metadata": 1,
                "score": {"$meta": "vectorSearchScore"},
                "_id": 0  # Exclude ObjectId to avoid serialization error
            }
        }]
        
        # Add filters if provided
        if request.filters:
            pipeline.insert(1, {"$match": request.filters})
        
        # Execute search
        cursor = collection.aggregate(pipeline)
        results = await cursor.to_list(length=request.top_k)
        
        end_time = asyncio.get_event_loop().time()
        query_time = (end_time - start_time) * 1000  # Convert to ms
        
        return VectorSearchResponse(
            results=results,
            count=len(results),
            query_time_ms=round(query_time, 2)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vector search failed: {str(e)}")


@app.post("/store", response_model=StoreConversationResponse)
async def store_conversation(request: StoreConversationRequest):
    """Store conversation turn in history."""
    if not mongo_client:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        collection = mongo_client[DB_NAME][HISTORY_COLLECTION]
        
        message = {
            "session_id": request.session_id,
            "user_message": request.user_message,
            "bot_response": request.bot_response,
            "timestamp": datetime.utcnow(),
            "metadata": request.metadata or {}
        }
        
        result = await collection.insert_one(message)
        
        return StoreConversationResponse(
            status="stored",
            session_id=request.session_id,
            message_id=str(result.inserted_id)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Store failed: {str(e)}")


@app.post("/history", response_model=GetHistoryResponse)
async def get_conversation_history(request: GetHistoryRequest):
    """Retrieve conversation history for a session."""
    if not mongo_client:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        collection = mongo_client[DB_NAME][HISTORY_COLLECTION]
        
        cursor = collection.find(
            {"session_id": request.session_id}
        ).sort("timestamp", -1).limit(request.limit)
        
        messages = await cursor.to_list(length=request.limit)
        
        # Reverse to chronological order
        messages.reverse()
        
        # Convert ObjectId to string
        for msg in messages:
            msg['_id'] = str(msg['_id'])
            msg['timestamp'] = msg['timestamp'].isoformat()
        
        return GetHistoryResponse(
            messages=messages,
            session_id=request.session_id,
            count=len(messages)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"History retrieval failed: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    mongo_status = "disconnected"
    
    if mongo_client:
        try:
            await asyncio.wait_for(
                mongo_client.admin.command('ping'),
                timeout=5.0
            )
            mongo_status = "connected"
        except:
            mongo_status = "disconnected"
    
    return {
        "status": "healthy" if mongo_status == "connected" else "degraded",
        "mongodb": mongo_status,
        "database": f"{DB_NAME}.{COLLECTION_NAME}",
        "vector_index": VECTOR_INDEX,
        "service": "memory-layer",
        "version": "1.0.0"
    }


@app.get("/")
async def root():
    """Root endpoint with service info."""
    return {
        "service": "Memory Layer",
        "description": "Vector Database and Conversation History Management",
        "version": "1.0.0",
        "endpoints": {
            "POST /search": "Vector similarity search",
            "POST /store": "Store conversation turn",
            "POST /history": "Get conversation history",
            "GET /health": "Health check"
        },
        "status": "operational"
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)

"""
Orchestrator - Main Coordinator for Multi-Agent Portfolio Chatbot
HuggingFace Space: harithkavish/nlweb-portfolio-chat (refactored)
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from typing import List, Dict, Optional
import os
import httpx
import asyncio
from datetime import datetime

app = FastAPI(
    title="Portfolio Chat Orchestrator",
    description="Multi-agent orchestration for AI-powered portfolio queries",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service endpoints
PERCEPTION_API = os.getenv("PERCEPTION_API", "https://harithkavish-perception-layer.hf.space")
MEMORY_API = os.getenv("MEMORY_API", "https://harithkavish-memory-layer.hf.space")
REASONING_API = os.getenv("REASONING_API", "https://harithkavish-reasoning-layer.hf.space")
EXECUTION_API = os.getenv("EXECUTION_API", "https://harithkavish-execution-layer.hf.space")
SAFETY_API = os.getenv("SAFETY_API", "https://harithkavish-monitoring-safety.hf.space")

# Timeouts
SERVICE_TIMEOUT = 30.0

# Request/Response Models
class ChatQuery(BaseModel):
    query: str
    top_k: int = 5
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    sources: List[Dict]
    query: str
    metadata: Dict


async def call_service(url: str, endpoint: str, data: dict, timeout: float = SERVICE_TIMEOUT) -> dict:
    """Helper to call microservice with error handling."""
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(f"{url}{endpoint}", json=data)
            response.raise_for_status()
            return response.json()
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail=f"Service timeout: {url}")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Service error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Service call failed: {str(e)}")


@app.post("/chat")
async def chat(query: ChatQuery):
    """
    Main chat endpoint - orchestrates all microservices.
    
    Flow:
    1. Validate input (Safety Layer)
    2. Generate embedding (Perception Layer)
    3. Classify intent (Perception Layer)
    4. Search for context (Memory Layer)
    5. Generate response (Reasoning Layer)
    6. Validate output (Safety Layer)
    7. Store conversation (Memory Layer)
    """
    
    start_time = datetime.now()
    session_id = query.session_id or f"session_{int(start_time.timestamp())}"
    
    try:
        # Step 1: Validate input
        validation = await call_service(
            SAFETY_API, "/validate/input",
            {"text": query.query, "session_id": session_id}
        )
        
        if not validation.get("is_safe", True):
            return {
                "response": "I'm sorry, but I cannot process that request due to safety concerns.",
                "sources": [],
                "query": query.query,
                "metadata": {"error": "Input validation failed", "issues": validation.get("issues", [])}
            }
        
        # Step 2 & 3: Perception (parallel - embedding + intent)
        perception_tasks = [
            call_service(PERCEPTION_API, "/embed", {"text": query.query}),
            call_service(PERCEPTION_API, "/classify", {"text": query.query})
        ]
        
        embed_result, classify_result = await asyncio.gather(*perception_tasks)
        
        embedding = embed_result.get("embedding")
        intent = classify_result.get("intent")
        intent_confidence = classify_result.get("confidence", 0.0)
        
        # Step 4: Memory - search for context
        search_result = await call_service(
            MEMORY_API, "/search",
            {"embedding": embedding, "top_k": query.top_k}
        )
        
        context_docs = search_result.get("results", [])
        
        # Step 5: Reasoning - generate response
        generate_result = await call_service(
            REASONING_API, "/generate",
            {
                "query": query.query,
                "context": context_docs,
                "intent": intent
            }
        )
        
        answer = generate_result.get("response")
        generation_confidence = generate_result.get("confidence", 0.0)
        
        # Step 6: Validate output
        output_validation = await call_service(
            SAFETY_API, "/validate/output",
            {"text": answer, "context": context_docs}
        )
        
        if not output_validation.get("is_safe", True):
            answer = "I apologize, but I cannot provide that response. Please rephrase your question."
        
        # Step 7: Store conversation (fire and forget)
        asyncio.create_task(
            call_service(
                MEMORY_API, "/store",
                {
                    "session_id": session_id,
                    "user_message": query.query,
                    "bot_response": answer,
                    "metadata": {
                        "intent": intent,
                        "intent_confidence": intent_confidence,
                        "generation_confidence": generation_confidence
                    }
                }
            )
        )
        
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
        
        # Calculate total processing time
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds() * 1000
        
        return {
            "response": answer,
            "sources": sources,
            "query": query.query,
            "metadata": {
                "intent": intent,
                "intent_confidence": round(intent_confidence, 3),
                "processing_time_ms": round(processing_time, 2),
                "session_id": session_id,
                "context_docs_found": len(context_docs)
            }
        }
    
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Orchestration error: {e}")
        return {
            "response": "I apologize, but I encountered an error while processing your request. Please try again.",
            "sources": [],
            "query": query.query,
            "metadata": {"error": str(e)}
        }


@app.get("/widget.js")
async def widget_javascript():
    """Serve the embeddable JavaScript widget (same as before)."""
    
    # Import widget code from your current implementation
    # For now, returning a placeholder
    js_content = """(function() {
    console.log('Portfolio Chatbot Widget v2.0 - Multi-Agent Architecture');
    // TODO: Copy widget code from current nlweb-hf-deployment/app.py
    // The widget code remains the same, just update API_BASE if needed
    const API_BASE = window.location.origin;
    // ... rest of widget code ...
})();
"""
    
    return Response(
        content=js_content,
        media_type="application/javascript; charset=utf-8"
    )


@app.get("/health")
async def health_check():
    """
    Comprehensive health check for all services.
    """
    services = {
        "perception": PERCEPTION_API,
        "memory": MEMORY_API,
        "reasoning": REASONING_API,
        "execution": EXECUTION_API,
        "safety": SAFETY_API
    }
    
    service_status = {}
    
    async def check_service(name: str, url: str):
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{url}/health")
                service_status[name] = "healthy" if response.status_code == 200 else "degraded"
        except:
            service_status[name] = "unreachable"
    
    # Check all services in parallel
    await asyncio.gather(*[
        check_service(name, url) for name, url in services.items()
    ])
    
    # Overall status
    all_healthy = all(status == "healthy" for status in service_status.values())
    
    return {
        "status": "healthy" if all_healthy else "degraded",
        "services": service_status,
        "orchestrator": "operational",
        "version": "2.0.0",
        "architecture": "multi-agent-microservices"
    }


@app.get("/")
async def root():
    """Root endpoint with service info."""
    return {
        "service": "Portfolio Chat Orchestrator",
        "description": "Multi-agent orchestration for AI-powered portfolio queries",
        "version": "2.0.0",
        "architecture": "microservices",
        "layers": {
            "perception": PERCEPTION_API,
            "memory": MEMORY_API,
            "reasoning": REASONING_API,
            "execution": EXECUTION_API,
            "safety": SAFETY_API
        },
        "endpoints": {
            "POST /chat": "Main chat endpoint",
            "GET /widget.js": "Embeddable widget",
            "GET /health": "Health check (all services)",
            "GET /openapi.json": "OpenAPI specification"
        },
        "status": "operational"
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)

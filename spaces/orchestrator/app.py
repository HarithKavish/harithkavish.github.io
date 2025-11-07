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
        
        # Step 4: Memory - search across three vector databases
        # Determine which domains to search based on intent
        domains_to_search = ["assistant", "portfolio", "knowledge"]  # Search all by default
        
        # Use multi-domain search for comprehensive context
        search_result = await call_service(
            MEMORY_API, "/search/multi",
            {
                "embedding": embedding,
                "top_k_per_domain": 3,  # Get top 3 from each domain
                "domains": domains_to_search
            }
        )
        
        # Combine results from all domains
        assistant_results = search_result.get("assistant_results", [])
        portfolio_results = search_result.get("portfolio_results", [])
        knowledge_results = search_result.get("knowledge_results", [])
        
        # Merge and prioritize based on query type
        if "who are you" in query.query.lower() or "what is neo" in query.query.lower():
            # Prioritize assistant identity for "who are you" queries
            context_docs = assistant_results + portfolio_results[:2] + knowledge_results[:1]
        elif "hire" in query.query.lower() or "work" in query.query.lower() or "project" in query.query.lower():
            # Prioritize portfolio for hiring/project queries
            context_docs = portfolio_results + assistant_results[:1] + knowledge_results[:1]
        else:
            # Balanced approach: portfolio first, then assistant, then knowledge
            context_docs = portfolio_results + assistant_results + knowledge_results
        
        # Limit total context to avoid token limits
        context_docs = context_docs[:query.top_k]
        
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
    """Serve the embeddable JavaScript widget."""
    js_content = """(function () {
    'use strict';

    // Prevent multiple initializations
    if (window.PortfolioChatbot) {
        console.warn('Portfolio Chatbot already initialized');
        return;
    }

    // Configuration
    // Detect if loaded from external site vs. orchestrator itself
    const SCRIPT_SRC = document.currentScript?.src || '';
    const API_BASE = SCRIPT_SRC ? new URL(SCRIPT_SRC).origin : window.location.origin;
    const STORAGE_KEY = 'portfolio_chat_history';
    const SESSION_KEY = 'portfolio_chat_session_id';

    // Generate or retrieve session ID
    let sessionId = localStorage.getItem(SESSION_KEY);
    if (!sessionId) {
        sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        localStorage.setItem(SESSION_KEY, sessionId);
    }

    // Chat history management
    function getChatHistory() {
        try {
            const history = localStorage.getItem(STORAGE_KEY);
            return history ? JSON.parse(history) : [];
        } catch (e) {
            console.error('Failed to load chat history:', e);
            return [];
        }
    }

    function saveChatHistory(messages) {
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
        } catch (e) {
            console.error('Failed to save chat history:', e);
        }
    }

    function addMessageToHistory(message, sender, sources = null) {
        const history = getChatHistory();
        history.push({
            text: message,
            sender: sender,
            sources: sources,
            timestamp: Date.now()
        });
        saveChatHistory(history);
    }

    function clearChatHistory() {
        localStorage.removeItem(STORAGE_KEY);
    }

    // Inject CSS with theme support
    const style = document.createElement('style');
    style.textContent = `
        #portfolio-chatbot {
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 99999;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', Arial, sans-serif;
        }
        
        /* Dark theme support */
        #portfolio-chatbot.dark-theme #chat-window {
            background: #1a1a1a;
        }
        
        #portfolio-chatbot.dark-theme #chat-messages {
            background: #2d2d2d;
        }
        
        #portfolio-chatbot.dark-theme .message.bot {
            background: #3a3a3a;
            color: #e0e0e0;
            border-color: #4a4a4a;
        }
        
        #portfolio-chatbot.dark-theme .sources {
            color: #b0b0b0;
            border-top-color: #4a4a4a;
        }
        
        #portfolio-chatbot.dark-theme .source-item {
            background: #4a4a4a;
            color: #e0e0e0;
        }
        
        #portfolio-chatbot.dark-theme #chat-input-container {
            background: #1a1a1a;
            border-top-color: #4a4a4a;
        }
        
        #portfolio-chatbot.dark-theme #chat-input {
            background: #2d2d2d;
            color: #e0e0e0;
            border-color: #4a4a4a;
        }
        
        #portfolio-chatbot.dark-theme #chat-input::placeholder {
            color: #888;
        }
        
        #portfolio-chatbot.dark-theme #chat-messages::-webkit-scrollbar-thumb {
            background: #555;
        }
        
        #chat-toggle {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            color: white;
            font-size: 28px;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(0,0,0,0.25);
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        #chat-toggle:hover {
            transform: scale(1.1);
            box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        }
        
        #chat-window {
            position: fixed;
            bottom: 90px;
            right: 20px;
            width: 380px;
            height: 550px;
            background: white;
            border-radius: 16px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.25);
            display: none;
            flex-direction: column;
            overflow: hidden;
            animation: slideIn 0.3s ease;
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        #chat-window.open {
            display: flex;
        }
        
        #chat-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            font-weight: 600;
            font-size: 16px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .header-title {
            flex: 1;
        }
        
        .header-actions {
            display: flex;
            gap: 8px;
        }
        
        #chat-clear {
            background: rgba(255,255,255,0.2);
            border: none;
            color: white;
            font-size: 14px;
            cursor: pointer;
            padding: 4px 12px;
            border-radius: 12px;
            transition: background 0.2s;
            font-weight: 500;
        }
        
        #chat-clear:hover {
            background: rgba(255,255,255,0.3);
        }
        
        #chat-close {
            background: none;
            border: none;
            color: white;
            font-size: 24px;
            cursor: pointer;
            padding: 0;
            width: 30px;
            height: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            transition: background 0.2s;
        }
        
        #chat-close:hover {
            background: rgba(255,255,255,0.2);
        }
        
        #chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: #f8f9fa;
        }
        
        #chat-messages::-webkit-scrollbar {
            width: 8px;
        }
        
        #chat-messages::-webkit-scrollbar-thumb {
            background: #ccc;
            border-radius: 4px;
        }
        
        .message {
            margin-bottom: 16px;
            padding: 12px 16px;
            border-radius: 12px;
            max-width: 85%;
            word-wrap: break-word;
            line-height: 1.5;
            animation: messageIn 0.3s ease;
        }
        
        @keyframes messageIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .message.user {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin-left: auto;
            border-bottom-right-radius: 4px;
        }
        
        .message.bot {
            background: white;
            color: #333;
            border: 1px solid #e0e0e0;
            border-bottom-left-radius: 4px;
        }
        
        .timestamp {
            font-size: 10px;
            color: rgba(255,255,255,0.7);
            margin-top: 6px;
            text-align: right;
        }
        
        .message.bot .timestamp {
            color: #999;
        }
        
        #portfolio-chatbot.dark-theme .message.bot .timestamp {
            color: #888;
        }
        
        .sources {
            font-size: 11px;
            color: #666;
            margin-top: 8px;
            padding-top: 8px;
            border-top: 1px solid #f0f0f0;
        }
        
        .source-item {
            display: inline-block;
            background: #f0f0f0;
            padding: 2px 8px;
            border-radius: 10px;
            margin: 2px;
            font-size: 10px;
        }
        
        #chat-input-container {
            padding: 16px;
            background: white;
            border-top: 1px solid #e0e0e0;
            display: flex;
            gap: 8px;
        }
        
        #chat-input {
            flex: 1;
            padding: 12px 16px;
            border: 1px solid #ddd;
            border-radius: 24px;
            outline: none;
            font-size: 14px;
            transition: border-color 0.2s;
        }
        
        #chat-input:focus {
            border-color: #667eea;
        }
        
        #chat-send {
            padding: 12px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 24px;
            cursor: pointer;
            font-weight: 600;
            transition: transform 0.2s;
        }
        
        #chat-send:hover {
            transform: scale(1.05);
        }
        
        #chat-send:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .typing-indicator {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 12px 16px;
        }
        
        .typing-indicator span {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #667eea;
            animation: typing 1.4s infinite;
        }
        
        .typing-indicator span:nth-child(1) { animation-delay: 0s; }
        .typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
        .typing-indicator span:nth-child(3) { animation-delay: 0.4s; }
        
        @keyframes typing {
            0%, 60%, 100% { transform: translateY(0); opacity: 0.7; }
            30% { transform: translateY(-10px); opacity: 1; }
        }
        
        @media (max-width: 480px) {
            #chat-window {
                width: calc(100vw - 40px);
                height: calc(100vh - 120px);
                right: 20px;
            }
        }
    `;
    document.head.appendChild(style);

    // Detect and apply theme from localStorage
    function applyTheme() {
        const savedTheme = localStorage.getItem('theme');
        const chatbot = document.getElementById('portfolio-chatbot');
        if (chatbot) {
            if (savedTheme === 'dark') {
                chatbot.classList.add('dark-theme');
            } else {
                chatbot.classList.remove('dark-theme');
            }
        }
    }

    // Listen for theme changes
    window.addEventListener('storage', (e) => {
        if (e.key === 'theme') {
            applyTheme();
        }
    });

    // Also listen for manual theme changes on the same page
    const originalSetItem = localStorage.setItem;
    localStorage.setItem = function (key, value) {
        originalSetItem.apply(this, arguments);
        if (key === 'theme') {
            applyTheme();
        }
    };

    // Inject HTML
    const widgetHTML = `
        <div id="portfolio-chatbot">
            <button id="chat-toggle" title="Chat with Neo AI - Harith Kavish's Assistant" aria-label="Open chat">
                💬
            </button>
            <div id="chat-window" role="dialog" aria-label="Chat window">
                <div id="chat-header">
                    <span class="header-title">Neo AI - Harith Kavish's Assistant</span>
                    <div class="header-actions">
                        <button id="chat-clear" title="Clear chat history" aria-label="Clear chat">🗑️ Clear</button>
                        <button id="chat-close" title="Close chat" aria-label="Close chat">×</button>
                    </div>
                </div>
                <div id="chat-messages" role="log" aria-live="polite"></div>
                <div id="chat-input-container">
                    <input 
                        id="chat-input" 
                        type="text" 
                        placeholder="Ask me anything..." 
                        aria-label="Chat message input"
                        autocomplete="off"
                    >
                    <button id="chat-send" aria-label="Send message">Send</button>
                </div>
            </div>
        </div>
    `;
    document.body.insertAdjacentHTML('beforeend', widgetHTML);

    // Apply theme immediately after widget insertion
    applyTheme();

    // Elements
    const toggle = document.getElementById('chat-toggle');
    const chatWindow = document.getElementById('chat-window');
    const closeBtn = document.getElementById('chat-close');
    const clearBtn = document.getElementById('chat-clear');
    const messagesDiv = document.getElementById('chat-messages');
    const input = document.getElementById('chat-input');
    const sendBtn = document.getElementById('chat-send');

    let isOpen = false;
    let isFirstOpen = true;

    // Toggle chat window
    function toggleChat() {
        isOpen = !isOpen;
        chatWindow.classList.toggle('open', isOpen);

        if (isOpen) {
            input.focus();
            if (isFirstOpen) {
                restoreSession();
                isFirstOpen = false;
            }
        }
    }

    // Clear chat history
    function clearChat() {
        if (confirm('Are you sure you want to clear the chat history?')) {
            clearChatHistory();
            messagesDiv.innerHTML = '';
            displayMessage("Hello! I'm Neo AI, Harith Kavish's assistant. Ask me anything about his projects, skills, or experience!", 'bot', null, false);
        }
    }

    toggle.addEventListener('click', toggleChat);
    closeBtn.addEventListener('click', toggleChat);
    clearBtn.addEventListener('click', clearChat);

    // Display message with timestamp
    function displayMessage(text, sender, sources = null, saveToHistory = true, responseTime = null) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${sender}`;
        msgDiv.textContent = text;

        // Add timestamp
        const now = new Date();
        const timeString = now.toLocaleTimeString('en-IN', { 
            hour: '2-digit', 
            minute: '2-digit',
            second: '2-digit',
            hour12: true,
            timeZone: 'Asia/Kolkata'
        });
        
        const timestampDiv = document.createElement('div');
        timestampDiv.className = 'timestamp';
        
        if (responseTime && sender === 'bot') {
            timestampDiv.textContent = `${timeString} • ${responseTime.toFixed(2)}s`;
        } else {
            timestampDiv.textContent = timeString;
        }
        
        msgDiv.appendChild(timestampDiv);

        if (sources && sources.length > 0) {
            const sourcesDiv = document.createElement('div');
            sourcesDiv.className = 'sources';
            sourcesDiv.innerHTML = '📚 Sources: ' + sources.map(s =>
                `<span class="source-item">${s.name} (${(s.score * 100).toFixed(0)}%)</span>`
            ).join('');
            msgDiv.appendChild(sourcesDiv);
        }

        messagesDiv.appendChild(msgDiv);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;

        // Save to localStorage
        if (saveToHistory) {
            addMessageToHistory(text, sender, sources);
        }
    }

    // Show typing indicator
    function showTyping() {
        const typing = document.createElement('div');
        typing.className = 'message bot';
        typing.innerHTML = '<div class="typing-indicator"><span></span><span></span><span></span></div>';
        typing.id = 'typing-indicator';
        messagesDiv.appendChild(typing);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }

    function hideTyping() {
        const typing = document.getElementById('typing-indicator');
        if (typing) typing.remove();
    }

    // Send message
    async function sendMessage() {
        const message = input.value.trim();
        if (!message) return;

        displayMessage(message, 'user');
        input.value = '';
        input.disabled = true;
        sendBtn.disabled = true;
        showTyping();

        const startTime = performance.now();

        try {
            const response = await fetch(`${API_BASE}/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    query: message,
                    top_k: 5
                })
            });

            const data = await response.json();
            const endTime = performance.now();
            const responseTime = (endTime - startTime) / 1000; // Convert to seconds
            
            hideTyping();

            displayMessage(
                data.response || 'Sorry, I could not generate a response.', 
                'bot', 
                data.sources,
                true,
                responseTime
            );
        } catch (error) {
            const endTime = performance.now();
            const responseTime = (endTime - startTime) / 1000;
            
            hideTyping();
            displayMessage(
                'Sorry, I encountered an error. Please try again.', 
                'bot',
                null,
                true,
                responseTime
            );
            console.error('Chat error:', error);
        } finally {
            input.disabled = false;
            sendBtn.disabled = false;
            input.focus();
        }
    }

    // Restore previous session
    async function restoreSession() {
        const history = getChatHistory();

        if (history.length === 0) {
            // First time user - show welcome message
            displayMessage("Hello! I'm Neo AI, Harith Kavish's assistant. Ask me anything about his projects, skills, or experience!", 'bot', null, false);
        } else {
            // Restore previous conversation
            history.forEach(msg => {
                displayMessage(msg.text, msg.sender, msg.sources, false);
            });
        }
    }

    // Event listeners
    sendBtn.addEventListener('click', sendMessage);
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Expose API for external control
    window.PortfolioChatbot = {
        open: () => { if (!isOpen) toggleChat(); },
        close: () => { if (isOpen) toggleChat(); },
        toggle: toggleChat,
        sendMessage: (msg) => {
            input.value = msg;
            sendMessage();
        }
    };

    console.log('✅ Portfolio Chatbot Widget loaded successfully!');
})();
"""
    return Response(content=js_content, media_type="application/javascript; charset=utf-8")


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

---
title: NLWeb Orchestrator
emoji: 🎯
colorFrom: red
colorTo: yellow
sdk: docker
app_file: app.py
pinned: false
---

# Orchestrator - Multi-Agent Portfolio Chatbot

Main coordination service that routes requests through all specialized layers.

## Architecture

The orchestrator coordinates 5 microservices:

1. **Perception Layer**: NLU, embeddings, intent classification
2. **Memory Layer**: Vector search, conversation history
3. **Reasoning Layer**: FLAN-T5 response generation
4. **Execution Layer**: Tool calling, GitHub integration
5. **Monitoring & Safety**: Input/output validation, rate limiting

## Request Flow

```
User Input → Safety Check → Perception → Memory Retrieval 
          → Reasoning → Tool Execution (if needed) 
          → Safety Check → Response
```

## API Endpoints

### POST /chat
Main chat endpoint for user messages.

**Request:**
```json
{
  "message": "What projects has Harith worked on?",
  "session_id": "unique-session-id"
}
```

**Response:**
```json
{
  "response": "Harith has worked on several projects including...",
  "session_id": "unique-session-id",
  "metadata": {
    "intent": "query_projects",
    "sources": ["project1", "project2"],
    "confidence": 0.92
  }
}
```

### GET /widget.js
Get the embeddable widget JavaScript.

### GET /health
Health check endpoint.

## Environment Variables

**Required:**
- `PERCEPTION_API`: URL to perception layer service
- `MEMORY_API`: URL to memory layer service
- `REASONING_API`: URL to reasoning layer service
- `EXECUTION_API`: URL to execution layer service
- `MONITORING_API`: URL to monitoring & safety service

## Integration

Embed the chatbot on any webpage:

```html
<script src="https://harithkavish-nlweb-orchestrator.hf.space/widget.js"></script>
```

## Features

- Multi-agent coordination
- Automatic error recovery and fallbacks
- Session management
- Conversation history persistence
- Rate limiting and safety checks
- Real-time streaming responses (optional)

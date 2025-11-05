# Memory Layer

Vector Database and Conversation History Management service for the multi-agent portfolio chatbot.

## Features

- **Vector Search**: MongoDB Atlas vector similarity search
- **Conversation History**: Store and retrieve chat sessions
- **Session Management**: Track conversations by session ID

## API Endpoints

### POST /search
Perform vector similarity search.

**Request:**
```json
{
  "embedding": [0.123, -0.456, ...],
  "top_k": 5,
  "filters": {"metadata.type": "Project"}
}
```

**Response:**
```json
{
  "results": [
    {
      "content": "...",
      "metadata": {...},
      "score": 0.95
    }
  ],
  "count": 5,
  "query_time_ms": 45.2
}
```

### POST /store
Store conversation turn.

**Request:**
```json
{
  "session_id": "session_123",
  "user_message": "What projects?",
  "bot_response": "Harith has worked on...",
  "metadata": {"intent": "QUESTION_ABOUT_PROJECTS"}
}
```

**Response:**
```json
{
  "status": "stored",
  "session_id": "session_123",
  "message_id": "507f1f77bcf86cd799439011"
}
```

### POST /history
Get conversation history.

**Request:**
```json
{
  "session_id": "session_123",
  "limit": 10
}
```

**Response:**
```json
{
  "messages": [
    {
      "user_message": "...",
      "bot_response": "...",
      "timestamp": "2025-11-05T10:30:00"
    }
  ],
  "session_id": "session_123",
  "count": 3
}
```

### GET /health
Health check endpoint.

## Environment Variables

```bash
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/
DB_NAME=nlweb
COLLECTION_NAME=portfolio_vectors
VECTOR_INDEX=vector_index
HISTORY_COLLECTION=conversation_history
```

## MongoDB Atlas Setup

1. Create vector search index:
```json
{
  "fields": [
    {
      "type": "vector",
      "path": "embedding",
      "numDimensions": 768,
      "similarity": "cosine"
    }
  ]
}
```

2. Create indexes for history collection:
```javascript
db.conversation_history.createIndex({ "session_id": 1, "timestamp": -1 })
```

## Deployment

### HuggingFace Spaces
1. Create new Space: `harithkavish/memory-layer`
2. Upload `app.py` and `requirements.txt`
3. Set environment variables (Secrets)
4. Deploy

### Local Testing
```bash
export MONGODB_URI="mongodb+srv://..."
pip install -r requirements.txt
python app.py
```

Access at: http://localhost:7860

## Resource Requirements

- **CPU**: 2 cores
- **RAM**: 4GB
- **Storage**: 500MB
- **External**: MongoDB Atlas (free tier OK)

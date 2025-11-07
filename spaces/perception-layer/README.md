---
title: NLWeb Perception Layer
emoji: 🧠
colorFrom: blue
colorTo: purple
sdk: docker
app_file: app.py
pinned: false
---

# Perception Layer

Natural Language Understanding and Embedding Generation service for the multi-agent portfolio chatbot.

## Features

- **Text Embeddings**: Generate 768-dimensional semantic embeddings using sentence-transformers
- **Intent Classification**: Zero-shot classification for user intent detection
- **Batch Processing**: Efficient batch embedding generation

## API Endpoints

### POST /embed
Generate embedding for a single text.

**Request:**
```json
{
  "text": "What projects has Harith worked on?"
}
```

**Response:**
```json
{
  "embedding": [0.123, -0.456, ...],
  "dimensions": 768
}
```

### POST /embed/batch
Generate embeddings for multiple texts.

**Request:**
```json
{
  "texts": ["text1", "text2", "text3"]
}
```

**Response:**
```json
{
  "embeddings": [[...], [...], [...]],
  "dimensions": 768,
  "count": 3
}
```

### POST /classify
Classify user intent.

**Request:**
```json
{
  "text": "Hello"
}
```

**Response:**
```json
{
  "intent": "GREETING",
  "confidence": 0.95,
  "details": {
    "all_intents": ["GREETING", "GENERAL_CONVERSATION", ...],
    "all_scores": [0.95, 0.03, ...]
  }
}
```

### GET /health
Health check endpoint.

## Models Used

- **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2` (384MB)
- **Intent Classification**: `facebook/bart-large-mnli` (1.6GB)

## Deployment

### HuggingFace Spaces
1. Create new Space: `harithkavish/perception-layer`
2. Upload `app.py` and `requirements.txt`
3. Set Space SDK to "Docker" with Python 3.10
4. Deploy

### Local Testing
```bash
pip install -r requirements.txt
python app.py
```

Access at: http://localhost:7860

## Resource Requirements

- **CPU**: 2 cores
- **RAM**: 8GB
- **Storage**: 2GB (models)
- **GPU**: Optional (speeds up classification)

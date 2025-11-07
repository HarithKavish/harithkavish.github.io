---
title: NLWeb Reasoning Layer
emoji: 🤔
colorFrom: purple
colorTo: pink
sdk: docker
app_file: app.py
pinned: false
---

# Reasoning Layer

Strategic reasoning and response generation service using FLAN-T5-large.

## Features

- **Text Generation**: Generate contextual responses using FLAN-T5
- **Query Analysis**: Analyze user queries for intent and complexity
- **RAG Support**: Generate responses with Retrieval-Augmented Generation

## API Endpoints

### POST /generate
Generate a response based on query and context.

**Request:**
```json
{
  "query": "What projects has Harith worked on?",
  "context": ["Project 1...", "Project 2..."],
  "max_length": 200
}
```

### POST /analyze
Analyze a query to determine type and complexity.

**Request:**
```json
{
  "query": "Tell me about your machine learning projects"
}
```

## Environment Variables

None required - model loaded from HuggingFace Hub.

## Model

- **FLAN-T5-large**: 780M parameter instruction-tuned model
- **Task**: Text-to-text generation
- **Context**: Optimized for question answering and information extraction

---
title: NLWeb Portfolio Chat
emoji: 💬
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
app_port: 7860
---

# NLWeb Portfolio Chat

An AI-powered chat interface for Harith Kavish's portfolio using Gemma2:2b and MongoDB vector search.

## Features

- 🤖 Gemma2:2b LLM for intelligent responses
- 🔍 MongoDB Atlas vector search with 0.85+ relevance scores
- 📝 Markdown formatting support
- 🌙 Dark/light theme compatibility
- ⚡ FastAPI backend with CORS support

## Usage

This Space provides the backend API for the portfolio chat feature at [harithkavish.github.io](https://harithkavish.github.io).

### Endpoints

- `GET /` - Health check
- `POST /chat` - Send chat queries
- `POST /chat/stream` - Streaming responses
- `GET /health` - Detailed health status
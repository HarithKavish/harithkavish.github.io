---
title: NLWeb Execution Layer
emoji: ⚡
colorFrom: yellow
colorTo: red
sdk: docker
app_file: app.py
pinned: false
---

# Execution Layer

Tool calling and action execution service for the multi-agent portfolio chatbot.

## Features

- **Tool Management**: Registry of available tools and their schemas
- **Safe Execution**: Sandboxed execution environment
- **GitHub Integration**: Fetch repository and profile statistics
- **Calculation Tools**: Mathematical and data processing utilities

## API Endpoints

### GET /tools
List all available tools with schemas.

**Response:**
```json
{
  "tools": [
    {
      "name": "get_github_stats",
      "description": "Get GitHub profile statistics",
      "parameters": {...}
    }
  ]
}
```

### POST /execute
Execute a tool with given parameters.

**Request:**
```json
{
  "tool_name": "get_github_stats",
  "parameters": {
    "username": "HarithKavish"
  }
}
```

## Environment Variables

- `GITHUB_TOKEN` (optional): GitHub personal access token for higher rate limits

## Available Tools

1. **get_github_stats**: Fetch GitHub user statistics
2. **get_project_status**: Get portfolio project information
3. **calculate**: Perform mathematical calculations

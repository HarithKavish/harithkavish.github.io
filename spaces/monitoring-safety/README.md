---
title: NLWeb Monitoring & Safety
emoji: 🛡️
colorFrom: red
colorTo: yellow
sdk: docker
app_file: app.py
pinned: false
---

# Monitoring & Safety Layer

Input/output validation and rate limiting service for the multi-agent portfolio chatbot.

## Features

- **Input Validation**: Detect XSS, SQL injection, and malicious content
- **Output Safety**: Check for hallucinations, harmful content, PII leakage
- **Rate Limiting**: Per-session and global rate limits
- **Analytics**: Track usage patterns and security events

## API Endpoints

### POST /validate/input
Validate user input for security threats.

**Request:**
```json
{
  "text": "User input text",
  "session_id": "session123"
}
```

**Response:**
```json
{
  "is_safe": true,
  "threats": [],
  "sanitized_text": "User input text"
}
```

### POST /validate/output
Validate AI-generated output before sending to user.

**Request:**
```json
{
  "text": "AI response",
  "query": "Original query",
  "context": ["Context data"]
}
```

**Response:**
```json
{
  "is_safe": true,
  "issues": [],
  "confidence": 0.95
}
```

### POST /rate-limit
Check if request should be rate limited.

**Request:**
```json
{
  "session_id": "session123"
}
```

**Response:**
```json
{
  "allowed": true,
  "remaining": 45,
  "reset_in": 3600
}
```

## Security Checks

### Input Validation
- XSS attack patterns
- SQL injection attempts
- Command injection
- Path traversal
- Excessive length

### Output Validation
- Hallucination detection
- PII leakage (emails, phone numbers, SSN)
- Harmful content
- Factual consistency

## Rate Limits

- **Per session**: 50 requests/hour
- **Global**: 1000 requests/hour
- **Burst**: 10 requests/minute per session

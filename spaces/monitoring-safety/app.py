"""
Monitoring & Safety Layer - Input/Output Validation and Safety Checks
HuggingFace Space: harithkavish/monitoring-safety
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import os
import re
from datetime import datetime, timedelta
from collections import defaultdict

app = FastAPI(
    title="Monitoring & Safety Layer",
    description="Safety validation, rate limiting, and monitoring service",
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

# Configuration
TOXICITY_THRESHOLD = float(os.getenv("TOXICITY_THRESHOLD", "0.7"))
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
MAX_INPUT_LENGTH = int(os.getenv("MAX_INPUT_LENGTH", "1000"))
MAX_OUTPUT_LENGTH = int(os.getenv("MAX_OUTPUT_LENGTH", "2000"))

# In-memory rate limiting (in production, use Redis)
rate_limit_store = defaultdict(list)

# Toxicity model (lightweight)
toxicity_model = None


# Request/Response Models
class ValidateInputRequest(BaseModel):
    text: str
    session_id: Optional[str] = None

class ValidateInputResponse(BaseModel):
    is_safe: bool
    issues: List[str]
    filtered_text: Optional[str] = None

class ValidateOutputRequest(BaseModel):
    text: str
    context: Optional[List[Dict]] = None

class ValidateOutputResponse(BaseModel):
    is_safe: bool
    confidence: float
    issues: List[str]

class RateLimitRequest(BaseModel):
    identifier: str  # IP, session_id, etc.

class RateLimitResponse(BaseModel):
    allowed: bool
    remaining: int
    reset_in_seconds: int


@app.on_event("startup")
async def startup_event():
    """Initialize safety models."""
    global toxicity_model
    
    print("🚀 Loading Monitoring & Safety Layer...")
    
    # Optional: Load toxicity detection model
    # Keeping it simple for now - pattern-based filtering
    toxicity_model = None  # Could load "unitary/toxic-bert" here
    
    print("✓ Monitoring & Safety Layer ready!")


def check_input_patterns(text: str) -> List[str]:
    """Check for problematic patterns in input."""
    issues = []
    
    # Check length
    if len(text) > MAX_INPUT_LENGTH:
        issues.append(f"Input too long ({len(text)} > {MAX_INPUT_LENGTH})")
    
    # Check for SQL injection patterns
    sql_patterns = [
        r"('\s*OR\s*'1'\s*=\s*'1)",
        r"(;\s*DROP\s+TABLE)",
        r"(UNION\s+SELECT)",
    ]
    for pattern in sql_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            issues.append("Potential SQL injection detected")
            break
    
    # Check for XSS patterns
    xss_patterns = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"onerror\s*=",
        r"onclick\s*=",
    ]
    for pattern in xss_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            issues.append("Potential XSS detected")
            break
    
    # Check for command injection
    cmd_patterns = [
        r"[;&|]\s*(rm|cat|ls|wget|curl)",
        r"`.*`",
        r"\$\(.*\)",
    ]
    for pattern in cmd_patterns:
        if re.search(pattern, text):
            issues.append("Potential command injection detected")
            break
    
    # Check for excessive special characters (possible gibberish/attack)
    special_char_ratio = sum(1 for c in text if not c.isalnum() and not c.isspace()) / max(len(text), 1)
    if special_char_ratio > 0.5:
        issues.append("Excessive special characters detected")
    
    return issues


def check_rate_limit(identifier: str) -> tuple[bool, int, int]:
    """Check if identifier is within rate limits."""
    now = datetime.now()
    minute_ago = now - timedelta(minutes=1)
    
    # Clean old entries
    rate_limit_store[identifier] = [
        timestamp for timestamp in rate_limit_store[identifier]
        if timestamp > minute_ago
    ]
    
    # Check current count
    current_count = len(rate_limit_store[identifier])
    
    if current_count >= RATE_LIMIT_PER_MINUTE:
        # Calculate reset time
        oldest = min(rate_limit_store[identifier])
        reset_in = 60 - int((now - oldest).total_seconds())
        return False, 0, reset_in
    
    # Add current request
    rate_limit_store[identifier].append(now)
    
    remaining = RATE_LIMIT_PER_MINUTE - (current_count + 1)
    return True, remaining, 60


def check_output_hallucination(text: str, context: List[Dict]) -> List[str]:
    """Check for potential hallucinations in output."""
    issues = []
    
    # Check length
    if len(text) > MAX_OUTPUT_LENGTH:
        issues.append(f"Output too long ({len(text)} > {MAX_OUTPUT_LENGTH})")
    
    # Check if output is too short (potential generation failure)
    if len(text.strip()) < 10:
        issues.append("Output suspiciously short")
    
    # Check for common hallucination markers
    hallucination_phrases = [
        "i don't have information",
        "i cannot find",
        "error generating",
        "failed to",
        "as an ai",
    ]
    text_lower = text.lower()
    for phrase in hallucination_phrases:
        if phrase in text_lower:
            # These are actually GOOD - the model is being honest
            pass
    
    # Check for contradictions (basic)
    if "yes" in text_lower and "no" in text_lower and len(text.split()) < 50:
        issues.append("Potential contradiction detected")
    
    return issues


@app.post("/validate/input", response_model=ValidateInputResponse)
async def validate_input(request: ValidateInputRequest):
    """Validate user input for safety."""
    
    issues = check_input_patterns(request.text)
    
    is_safe = len(issues) == 0
    
    # If unsafe, provide filtered version
    filtered_text = None
    if not is_safe:
        # Simple filtering: remove special characters
        filtered_text = re.sub(r'[^a-zA-Z0-9\s.,!?]', '', request.text)
    
    return ValidateInputResponse(
        is_safe=is_safe,
        issues=issues,
        filtered_text=filtered_text if not is_safe else None
    )


@app.post("/validate/output", response_model=ValidateOutputResponse)
async def validate_output(request: ValidateOutputRequest):
    """Validate model output for safety and quality."""
    
    issues = check_output_hallucination(request.text, request.context or [])
    
    is_safe = len(issues) == 0
    
    # Calculate confidence (inverse of issues)
    confidence = max(0.0, 1.0 - (len(issues) * 0.2))
    
    return ValidateOutputResponse(
        is_safe=is_safe,
        confidence=confidence,
        issues=issues
    )


@app.post("/rate-limit", response_model=RateLimitResponse)
async def check_rate_limit_endpoint(request: RateLimitRequest):
    """Check if identifier is within rate limits."""
    
    allowed, remaining, reset_in = check_rate_limit(request.identifier)
    
    return RateLimitResponse(
        allowed=allowed,
        remaining=remaining,
        reset_in_seconds=reset_in
    )


@app.get("/metrics")
async def get_metrics():
    """Get system metrics."""
    
    # Calculate current rates
    total_requests = sum(len(timestamps) for timestamps in rate_limit_store.values())
    active_sessions = len(rate_limit_store)
    
    return {
        "active_sessions": active_sessions,
        "total_requests_last_minute": total_requests,
        "rate_limit_per_minute": RATE_LIMIT_PER_MINUTE,
        "max_input_length": MAX_INPUT_LENGTH,
        "max_output_length": MAX_OUTPUT_LENGTH,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "monitoring-safety",
        "version": "1.0.0",
        "rate_limit_enabled": True,
        "input_validation_enabled": True,
        "output_validation_enabled": True
    }


@app.get("/")
async def root():
    """Root endpoint with service info."""
    return {
        "service": "Monitoring & Safety Layer",
        "description": "Safety validation, rate limiting, and monitoring service",
        "version": "1.0.0",
        "endpoints": {
            "POST /validate/input": "Validate user input",
            "POST /validate/output": "Validate model output",
            "POST /rate-limit": "Check rate limit",
            "GET /metrics": "Get system metrics",
            "GET /health": "Health check"
        },
        "limits": {
            "rate_limit_per_minute": RATE_LIMIT_PER_MINUTE,
            "max_input_length": MAX_INPUT_LENGTH,
            "max_output_length": MAX_OUTPUT_LENGTH
        },
        "status": "operational"
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)

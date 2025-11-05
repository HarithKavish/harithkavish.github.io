# Multi-Agent Architecture Implementation Guide

## Overview
This guide provides complete implementation for transforming your monolithic chatbot into a microservices-based multi-agent system with 6 specialized HuggingFace Spaces.

## Architecture Diagram

```
                        ┌─────────────────────────────────┐
                        │     ORCHESTRATOR (Space 3)      │
                        │  nlweb-portfolio-chat.hf.space  │
                        │                                 │
                        │  - Request routing              │
                        │  - Agent coordination           │
                        │  - Response assembly            │
                        │  - Widget serving               │
                        └────────────┬────────────────────┘
                                     │
              ┌──────────────────────┼──────────────────────┐
              │                      │                      │
    ┌─────────▼─────────┐  ┌────────▼────────┐  ┌─────────▼──────────┐
    │  PERCEPTION (S4)  │  │  MEMORY (S5)    │  │  REASONING (S6)    │
    │  perception-layer │  │  memory-layer   │  │  reasoning-layer   │
    │                   │  │                 │  │                    │
    │  - Embeddings     │  │  - Vector DB    │  │  - FLAN-T5        │
    │  - Intent detect  │  │  - History      │  │  - Generation     │
    │  - NLU            │  │  - Context      │  │  - Planning       │
    └───────────────────┘  └─────────────────┘  └────────────────────┘
              │                      │                      │
    ┌─────────▼─────────┐  ┌────────▼────────────────────┐
    │  EXECUTION (S7)   │  │  MONITORING & SAFETY (S8)   │
    │  execution-layer  │  │  monitoring-safety          │
    │                   │  │                             │
    │  - Tool calling   │  │  - Input validation         │
    │  - API calls      │  │  - Output safety            │
    │  - Actions        │  │  - Rate limiting            │
    └───────────────────┘  └─────────────────────────────┘
```

## Space Configuration

| Space # | Name | URL | Purpose | Resources |
|---------|------|-----|---------|-----------|
| 3 | orchestrator | nlweb-portfolio-chat.hf.space | Main coordinator | 2 CPU, 4GB RAM |
| 4 | perception-layer | perception-layer.hf.space | Embeddings & NLU | 2 CPU, 8GB RAM |
| 5 | memory-layer | memory-layer.hf.space | Vector DB & history | 2 CPU, 4GB RAM |
| 6 | reasoning-layer | reasoning-layer.hf.space | LLM generation | 2 CPU, 16GB RAM |
| 7 | execution-layer | execution-layer.hf.space | Action execution | 2 CPU, 4GB RAM |
| 8 | monitoring-safety | monitoring-safety.hf.space | Safety & logging | 2 CPU, 4GB RAM |

---

## Implementation Timeline

### Week 1: Foundation
- Day 1-2: Create all Space repositories
- Day 3-4: Deploy Memory Layer
- Day 5-7: Deploy Perception Layer

### Week 2: Core Intelligence
- Day 1-3: Deploy Reasoning Layer
- Day 4-5: Deploy Execution Layer
- Day 6-7: Deploy Monitoring & Safety

### Week 3: Integration
- Day 1-5: Refactor Orchestrator
- Day 6-7: End-to-end testing

### Week 4: Optimization
- Day 1-3: Performance tuning
- Day 4-5: Error handling
- Day 6-7: Documentation & deployment

---

## Service Dependencies

```
Orchestrator depends on:
├─ Perception Layer (required)
├─ Memory Layer (required)
├─ Reasoning Layer (required)
├─ Execution Layer (optional)
└─ Monitoring & Safety (required)

Perception Layer:
└─ No dependencies (standalone)

Memory Layer:
└─ MongoDB Atlas (external)

Reasoning Layer:
└─ No dependencies (standalone)

Execution Layer:
└─ External APIs (GitHub, etc.)

Monitoring & Safety:
└─ No dependencies (standalone)
```

---

## API Contracts

### Orchestrator → Perception
```
POST https://harithkavish-perception-layer.hf.space/embed
Request:  {"text": "What projects has Harith worked on?"}
Response: {"embedding": [0.123, -0.456, ...], "dimensions": 768}

POST https://harithkavish-perception-layer.hf.space/classify
Request:  {"text": "Hello"}
Response: {"intent": "GREETING", "confidence": 0.95}
```

### Orchestrator → Memory
```
POST https://harithkavish-memory-layer.hf.space/search
Request:  {"embedding": [...], "top_k": 5}
Response: {"results": [{"content": "...", "score": 0.95, "metadata": {...}}]}

POST https://harithkavish-memory-layer.hf.space/store
Request:  {"session_id": "123", "messages": [...]}
Response: {"status": "stored", "count": 2}
```

### Orchestrator → Reasoning
```
POST https://harithkavish-reasoning-layer.hf.space/generate
Request:  {"query": "...", "context": [...]}
Response: {"response": "Harith has worked on...", "confidence": 0.92}
```

### Orchestrator → Execution
```
POST https://harithkavish-execution-layer.hf.space/execute
Request:  {"action": "check_status", "params": {"project": "SkinNet"}}
Response: {"result": {"status": "online", "uptime": "99.9%"}}
```

### Orchestrator → Monitoring & Safety
```
POST https://harithkavish-monitoring-safety.hf.space/validate/input
Request:  {"text": "user input"}
Response: {"is_safe": true, "issues": []}

POST https://harithkavish-monitoring-safety.hf.space/validate/output
Request:  {"text": "bot response"}
Response: {"is_safe": true, "confidence": 0.98}
```

---

## Environment Variables

### All Spaces (Common)
```bash
# Logging
LOG_LEVEL=INFO
ENVIRONMENT=production

# CORS
ALLOWED_ORIGINS=*
```

### Memory Layer
```bash
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/
DB_NAME=nlweb
COLLECTION_NAME=portfolio_vectors
VECTOR_INDEX=vector_index
```

### Reasoning Layer
```bash
MODEL_NAME=google/flan-t5-large
MAX_TOKENS=250
TEMPERATURE=0.7
```

### Execution Layer
```bash
GITHUB_TOKEN=ghp_xxx...
GITHUB_USERNAME=HarithKavish
```

### Monitoring & Safety
```bash
TOXICITY_THRESHOLD=0.7
RATE_LIMIT_PER_MINUTE=60
```

---

## Deployment Checklist

### Pre-Deployment
- [ ] Create HuggingFace Spaces (6 new)
- [ ] Set up environment variables
- [ ] Configure MongoDB Atlas
- [ ] Test each service locally

### Deployment Order
1. [ ] Deploy Memory Layer (no dependencies)
2. [ ] Deploy Perception Layer (no dependencies)
3. [ ] Deploy Reasoning Layer (no dependencies)
4. [ ] Deploy Execution Layer (no dependencies)
5. [ ] Deploy Monitoring & Safety (no dependencies)
6. [ ] Deploy Orchestrator (depends on all)

### Post-Deployment
- [ ] Health check all endpoints
- [ ] Update manifests (.well-known/)
- [ ] Test end-to-end flow
- [ ] Monitor logs
- [ ] Performance benchmarking

---

## Monitoring & Observability

### Health Check Endpoints
```
GET https://harithkavish-perception-layer.hf.space/health
GET https://harithkavish-memory-layer.hf.space/health
GET https://harithkavish-reasoning-layer.hf.space/health
GET https://harithkavish-execution-layer.hf.space/health
GET https://harithkavish-monitoring-safety.hf.space/health
GET https://harithkavish-nlweb-portfolio-chat.hf.space/health
```

### Metrics to Track
- Request latency per layer
- Error rates
- Token usage (Reasoning layer)
- Cache hit rates (Memory layer)
- Safety validation failures

---

## Rollback Plan

### If Issues Arise
1. **Orchestrator can fallback to monolithic mode**
   - Keep old code in separate branch
   - Feature flag for microservices vs monolithic

2. **Individual layer failures**
   - Orchestrator detects unhealthy services
   - Falls back to cached responses or default behavior

3. **Complete rollback**
   - Revert orchestrator to monolithic version
   - No changes to widget or manifests needed

---

## Cost Analysis

### HuggingFace Pro
- **Monthly:** $9/month (unlimited Spaces)
- **Per Space:** FREE (included in Pro)

### MongoDB Atlas
- **Current:** Free tier (512MB, 100 connections)
- **If needed:** Shared tier $9/month (2GB, 500 connections)

### Total Monthly Cost
- **Minimum:** $9/month (HF Pro only)
- **Maximum:** $18/month (HF Pro + MongoDB)

---

## Performance Expectations

### Latency Breakdown
```
User Query → Orchestrator:           10ms
Orchestrator → Perception:           50ms  (embedding generation)
Orchestrator → Memory:               100ms (vector search)
Orchestrator → Reasoning:            1-2s  (LLM generation)
Orchestrator → Safety:               50ms  (validation)
Orchestrator → User Response:        ~1.5-2.5s total
```

### Throughput
- **Monolithic:** ~5 req/sec (single Space bottleneck)
- **Microservices:** ~20 req/sec (parallel processing)

---

## Next Steps

See individual implementation files:
1. `spaces/perception-layer/` - Perception Layer code
2. `spaces/memory-layer/` - Memory Layer code
3. `spaces/reasoning-layer/` - Reasoning Layer code
4. `spaces/execution-layer/` - Execution Layer code
5. `spaces/monitoring-safety/` - Monitoring & Safety code
6. `spaces/orchestrator/` - Orchestrator code

Each directory contains:
- `app.py` - Main FastAPI application
- `requirements.txt` - Python dependencies
- `Dockerfile` - Container configuration (optional)
- `README.md` - Service-specific documentation

# Multi-Agent Chatbot - Deployment Guide

## Overview
This guide walks you through deploying all 6 microservices to HuggingFace Spaces.

## Prerequisites

- HuggingFace Account (Pro tier - $9/month for unlimited Spaces)
- MongoDB Atlas account (free tier is sufficient)
- GitHub account (for version control)

## Deployment Order

Deploy in this order to respect dependencies:

1. **Memory Layer** (no dependencies)
2. **Perception Layer** (no dependencies)
3. **Reasoning Layer** (no dependencies)
4. **Execution Layer** (no dependencies)
5. **Monitoring & Safety** (no dependencies)
6. **Orchestrator** (depends on all above)

---

## 1. Deploy Memory Layer

### Step 1: Create HuggingFace Space
1. Go to https://huggingface.co/new-space
2. Name: `memory-layer`
3. SDK: **Docker**
4. Hardware: **CPU basic** (free)
5. Click "Create Space"

### Step 2: Upload Files
Upload from `spaces/memory-layer/`:
- `app.py`
- `requirements.txt`
- `README.md`

### Step 3: Configure Secrets
In Space Settings → Repository secrets:
```
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
DB_NAME=nlweb
COLLECTION_NAME=portfolio_vectors
VECTOR_INDEX=vector_index
HISTORY_COLLECTION=conversation_history
```

### Step 4: Create Dockerfile
Create `Dockerfile` in the Space:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 7860

CMD ["python", "app.py"]
```

### Step 5: Deploy
- Space will auto-build and deploy
- Wait for "Running" status
- Test: `https://harithkavish-memory-layer.hf.space/health`

---

## 2. Deploy Perception Layer

### Step 1: Create Space
- Name: `perception-layer`
- SDK: **Docker**
- Hardware: **CPU basic** (or upgrade to **GPU** for faster classification)

### Step 2: Upload Files
From `spaces/perception-layer/`:
- `app.py`
- `requirements.txt`
- `README.md`

### Step 3: Create Dockerfile
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 7860

CMD ["python", "app.py"]
```

### Step 4: Deploy
- Wait for build (~5-10 minutes, models are large)
- Test: `https://harithkavish-perception-layer.hf.space/health`

---

## 3. Deploy Reasoning Layer

### Step 1: Create Space
- Name: `reasoning-layer`
- SDK: **Docker**
- Hardware: **CPU basic** (or **GPU T4** for faster generation)

### Step 2: Upload Files
From `spaces/reasoning-layer/`:
- `app.py`
- `requirements.txt`
- `README.md`

### Step 3: Configure Environment (optional)
```
MODEL_NAME=google/flan-t5-large
MAX_TOKENS=250
TEMPERATURE=0.7
```

### Step 4: Create Dockerfile
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 7860

CMD ["python", "app.py"]
```

### Step 5: Deploy
- Build time: ~10-15 minutes (FLAN-T5 is ~3GB)
- Test: `https://harithkavish-reasoning-layer.hf.space/health`

---

## 4. Deploy Execution Layer

### Step 1: Create Space
- Name: `execution-layer`
- SDK: **Docker**
- Hardware: **CPU basic**

### Step 2: Upload Files
From `spaces/execution-layer/`:
- `app.py`
- `requirements.txt`
- `README.md`

### Step 3: Configure Secrets (optional)
```
GITHUB_TOKEN=ghp_your_token_here
GITHUB_USERNAME=HarithKavish
```

### Step 4: Create Dockerfile
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 7860

CMD ["python", "app.py"]
```

### Step 5: Deploy
- Test: `https://harithkavish-execution-layer.hf.space/health`

---

## 5. Deploy Monitoring & Safety

### Step 1: Create Space
- Name: `monitoring-safety`
- SDK: **Docker**
- Hardware: **CPU basic**

### Step 2: Upload Files
From `spaces/monitoring-safety/`:
- `app.py`
- `requirements.txt`
- `README.md`

### Step 3: Configure Environment (optional)
```
TOXICITY_THRESHOLD=0.7
RATE_LIMIT_PER_MINUTE=60
MAX_INPUT_LENGTH=1000
MAX_OUTPUT_LENGTH=2000
```

### Step 4: Create Dockerfile
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 7860

CMD ["python", "app.py"]
```

### Step 5: Deploy
- Test: `https://harithkavish-monitoring-safety.hf.space/health`

---

## 6. Deploy Orchestrator (Main Service)

### Step 1: Update Existing Space
- Use your existing Space: `nlweb-portfolio-chat`
- This maintains backward compatibility (same URL)

### Step 2: Backup Current Code
```bash
cd nlweb-hf-deployment
git checkout -b monolithic-backup
git push origin monolithic-backup
```

### Step 3: Replace with Orchestrator Code
From `spaces/orchestrator/`:
- Replace `app.py`
- Update `requirements.txt`
- Update `README.md`

### Step 4: Configure Environment Variables
In Space Settings → Repository secrets:
```
PERCEPTION_API=https://harithkavish-perception-layer.hf.space
MEMORY_API=https://harithkavish-memory-layer.hf.space
REASONING_API=https://harithkavish-reasoning-layer.hf.space
EXECUTION_API=https://harithkavish-execution-layer.hf.space
SAFETY_API=https://harithkavish-monitoring-safety.hf.space
```

### Step 5: Copy Widget Code
Copy the widget JavaScript from your current `app.py` (lines with widget HTML/CSS/JS) into the `/widget.js` endpoint in the new orchestrator.

### Step 6: Deploy
- Space will rebuild
- Test: `https://harithkavish-nlweb-portfolio-chat.hf.space/health`
- Should show all services status

---

## Testing the Complete System

### 1. Health Check All Services
```bash
curl https://harithkavish-memory-layer.hf.space/health
curl https://harithkavish-perception-layer.hf.space/health
curl https://harithkavish-reasoning-layer.hf.space/health
curl https://harithkavish-execution-layer.hf.space/health
curl https://harithkavish-monitoring-safety.hf.space/health
curl https://harithkavish-nlweb-portfolio-chat.hf.space/health
```

### 2. Test End-to-End Chat
```bash
curl -X POST https://harithkavish-nlweb-portfolio-chat.hf.space/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What projects has Harith worked on?", "top_k": 5}'
```

Expected response:
```json
{
  "response": "Harith has worked on several AI projects including...",
  "sources": [...],
  "query": "What projects has Harith worked on?",
  "metadata": {
    "intent": "QUESTION_ABOUT_PROJECTS",
    "processing_time_ms": 1500,
    ...
  }
}
```

### 3. Test Widget
Visit any page on `harithkavish.github.io` - the widget should auto-load and work as before.

---

## Rollback Plan

If anything goes wrong:

### Option 1: Rollback Orchestrator Only
```bash
cd nlweb-hf-deployment
git checkout monolithic-backup
git push origin main --force
```

### Option 2: Pause Individual Services
In each Space's Settings:
- Set Space to "Paused"
- Orchestrator will handle service failures gracefully

### Option 3: Feature Flag
Add environment variable to Orchestrator:
```
USE_MICROSERVICES=false
```

Then add fallback code in orchestrator to use monolithic mode.

---

## Monitoring

### Dashboard
Create a simple monitoring dashboard:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Service Status Dashboard</title>
    <script>
        async function checkHealth() {
            const services = {
                'Orchestrator': 'https://harithkavish-nlweb-portfolio-chat.hf.space/health',
                'Perception': 'https://harithkavish-perception-layer.hf.space/health',
                'Memory': 'https://harithkavish-memory-layer.hf.space/health',
                'Reasoning': 'https://harithkavish-reasoning-layer.hf.space/health',
                'Execution': 'https://harithkavish-execution-layer.hf.space/health',
                'Safety': 'https://harithkavish-monitoring-safety.hf.space/health'
            };
            
            for (const [name, url] of Object.entries(services)) {
                try {
                    const response = await fetch(url);
                    const data = await response.json();
                    document.getElementById(name).textContent = data.status;
                } catch (e) {
                    document.getElementById(name).textContent = 'ERROR';
                }
            }
        }
        
        setInterval(checkHealth, 30000); // Check every 30s
        checkHealth(); // Initial check
    </script>
</head>
<body>
    <h1>Multi-Agent Chatbot Status</h1>
    <ul>
        <li>Orchestrator: <span id="Orchestrator">Checking...</span></li>
        <li>Perception: <span id="Perception">Checking...</span></li>
        <li>Memory: <span id="Memory">Checking...</span></li>
        <li>Reasoning: <span id="Reasoning">Checking...</span></li>
        <li>Execution: <span id="Execution">Checking...</span></li>
        <li>Safety: <span id="Safety">Checking...</span></li>
    </ul>
</body>
</html>
```

---

## Troubleshooting

### Service Unreachable
1. Check Space status in HuggingFace
2. Check logs in Space settings
3. Verify environment variables
4. Test `/health` endpoint directly

### Slow Performance
1. Upgrade Spaces to GPU (Reasoning & Perception)
2. Increase timeouts in Orchestrator
3. Enable caching in Memory Layer

### Out of Memory
1. Reduce model sizes (use smaller FLAN-T5)
2. Upgrade Space hardware
3. Optimize batch sizes

---

## Cost Summary

### HuggingFace Pro
- **$9/month** for unlimited Spaces

### MongoDB Atlas
- **Free tier**: 512MB storage (sufficient for portfolio data)
- **Paid tier**: $9/month for 2GB (if you need more)

### Total Monthly Cost
- **Minimum**: $9/month
- **With MongoDB**: $18/month

---

## Next Steps

1. Deploy all 6 services (follow order above)
2. Test end-to-end functionality
3. Monitor for 24 hours
4. Update manifests (.well-known/) if URLs changed
5. Optimize performance based on metrics

---

## Support

If you encounter issues:
1. Check Space logs
2. Test each service individually
3. Review error messages in `/health` endpoints
4. Verify all environment variables are set correctly

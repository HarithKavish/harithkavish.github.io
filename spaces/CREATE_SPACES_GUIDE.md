# Multi-Agent Chatbot - Automated Space Creator

This script will guide you through creating all 6 HuggingFace Spaces automatically.

## Prerequisites

1. **HuggingFace CLI** installed:
```bash
pip install huggingface-hub
```

2. **Login to HuggingFace**:
```bash
huggingface-cli login
```
(You'll need your HF token from https://huggingface.co/settings/tokens)

3. **Git** installed and configured

## Automated Creation Script

Run the PowerShell script below to create all Spaces:

```powershell
.\create_all_spaces.ps1
```

Or create them manually following the steps in this guide.

## Manual Creation Steps

### Step 1: Perception Layer

```bash
cd spaces/perception-layer

# Initialize git repo
git init
git add .
git commit -m "Initial perception layer implementation"

# Create Space and push
huggingface-cli repo create perception-layer --type space --space_sdk docker
git remote add origin https://huggingface.co/spaces/harithkavish/perception-layer
git push origin main -f
```

### Step 2: Memory Layer

```bash
cd ../memory-layer

git init
git add .
git commit -m "Initial memory layer implementation"

huggingface-cli repo create memory-layer --type space --space_sdk docker
git remote add origin https://huggingface.co/spaces/harithkavish/memory-layer
git push origin main -f
```

### Step 3: Reasoning Layer

```bash
cd ../reasoning-layer

git init
git add .
git commit -m "Initial reasoning layer implementation"

huggingface-cli repo create reasoning-layer --type space --space_sdk docker
git remote add origin https://huggingface.co/spaces/harithkavish/reasoning-layer
git push origin main -f
```

### Step 4: Execution Layer

```bash
cd ../execution-layer

git init
git add .
git commit -m "Initial execution layer implementation"

huggingface-cli repo create execution-layer --type space --space_sdk docker
git remote add origin https://huggingface.co/spaces/harithkavish/execution-layer
git push origin main -f
```

### Step 5: Monitoring & Safety

```bash
cd ../monitoring-safety

git init
git add .
git commit -m "Initial monitoring & safety layer implementation"

huggingface-cli repo create monitoring-safety --type space --space_sdk docker
git remote add origin https://huggingface.co/spaces/harithkavish/monitoring-safety
git push origin main -f
```

### Step 6: Orchestrator

This will update your existing `nlweb-portfolio-chat` Space:

```bash
cd ../orchestrator

# Copy to your existing nlweb-hf-deployment directory
# This preserves your existing Space URL
```

## Post-Creation: Configure Secrets

For each Space, go to Settings → Repository secrets and add:

### Memory Layer
```
MONGODB_URI=your_mongodb_connection_string
DB_NAME=nlweb
COLLECTION_NAME=portfolio_vectors
VECTOR_INDEX=vector_index
HISTORY_COLLECTION=conversation_history
```

### Orchestrator (nlweb-portfolio-chat)
```
PERCEPTION_API=https://harithkavish-perception-layer.hf.space
MEMORY_API=https://harithkavish-memory-layer.hf.space
REASONING_API=https://harithkavish-reasoning-layer.hf.space
EXECUTION_API=https://harithkavish-execution-layer.hf.space
SAFETY_API=https://harithkavish-monitoring-safety.hf.space
```

### Execution Layer (optional)
```
GITHUB_TOKEN=ghp_your_token
GITHUB_USERNAME=HarithKavish
```

## Verification

After all Spaces are created and running, verify:

```bash
# Check all health endpoints
curl https://harithkavish-perception-layer.hf.space/health
curl https://harithkavish-memory-layer.hf.space/health
curl https://harithkavish-reasoning-layer.hf.space/health
curl https://harithkavish-execution-layer.hf.space/health
curl https://harithkavish-monitoring-safety.hf.space/health

# Check orchestrator (shows all services)
curl https://harithkavish-nlweb-portfolio-chat.hf.space/health
```

## Troubleshooting

If Space creation fails:
1. Ensure you're logged in: `huggingface-cli whoami`
2. Check if Space name is already taken
3. Verify you have HF Pro (for unlimited Spaces)

## Next Steps

Once all Spaces are created and running:
1. Test end-to-end with a chat query
2. Update manifests if needed
3. Monitor logs for any issues
4. Optimize based on performance metrics

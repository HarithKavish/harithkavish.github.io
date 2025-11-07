# Windows Deployment Guide (PATH Issues Workaround)

Since `pip` and `huggingface-cli` are not in your PATH, use these commands instead:

## Step 1: Authenticate with HuggingFace

### Option A - Using Token Directly (Recommended)
1. Go to: https://huggingface.co/settings/tokens
2. Create a new token with **write** access
3. Run this command (replace `YOUR_TOKEN_HERE` with your actual token):

```powershell
$env:HF_TOKEN = "YOUR_TOKEN_HERE"
py -c "from huggingface_hub import login; login(token='$env:HF_TOKEN')"
```

### Option B - Using Browser
```powershell
py -c "from huggingface_hub import login; login()"
```
This will open a browser for authentication.

## Step 2: Verify Authentication

```powershell
py -c "from huggingface_hub import whoami; print(whoami())"
```

You should see your username and account info.

## Step 3: Create Spaces Manually

Since the automation script relies on `huggingface-cli` being in PATH, we'll create each Space manually using Python:

### Create Perception Layer Space
```powershell
cd spaces\perception-layer
py -c "from huggingface_hub import create_repo; create_repo('harithkavish-nlweb-perception', repo_type='space', space_sdk='docker')"
git init
git remote add space https://huggingface.co/spaces/HarithKavish/harithkavish-nlweb-perception
git add .
git commit -m "Initial perception layer deployment"
git push --force space main
```

### Create Memory Layer Space
```powershell
cd ..\memory-layer
py -c "from huggingface_hub import create_repo; create_repo('harithkavish-nlweb-memory', repo_type='space', space_sdk='docker')"
git init
git remote add space https://huggingface.co/spaces/HarithKavish/harithkavish-nlweb-memory
git add .
git commit -m "Initial memory layer deployment"
git push --force space main
```

### Create Reasoning Layer Space
```powershell
cd ..\reasoning-layer
py -c "from huggingface_hub import create_repo; create_repo('harithkavish-nlweb-reasoning', repo_type='space', space_sdk='docker')"
git init
git remote add space https://huggingface.co/spaces/HarithKavish/harithkavish-nlweb-reasoning
git add .
git commit -m "Initial reasoning layer deployment"
git push --force space main
```

### Create Execution Layer Space
```powershell
cd ..\execution-layer
py -c "from huggingface_hub import create_repo; create_repo('harithkavish-nlweb-execution', repo_type='space', space_sdk='docker')"
git init
git remote add space https://huggingface.co/spaces/HarithKavish/harithkavish-nlweb-execution
git add .
git commit -m "Initial execution layer deployment"
git push --force space main
```

### Create Monitoring & Safety Layer Space
```powershell
cd ..\monitoring-safety
py -c "from huggingface_hub import create_repo; create_repo('harithkavish-nlweb-monitoring', repo_type='space', space_sdk='docker')"
git init
git remote add space https://huggingface.co/spaces/HarithKavish/harithkavish-nlweb-monitoring
git add .
git commit -m "Initial monitoring layer deployment"
git push --force space main
```

### Create Orchestrator Space
```powershell
cd ..\orchestrator
py -c "from huggingface_hub import create_repo; create_repo('harithkavish-nlweb-orchestrator', repo_type='space', space_sdk='docker')"
git init
git remote add space https://huggingface.co/spaces/HarithKavish/harithkavish-nlweb-orchestrator
git add .
git commit -m "Initial orchestrator deployment"
git push --force space main
```

## Step 4: Configure Environment Variables

After each Space is created, go to the Space's settings on HuggingFace and add these secrets:

### Memory Layer Secrets:
- `MONGODB_URI` - Your MongoDB Atlas connection string
- `DB_NAME` - `portfolio_chatbot`
- `COLLECTION_NAME` - `portfolio_data`
- `VECTOR_INDEX` - `vector_index`

### Orchestrator Secrets:
- `PERCEPTION_API` - https://harithkavish-nlweb-perception.hf.space
- `MEMORY_API` - https://harithkavish-nlweb-memory.hf.space
- `REASONING_API` - https://harithkavish-nlweb-reasoning.hf.space
- `EXECUTION_API` - https://harithkavish-nlweb-execution.hf.space
- `MONITORING_API` - https://harithkavish-nlweb-monitoring.hf.space

### Execution Layer (Optional):
- `GITHUB_TOKEN` - Your GitHub personal access token

## Step 5: Wait for Builds

Each Space will take 5-15 minutes to build. You can monitor progress at:
- https://huggingface.co/spaces/HarithKavish/harithkavish-nlweb-perception
- https://huggingface.co/spaces/HarithKavish/harithkavish-nlweb-memory
- https://huggingface.co/spaces/HarithKavish/harithkavish-nlweb-reasoning
- https://huggingface.co/spaces/HarithKavish/harithkavish-nlweb-execution
- https://huggingface.co/spaces/HarithKavish/harithkavish-nlweb-monitoring
- https://huggingface.co/spaces/HarithKavish/harithkavish-nlweb-orchestrator

## Step 6: Test

Once all Spaces are running, test the orchestrator:

```powershell
py -c "import requests; r = requests.post('https://harithkavish-nlweb-orchestrator.hf.space/chat', json={'message': 'Hello', 'session_id': 'test'}); print(r.json())"
```

## Alternative: Fix PATH Issues

If you want to use the automation scripts in the future, add Python's Scripts folder to your PATH:

1. Find Python's Scripts folder:
```powershell
py -c "import sys; import os; print(os.path.join(sys.prefix, 'Scripts'))"
```

2. Add that path to your Windows PATH environment variable
3. Restart your terminal
4. Then you can use `pip` and `huggingface-cli` directly

## Quick Start Command

If you just want to authenticate quickly:

```powershell
# Get your token from: https://huggingface.co/settings/tokens
# Then run:
py -c "from huggingface_hub import login; login(token='hf_YOUR_TOKEN_HERE')"
```

Replace `hf_YOUR_TOKEN_HERE` with your actual token.

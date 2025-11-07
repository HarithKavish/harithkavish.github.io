# NLWeb Implementation Guide

## What is NLWeb?

**NLWeb** is Microsoft's open-source project that brings conversational interfaces to websites using natural language and Schema.org. Think of it as "HTML for the agentic web" - it allows websites to provide natural language APIs that can be used by both humans and AI agents.

### Key Features:
- **Natural language queries** to website content
- **Schema.org** based responses (structured data)
- **MCP (Model Context Protocol)** support for AI agents
- **Platform-agnostic**: Works on Windows, macOS, Linux
- **Multiple LLM support**: OpenAI, DeepSeek, Gemini, Anthropic, HuggingFace
- **Vector database support**: Qdrant, Milvus, Azure AI Search, Elasticsearch, Postgres, etc.

---

## Step 1: Prerequisites

### System Requirements:
- **Python 3.9+** (3.10 or 3.11 recommended)
- **Git** (to clone the repository)
- **pip** (Python package manager)
- Optional: **Docker** (for containerized deployment)

### Check your Python version:
```powershell
python --version
```

If you need to install Python:
1. Download from [python.org](https://www.python.org/downloads/)
2. During installation, check "Add Python to PATH"

---

## Step 2: Clone the NLWeb Repository

```powershell
# Navigate to your projects directory
cd C:\Dev\GitHub

# Clone the NLWeb repository
git clone https://github.com/nlweb-ai/NLWeb.git

# Navigate into the project
cd NLWeb
```

---

## Step 3: Set Up the Environment

### Create a virtual environment:
```powershell
# Create virtual environment
python -m venv venv

# Activate it (PowerShell)
.\venv\Scripts\Activate.ps1

# If you get execution policy error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Install dependencies:
```powershell
# Install required packages
pip install -r requirements.txt
```

---

## Step 4: Configure NLWeb

### Copy the environment template:
```powershell
# Copy the template
copy .env.template .env
```

### Edit `.env` file with your settings:
```env
# Choose your LLM provider
LLM_PROVIDER=openai  # or deepseek, gemini, anthropic, huggingface

# OpenAI Configuration (if using OpenAI)
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini  # or gpt-4, gpt-3.5-turbo

# Vector Database (Qdrant is simplest to start)
VECTOR_STORE=qdrant
QDRANT_HOST=localhost
QDRANT_PORT=6333

# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# Optional: Azure AI Search (if you prefer Azure)
# AZURE_SEARCH_ENDPOINT=your_endpoint
# AZURE_SEARCH_KEY=your_key
```

### Get API Keys:
- **OpenAI**: [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- **Anthropic**: [console.anthropic.com](https://console.anthropic.com)
- **Google Gemini**: [makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
- **DeepSeek**: [platform.deepseek.com](https://platform.deepseek.com)

---

## Step 5: Set Up Vector Database (Qdrant - Easiest Option)

### Option A: Using Docker (Recommended):
```powershell
# Pull and run Qdrant
docker run -p 6333:6333 -p 6334:6334 -v ${PWD}/qdrant_storage:/qdrant/storage qdrant/qdrant
```

### Option B: Install Qdrant locally:
Download from [qdrant.tech/documentation/guides/installation/](https://qdrant.tech/documentation/guides/installation/)

---

## Step 6: Ingest Your Data

NLWeb needs data to answer queries. You can ingest:
- **Schema.org JSONL** files
- **RSS feeds**
- **Custom data**

### Example: Ingest your portfolio data
Create a file `my_data.jsonl` with your projects:

```jsonl
{"@type":"SoftwareApplication","name":"SkinNet Analyzer","description":"AI-powered skin condition detection","url":"https://harithkavish.github.io/SkinNet-Analyzer/"}
{"@type":"SoftwareApplication","name":"Object Detector","description":"Multi-object detection using YOLO","url":"https://harithkavish.github.io/Multi-Object-Detection-using-YOLO/"}
```

### Ingest the data:
```powershell
python scripts/ingest_data.py --file my_data.jsonl --collection portfolio
```

---

## Step 7: Run NLWeb Server

### Start the server:
```powershell
# Using the startup script
python start_server_debug.py

# Or directly with uvicorn
uvicorn code.main:app --host 0.0.0.0 --port 8000 --reload
```

### Test it in your browser:
Open [http://localhost:8000](http://localhost:8000)

You should see the NLWeb UI!

---

## Step 8: Test the Natural Language API

### Using curl (PowerShell):
```powershell
# Ask a natural language question
curl -X POST http://localhost:8000/api/ask `
  -H "Content-Type: application/json" `
  -d '{"question": "What projects does Harith have?"}'
```

### Expected response (Schema.org JSON):
```json
{
  "@context": "https://schema.org",
  "@type": "ItemList",
  "itemListElement": [
    {
      "@type": "SoftwareApplication",
      "name": "SkinNet Analyzer",
      "description": "AI-powered skin condition detection"
    }
  ]
}
```

---

## Step 9: Deploy Your NLWeb Instance

### Option A: Deploy to Azure App Service

```powershell
# Install Azure CLI
# Download from: https://aka.ms/installazurecliwindows

# Login
az login

# Create resource group
az group create --name nlweb-rg --location eastus

# Create app service plan
az appservice plan create --name nlweb-plan --resource-group nlweb-rg --sku B1 --is-linux

# Create web app
az webapp create --name harithkavish-nlweb --resource-group nlweb-rg --plan nlweb-plan --runtime "PYTHON|3.11"

# Deploy
az webapp up --name harithkavish-nlweb --resource-group nlweb-rg
```

Your NLWeb will be live at: `https://harithkavish-nlweb.azurewebsites.net`

### Option B: Deploy to Render (Free Tier)

1. Go to [render.com](https://render.com)
2. Create a new **Web Service**
3. Connect your GitHub repo (fork NLWeb first)
4. Settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn code.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables from your `.env`
6. Deploy!

### Option C: Deploy to Railway

1. Go to [railway.app](https://railway.app)
2. Create new project from GitHub repo
3. Add environment variables
4. Deploy automatically

### Option D: Run with Docker

```powershell
# Build the image
docker build -t harithkavish-nlweb .

# Run the container
docker run -p 8000:8000 -e OPENAI_API_KEY=your_key harithkavish-nlweb
```

---

## Step 10: Add NLWeb to Your Portfolio Website

Once deployed, let me know your deployment URL and I'll:
1. Add it to your "My Applications" section
2. Add a status check endpoint
3. Update your schema.org and sitemap
4. Add it to the BreadcrumbList

### Example entry:
```html
<a href="https://harithkavish-nlweb.azurewebsites.net/" class="footer-btn" id="nlweb-btn">
    <span class="status-dot" id="nlweb-status-dot"></span>
    NLWeb Assistant
</a>
```

---

## Next Steps After Deployment

1. **Customize the UI**: Modify `static/` folder for your branding
2. **Add more data**: Ingest your GitHub repos, blog posts, etc.
3. **Connect to live databases**: Instead of vector stores, connect directly to your databases
4. **Add authentication**: Protect your API if needed
5. **Enable MCP**: Allow AI agents to query your site

---

## Useful Resources

- **GitHub Repo**: [github.com/nlweb-ai/NLWeb](https://github.com/nlweb-ai/NLWeb)
- **Documentation**: Check the `docs/` folder in the repo
- **REST API Docs**: [NLWeb REST API](https://github.com/nlweb-ai/NLWeb/blob/main/docs/REST_API.md)
- **Microsoft Announcement**: [Microsoft Build 2025 - NLWeb](https://blogs.microsoft.com/blog/2025/05/19/microsoft-build-2025-the-age-of-ai-agents-and-building-the-open-agentic-web/)

---

## Quick Start Commands Summary

```powershell
# 1. Clone and setup
cd C:\Dev\GitHub
git clone https://github.com/nlweb-ai/NLWeb.git
cd NLWeb
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2. Configure
copy .env.template .env
# Edit .env with your API keys

# 3. Start Qdrant (in another terminal)
docker run -p 6333:6333 qdrant/qdrant

# 4. Start NLWeb
python start_server_debug.py

# 5. Open browser
# http://localhost:8000
```

---

## Troubleshooting

### Port already in use:
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with actual number)
taskkill /PID <PID> /F
```

### Python package conflicts:
```powershell
# Clear pip cache
pip cache purge

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Qdrant connection error:
```powershell
# Check if Qdrant is running
curl http://localhost:6333/collections
```

---

## Questions or Issues?

Once you've deployed, share:
1. Your deployment URL
2. Any errors you encountered
3. What type of data you want to make queryable

I'll help you integrate it into your portfolio website! 🚀

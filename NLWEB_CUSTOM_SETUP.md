# NLWeb Custom Setup Guide
## Using MongoDB Atlas + Local AI Models

Perfect! Your setup is ideal for a **free, self-hosted** NLWeb implementation.

---

## 🎯 Your Tech Stack

```
┌─────────────────────────────────────────────────────┐
│              YOUR NLWEB ARCHITECTURE                │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Frontend (Web UI) ──► NLWeb Backend               │
│                              │                      │
│                              ├──► Local AI Model   │
│                              │     (Llama, Mistral) │
│                              │                      │
│                              └──► MongoDB Atlas     │
│                                    (Vector Store)   │
│                                                     │
└─────────────────────────────────────────────────────┘

Benefits:
✅ Free (no API costs)
✅ Fast (local processing)
✅ Private (data stays with you)
✅ Scalable (MongoDB Atlas free tier: 512MB)
```

---

## 📦 Prerequisites Check

### 1. MongoDB Atlas Setup
```
✓ Account created at mongodb.com
✓ Free tier cluster (M0) provisioned
✓ Connection string available
✓ Vector Search enabled (Atlas Search required)
```

### 2. Local AI Model
What model are you running?
- **Ollama** (easiest - recommended)
- **LM Studio**
- **LocalAI**
- **llama.cpp**
- **Text Generation WebUI**

---

## 🚀 Quick Setup Path

### Step 1: Install & Configure Ollama (Recommended)

If you don't have Ollama yet:

```powershell
# Download Ollama for Windows
# Visit: https://ollama.ai/download

# After installation, pull a good model
ollama pull llama3.2:3b         # Fast, 2GB
# OR
ollama pull mistral:7b          # Better quality, 4GB
# OR
ollama pull llama3.1:8b         # Best for NLWeb, 4.7GB

# Test it
ollama run llama3.2:3b
>>> Hello! (type /bye to exit)
```

### Step 2: Get Your MongoDB Atlas Connection String

```
1. Go to: https://cloud.mongodb.com
2. Click "Connect" on your cluster
3. Choose "Connect your application"
4. Copy connection string:

mongodb+srv://username:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority

Replace <password> with your actual password
```

### Step 3: Clone NLWeb Repository

```powershell
cd C:\Dev\GitHub
git clone https://github.com/nlweb-ai/NLWeb.git
cd NLWeb
```

### Step 4: Create Virtual Environment

```powershell
# Create venv
python -m venv venv

# Activate
.\venv\Scripts\Activate.ps1

# If execution policy error:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Install dependencies
pip install -r requirements.txt

# Install MongoDB support
pip install pymongo motor dnspython

# Install Ollama support
pip install ollama
```

### Step 5: Configure NLWeb for Your Setup

Create `.env` file:

```env
# ===================================
# LLM Configuration (Local Ollama)
# ===================================
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
# OR use: mistral:7b, llama3.1:8b, phi3:mini

# ===================================
# Vector Store (MongoDB Atlas)
# ===================================
VECTOR_STORE=mongodb
MONGODB_URI=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
MONGODB_DATABASE=nlweb
MONGODB_COLLECTION=portfolio_vectors

# Enable Atlas Vector Search
MONGODB_VECTOR_SEARCH=true
MONGODB_INDEX_NAME=vector_index

# ===================================
# Embedding Model (Local or API)
# ===================================
# Option A: Use Ollama for embeddings too (FREE)
EMBEDDING_PROVIDER=ollama
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

# Option B: Use OpenAI embeddings (better quality, small cost)
# EMBEDDING_PROVIDER=openai
# OPENAI_API_KEY=sk-...
# EMBEDDING_MODEL=text-embedding-3-small

# ===================================
# Server Configuration
# ===================================
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
DEBUG=true

# ===================================
# Optional: Fallback to API
# ===================================
# If local model is slow, fallback to cloud
ENABLE_FALLBACK=false
# FALLBACK_LLM_PROVIDER=openai
# OPENAI_API_KEY=sk-...
```

### Step 6: Set Up MongoDB Atlas Vector Search

You need to create a Vector Search index in Atlas:

```json
// In MongoDB Atlas UI:
// 1. Go to your cluster → "Search" tab
// 2. Click "Create Search Index"
// 3. Choose "JSON Editor"
// 4. Use this configuration:

{
  "mappings": {
    "dynamic": true,
    "fields": {
      "embedding": {
        "type": "knnVector",
        "dimensions": 768,
        "similarity": "cosine"
      },
      "text": {
        "type": "string"
      },
      "metadata": {
        "type": "document",
        "dynamic": true
      }
    }
  }
}

// Index name: vector_index
// Database: nlweb
// Collection: portfolio_vectors
```

**Important:** 
- If using Ollama embeddings (`nomic-embed-text`): dimensions = 768
- If using OpenAI `text-embedding-3-small`: dimensions = 1536
- If using OpenAI `text-embedding-ada-002`: dimensions = 1536

### Step 7: Install Ollama Embedding Model

```powershell
# Pull the embedding model
ollama pull nomic-embed-text

# Test it
ollama run nomic-embed-text "Hello world"
```

### Step 8: Prepare Your Portfolio Data

Create `my_portfolio_data.jsonl`:

```jsonl
{"@type":"Person","@id":"https://harithkavish.github.io/","name":"Harith Kavish","jobTitle":"AI Developer","description":"Full-Stack Engineer and AI Developer specializing in machine learning, deep learning, and computer vision","url":"https://harithkavish.github.io/","sameAs":["https://github.com/HarithKavish","https://www.linkedin.com/in/harithkavish/","https://x.com/harithkavish"]}
{"@type":"SoftwareApplication","name":"SkinNet Analyzer","applicationCategory":"HealthApplication","description":"AI-powered skin condition detection and analysis using deep learning and convolutional neural networks. Provides real-time skin health assessment.","url":"https://harithkavish.github.io/SkinNet-Analyzer/","offers":{"@type":"Offer","price":"0","priceCurrency":"USD"},"operatingSystem":"Web","applicationSubCategory":"Medical AI"}
{"@type":"SoftwareApplication","name":"Object Detector","applicationCategory":"MultimediaApplication","description":"Multi-object detection application using YOLO (You Only Look Once) algorithm for real-time object recognition and classification.","url":"https://harithkavish.github.io/Multi-Object-Detection-using-YOLO/","offers":{"@type":"Offer","price":"0","priceCurrency":"USD"},"operatingSystem":"Web","applicationSubCategory":"Computer Vision"}
{"@type":"WebSite","name":"Harith Kavish Portfolio","url":"https://harithkavish.github.io/","description":"Portfolio website showcasing AI projects, machine learning applications, and full-stack development work by Harith Kavish","author":{"@type":"Person","name":"Harith Kavish"}}
```

### Step 9: Custom Ingestion Script for MongoDB

Create `ingest_to_mongodb.py`:

```python
import os
import json
from pymongo import MongoClient
from ollama import Client as OllamaClient
from dotenv import load_dotenv

load_dotenv()

# MongoDB connection
mongo_uri = os.getenv('MONGODB_URI')
client = MongoClient(mongo_uri)
db = client[os.getenv('MONGODB_DATABASE', 'nlweb')]
collection = db[os.getenv('MONGODB_COLLECTION', 'portfolio_vectors')]

# Ollama for embeddings
ollama = OllamaClient(host=os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434'))
embedding_model = os.getenv('OLLAMA_EMBEDDING_MODEL', 'nomic-embed-text')

def get_embedding(text):
    """Generate embedding using Ollama"""
    response = ollama.embeddings(model=embedding_model, prompt=text)
    return response['embedding']

def ingest_jsonl(file_path):
    """Ingest JSONL file into MongoDB with embeddings"""
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line)
            
            # Create searchable text from Schema.org data
            text_parts = []
            if 'name' in data:
                text_parts.append(data['name'])
            if 'description' in data:
                text_parts.append(data['description'])
            if 'jobTitle' in data:
                text_parts.append(data['jobTitle'])
            
            text = ' '.join(text_parts)
            
            # Generate embedding
            print(f"Generating embedding for: {data.get('name', 'Unknown')}")
            embedding = get_embedding(text)
            
            # Prepare document
            document = {
                'text': text,
                'embedding': embedding,
                'metadata': data,
                '@type': data.get('@type', 'Thing')
            }
            
            # Insert into MongoDB
            collection.insert_one(document)
            print(f"✓ Inserted: {data.get('name', 'Unknown')}")

if __name__ == '__main__':
    print("Starting ingestion...")
    ingest_jsonl('my_portfolio_data.jsonl')
    print(f"\n✅ Ingestion complete! Total documents: {collection.count_documents({})}")
```

Run it:

```powershell
python ingest_to_mongodb.py
```

### Step 10: Modify NLWeb to Use Your Setup

NLWeb needs to be configured to use MongoDB and Ollama. Check if the repo supports these natively, or you may need to modify:

**File: `code/config.py`** (or similar)

```python
import os
from ollama import Client as OllamaClient
from pymongo import MongoClient

# Ollama configuration
OLLAMA_CLIENT = OllamaClient(host=os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434'))
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama3.2:3b')

# MongoDB configuration
MONGO_CLIENT = MongoClient(os.getenv('MONGODB_URI'))
MONGO_DB = MONGO_CLIENT[os.getenv('MONGODB_DATABASE', 'nlweb')]
MONGO_COLLECTION = MONGO_DB[os.getenv('MONGODB_COLLECTION', 'portfolio_vectors')]
```

**File: `code/llm_provider.py`** (create if needed)

```python
from ollama import Client

class OllamaLLMProvider:
    def __init__(self, base_url, model):
        self.client = Client(host=base_url)
        self.model = model
    
    def generate(self, prompt, max_tokens=500):
        response = self.client.generate(
            model=self.model,
            prompt=prompt,
            options={'num_predict': max_tokens}
        )
        return response['response']
    
    def chat(self, messages):
        response = self.client.chat(
            model=self.model,
            messages=messages
        )
        return response['message']['content']
```

**File: `code/vector_search.py`** (create if needed)

```python
from pymongo import MongoClient
from ollama import Client as OllamaClient
import os

class MongoDBVectorSearch:
    def __init__(self):
        self.mongo_client = MongoClient(os.getenv('MONGODB_URI'))
        self.db = self.mongo_client[os.getenv('MONGODB_DATABASE', 'nlweb')]
        self.collection = self.db[os.getenv('MONGODB_COLLECTION', 'portfolio_vectors')]
        self.ollama = OllamaClient(host=os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434'))
        self.embedding_model = os.getenv('OLLAMA_EMBEDDING_MODEL', 'nomic-embed-text')
    
    def search(self, query, limit=5):
        # Generate query embedding
        query_embedding = self.ollama.embeddings(
            model=self.embedding_model,
            prompt=query
        )['embedding']
        
        # Vector search using Atlas Search
        pipeline = [
            {
                "$search": {
                    "knnBeta": {
                        "vector": query_embedding,
                        "path": "embedding",
                        "k": limit
                    }
                }
            },
            {
                "$project": {
                    "metadata": 1,
                    "text": 1,
                    "score": {"$meta": "searchScore"}
                }
            }
        ]
        
        results = list(self.collection.aggregate(pipeline))
        return results
```

### Step 11: Test Locally

```powershell
# Make sure Ollama is running
ollama serve

# In another terminal, activate venv and start NLWeb
cd C:\Dev\GitHub\NLWeb
.\venv\Scripts\Activate.ps1
python start_server_debug.py

# Or use uvicorn directly
uvicorn code.main:app --host 0.0.0.0 --port 8000 --reload
```

Open: http://localhost:8000

Test queries:
- "What projects does Harith have?"
- "Tell me about AI health applications"
- "Show me computer vision projects"

### Step 12: Monitor & Debug

```powershell
# Check Ollama logs
ollama list  # See loaded models
ollama ps    # See running models

# Check MongoDB
# Go to Atlas UI → Collections → Browse data
# You should see your vectors in portfolio_vectors

# Check NLWeb logs
# Terminal output will show:
# - Query received
# - Embedding generated
# - Vector search results
# - LLM response
```

---

## 📊 Performance Optimization

### Ollama Model Recommendations

| Model | Size | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| **llama3.2:3b** | 2GB | ⚡⚡⚡ | ⭐⭐⭐ | Testing, fast responses |
| **mistral:7b** | 4GB | ⚡⚡ | ⭐⭐⭐⭐ | Balanced |
| **llama3.1:8b** | 4.7GB | ⚡⚡ | ⭐⭐⭐⭐⭐ | Production (recommended) |
| **phi3:mini** | 2.3GB | ⚡⚡⚡ | ⭐⭐⭐ | Resource constrained |

### MongoDB Atlas Limits (Free Tier)

```
Storage: 512 MB (plenty for your portfolio)
RAM: 512 MB shared
Connections: 500 max
Vector Search: ✅ Supported
Estimated capacity: ~100,000 documents with embeddings
```

### Speed Comparison

```
Cloud API (OpenAI):
└─► 1-3 seconds per query (network + API processing)

Your Local Setup:
├─► Embedding: ~0.2s (Ollama local)
├─► Vector search: ~0.1s (MongoDB Atlas)
├─► LLM response: ~2-5s (Ollama local, depends on model)
└─► Total: ~2-6 seconds

With GPU:
└─► LLM response: ~0.5-2s (much faster!)
```

---

## 🚀 Deployment Options

### Option 1: Deploy NLWeb Backend Only

```
Backend (NLWeb + Ollama):
├─► VPS/Cloud VM (e.g., DigitalOcean, Linode)
├─► Docker container with Ollama + NLWeb
└─► MongoDB Atlas (already cloud-hosted)

Frontend:
└─► Keep on GitHub Pages (harithkavish.github.io)
    └─► Embed chat widget pointing to backend
```

### Option 2: Full Local Development, Cloud Deployment

```
Development: Local (your laptop)
Production: 
├─► Backend: Railway/Render (free tier)
│   └─► May need to use cloud LLM (Ollama needs GPU/RAM)
└─► MongoDB: Atlas (already cloud)
```

### Option 3: Hybrid Setup (Recommended)

```
Local (Development):
├─► Ollama (local)
├─► NLWeb (local)
└─► MongoDB Atlas (cloud)

Production (Deployment):
├─► NLWeb backend: Render/Railway
├─► LLM: OpenAI API (small cost) OR Azure OpenAI (free credits)
└─► MongoDB Atlas (cloud)
```

---

## 💰 Cost Analysis

### Your Current Setup (Local Dev):

```
Ollama: FREE ✅
MongoDB Atlas (M0): FREE ✅
NLWeb: FREE (open source) ✅

Total: $0/month
```

### Production Deployment Costs:

```
Option A: All Free
├─► Backend: Render free tier
├─► LLM: Ollama on VPS ($5-10/month for small VPS)
└─► MongoDB: Atlas free tier
Total: $5-10/month

Option B: Hybrid
├─► Backend: Render free tier
├─► LLM: OpenAI API (~$0.50-2/month for light use)
└─► MongoDB: Atlas free tier
Total: $0.50-2/month

Option C: Premium
├─► Backend: Railway/Render paid ($7/month)
├─► LLM: OpenAI GPT-4 ($5-10/month)
└─► MongoDB: Atlas M2 ($9/month)
Total: $21-26/month (unnecessary for portfolio)
```

**Recommendation:** Start with local setup (FREE), deploy to Render + OpenAI API when ready ($0.50-2/month)

---

## 🎯 Next Steps

1. **Install Ollama** (if not already)
2. **Pull a model**: `ollama pull llama3.1:8b`
3. **Get MongoDB Atlas connection string**
4. **Clone NLWeb repo**
5. **Create .env with your settings**
6. **Set up Vector Search index in Atlas**
7. **Create your portfolio data file**
8. **Run ingestion script**
9. **Test locally**
10. **Let me know when ready to integrate with your website!**

---

## 📞 Integration With Your Portfolio

Once your NLWeb is running, I can help you:

1. **Add it to your website** as a new application button
2. **Create a status check** to show if it's online
3. **Update schema.org** with your NLWeb endpoint
4. **Add it to sitemap** and breadcrumbs
5. **Embed a chat widget** (optional) on your main page

---

## ❓ Questions?

Let me know:
- Which Ollama model did you install?
- Do you have MongoDB Atlas set up already?
- Do you need help with any specific configuration?
- Ready to start the setup?

I'm here to guide you through each step! 🚀

# 🚀 NLWeb Quick Start Guide

I've created everything you need! Follow these steps:

## ✅ Files Created:

1. **nlweb_setup.ps1** - Automated setup script
2. **nlweb_env_template.txt** - Configuration template
3. **portfolio_data.jsonl** - Your portfolio data (ready to ingest)
4. **nlweb_setup_mongodb.py** - MongoDB setup helper
5. **nlweb_ingest_data.py** - Data ingestion script

---

## 📋 Step-by-Step Instructions

### Step 1: Run the Setup Script

Open PowerShell and run:

```powershell
cd C:\Dev\GitHub\harithkavish_github_io
.\nlweb_setup.ps1
```

This will:
- Clone NLWeb repository
- Create virtual environment
- Install all dependencies
- Download required Ollama models (if needed)

**Note:** If you get an execution policy error:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

### Step 2: Configure MongoDB Connection

1. Get your MongoDB Atlas connection string:
   - Go to: https://cloud.mongodb.com
   - Click "Connect" on your cluster
   - Choose "Connect your application"
   - Copy the connection string

2. Edit the configuration file:
   ```powershell
   notepad C:\Dev\GitHub\NLWeb\.env
   ```

3. Replace this line:
   ```
   MONGODB_URI=mongodb+srv://YOUR_USERNAME:YOUR_PASSWORD@cluster0.xxxxx.mongodb.net/...
   ```
   
   With your actual connection string:
   ```
   MONGODB_URI=mongodb+srv://harith:yourpassword@cluster0.abc123.mongodb.net/?retryWrites=true&w=majority
   ```

4. Save and close

---

### Step 3: Setup MongoDB Atlas Vector Index

Run:
```powershell
cd C:\Dev\GitHub\harithkavish_github_io
python nlweb_setup_mongodb.py
```

This will:
- Test your MongoDB connection
- Create the database and collection
- Show you how to create the Vector Search Index

**Follow the instructions** it displays to create the index in MongoDB Atlas UI.

---

### Step 4: Ingest Your Portfolio Data

Run:
```powershell
python nlweb_ingest_data.py
```

This will:
- Connect to Ollama (make sure it's running!)
- Generate embeddings for your portfolio data
- Upload everything to MongoDB Atlas

**Time estimate:** 2-3 minutes (depending on your internet speed)

---

### Step 5: Start NLWeb Server

```powershell
cd C:\Dev\GitHub\NLWeb
.\venv\Scripts\Activate.ps1
python start_server_debug.py
```

Or:
```powershell
uvicorn code.main:app --host 0.0.0.0 --port 8000 --reload
```

---

### Step 6: Test It!

1. Open your browser: http://localhost:8000

2. Try these queries:
   - "What projects does Harith have?"
   - "Tell me about AI health applications"
   - "What are Harith's skills?"
   - "Show me computer vision projects"

---

## 🔧 Troubleshooting

### Ollama not running:
```powershell
ollama serve
```

### Can't find models:
```powershell
ollama list
ollama pull llama3.2:3b
ollama pull nomic-embed-text
```

### MongoDB connection error:
- Check your connection string
- Make sure your IP is whitelisted in MongoDB Atlas
- Go to: Network Access → Add IP Address → Add Current IP

### Port 8000 already in use:
```powershell
# Find and kill the process
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

---

## 📊 What Gets Created

```
C:\Dev\GitHub\
├── harithkavish_github_io\
│   ├── nlweb_setup.ps1           ← Setup script
│   ├── nlweb_env_template.txt    ← Config template
│   ├── nlweb_setup_mongodb.py    ← MongoDB helper
│   ├── nlweb_ingest_data.py      ← Data ingestion
│   └── portfolio_data.jsonl      ← Your data
│
└── NLWeb\                        ← NLWeb repository
    ├── .env                      ← Your config (created by script)
    ├── venv\                     ← Python environment
    ├── code\                     ← NLWeb source code
    └── start_server_debug.py     ← Server starter
```

---

## 🎯 Expected Results

After ingestion, you should have:
- **6 documents** in MongoDB with embeddings
- Vector search index configured
- NLWeb server responding to queries
- Natural language interface to your portfolio

---

## 🚀 Ready to Start?

Run this now:
```powershell
cd C:\Dev\GitHub\harithkavish_github_io
.\nlweb_setup.ps1
```

Then follow Steps 2-6 above!

Let me know if you hit any errors or need help! 🎯

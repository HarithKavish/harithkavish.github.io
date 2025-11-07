# NLWeb Quick Setup Script
# Run this in PowerShell to set up NLWeb with Ollama + MongoDB Atlas

Write-Host "🚀 NLWeb Setup Script - Starting..." -ForegroundColor Cyan
Write-Host ""

# Step 1: Clone NLWeb repository
Write-Host "Step 1: Cloning NLWeb repository..." -ForegroundColor Yellow
cd C:\Dev\GitHub
if (Test-Path "NLWeb") {
    Write-Host "✓ NLWeb directory already exists. Updating..." -ForegroundColor Green
    cd NLWeb
    git pull
} else {
    git clone https://github.com/nlweb-ai/NLWeb.git
    cd NLWeb
}
Write-Host "✓ Repository ready!" -ForegroundColor Green
Write-Host ""

# Step 2: Create virtual environment
Write-Host "Step 2: Creating Python virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "✓ Virtual environment already exists" -ForegroundColor Green
} else {
    python -m venv venv
    Write-Host "✓ Virtual environment created!" -ForegroundColor Green
}
Write-Host ""

# Step 3: Activate virtual environment
Write-Host "Step 3: Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1
Write-Host "✓ Virtual environment activated!" -ForegroundColor Green
Write-Host ""

# Step 4: Install dependencies
Write-Host "Step 4: Installing dependencies..." -ForegroundColor Yellow
Write-Host "This may take a few minutes..." -ForegroundColor Gray
pip install --upgrade pip
pip install -r requirements.txt
pip install pymongo motor ollama dnspython python-dotenv
Write-Host "✓ All dependencies installed!" -ForegroundColor Green
Write-Host ""

# Step 5: Check Ollama models
Write-Host "Step 5: Checking Ollama models..." -ForegroundColor Yellow
Write-Host "Available models:" -ForegroundColor Cyan
ollama list
Write-Host ""

# Step 6: Pull required models if needed
Write-Host "Step 6: Ensuring required models are available..." -ForegroundColor Yellow
$models = ollama list | Select-String -Pattern "llama|mistral|phi|gemma"
if ($models) {
    Write-Host "✓ LLM models found!" -ForegroundColor Green
} else {
    Write-Host "Downloading lightweight model (llama3.2:3b - 2GB)..." -ForegroundColor Yellow
    ollama pull llama3.2:3b
}

# Check for embedding model
$embedding = ollama list | Select-String -Pattern "nomic-embed-text"
if ($embedding) {
    Write-Host "✓ Embedding model found!" -ForegroundColor Green
} else {
    Write-Host "Downloading embedding model (nomic-embed-text - 274MB)..." -ForegroundColor Yellow
    ollama pull nomic-embed-text
}
Write-Host ""

# Step 7: Create .env file
Write-Host "Step 7: Creating configuration file..." -ForegroundColor Yellow
Write-Host "⚠️  You need to add your MongoDB Atlas connection string!" -ForegroundColor Red
Write-Host ""
Write-Host "The .env file has been created at: C:\Dev\GitHub\NLWeb\.env" -ForegroundColor Cyan
Write-Host ""

Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Edit .env and add your MongoDB connection string" -ForegroundColor White
Write-Host "2. Run: python C:\Dev\GitHub\harithkavish_github_io\nlweb_setup_mongodb.py" -ForegroundColor White
Write-Host "3. Run: python C:\Dev\GitHub\harithkavish_github_io\nlweb_ingest_data.py" -ForegroundColor White
Write-Host "4. Run: python start_server_debug.py" -ForegroundColor White
Write-Host ""

# Hugging Face Spaces Deployment Script for NLWeb Portfolio Chat
Write-Host "🚀 Preparing deployment to Hugging Face Spaces..." -ForegroundColor Green

# Check if git is configured
$gitUser = git config user.name 2>$null
if (-not $gitUser) {
    Write-Host "❌ Git user not configured. Please run:" -ForegroundColor Red
    Write-Host "git config --global user.name 'Your Name'" -ForegroundColor Yellow
    Write-Host "git config --global user.email 'your.email@example.com'" -ForegroundColor Yellow
    exit 1
}

# Create deployment directory
$deployDir = "nlweb-hf-deployment"
if (Test-Path $deployDir) {
    Remove-Item -Recurse -Force $deployDir
}
New-Item -ItemType Directory -Path $deployDir | Out-Null
Set-Location $deployDir

# Initialize git repository
git init
git branch -M main

# Copy necessary files
Copy-Item "../app.py" .
Copy-Item "../requirements.txt" .
Copy-Item "../Dockerfile" .
Copy-Item "../README.md" .
Copy-Item "../.env.example" ".env"

Write-Host "✅ Files copied to deployment directory" -ForegroundColor Green

# Create gitignore
@"
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
ENV/
env.bak/
venv.bak/
.pytest_cache/
.coverage
htmlcov/
.tox/
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.DS_Store
.vscode/
"@ | Out-File -FilePath ".gitignore" -Encoding UTF8

Write-Host ""
Write-Host "📝 Instructions for deployment:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Go to https://huggingface.co/new-space" -ForegroundColor White
Write-Host "2. Create a new Space with these settings:" -ForegroundColor White
Write-Host "   - Owner: HarithKavish (or your username)" -ForegroundColor Gray
Write-Host "   - Space name: nlweb-portfolio-chat" -ForegroundColor Gray
Write-Host "   - License: MIT" -ForegroundColor Gray
Write-Host "   - SDK: Docker" -ForegroundColor Gray
Write-Host "   - Hardware: CPU basic (free tier)" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Clone the Space repository:" -ForegroundColor White
Write-Host "   git clone https://huggingface.co/spaces/HarithKavish/nlweb-portfolio-chat" -ForegroundColor Yellow
Write-Host ""
Write-Host "4. Copy the files from this deployment directory to the cloned Space" -ForegroundColor White
Write-Host ""
Write-Host "5. Update the .env file with your MongoDB credentials" -ForegroundColor White
Write-Host ""
Write-Host "6. Commit and push:" -ForegroundColor White
Write-Host "   git add ." -ForegroundColor Yellow
Write-Host "   git commit -m 'Initial deployment of NLWeb Portfolio Chat'" -ForegroundColor Yellow
Write-Host "   git push" -ForegroundColor Yellow
Write-Host ""
Write-Host "📍 The deployment files are ready in: $(Get-Location)" -ForegroundColor Magenta

# Optional: Open the deployment directory in Explorer
$openExplorer = Read-Host "Open deployment directory in Explorer? (y/n)"
if ($openExplorer -eq 'y' -or $openExplorer -eq 'Y') {
    Invoke-Item .
}
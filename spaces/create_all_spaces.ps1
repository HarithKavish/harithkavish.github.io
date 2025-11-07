# PowerShell Script to Create All HuggingFace Spaces
# Multi-Agent Portfolio Chatbot Architecture

Write-Host "🚀 Multi-Agent Chatbot - HuggingFace Spaces Creator" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host ""

# Check if HuggingFace CLI is installed
Write-Host "📋 Checking prerequisites..." -ForegroundColor Yellow
$hfCliInstalled = Get-Command huggingface-cli -ErrorAction SilentlyContinue

if (-not $hfCliInstalled) {
    Write-Host "❌ HuggingFace CLI not found!" -ForegroundColor Red
    Write-Host "   Install it with: pip install huggingface-hub" -ForegroundColor Yellow
    exit 1
}

# Check if logged in to HuggingFace
Write-Host "🔑 Checking HuggingFace authentication..." -ForegroundColor Yellow
$whoami = huggingface-cli whoami 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Not logged in to HuggingFace!" -ForegroundColor Red
    Write-Host "   Login with: huggingface-cli login" -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ Logged in as: $whoami" -ForegroundColor Green
Write-Host ""

# Define all spaces
$spaces = @(
    @{Name="perception-layer"; Path="spaces/perception-layer"; Description="Embeddings & NLU"},
    @{Name="memory-layer"; Path="spaces/memory-layer"; Description="Vector DB & History"},
    @{Name="reasoning-layer"; Path="spaces/reasoning-layer"; Description="LLM Generation"},
    @{Name="execution-layer"; Path="spaces/execution-layer"; Description="Tool Calling"},
    @{Name="monitoring-safety"; Path="spaces/monitoring-safety"; Description="Safety & Monitoring"}
)

Write-Host "📦 Creating $($spaces.Count) HuggingFace Spaces..." -ForegroundColor Cyan
Write-Host ""

$username = "harithkavish"  # Change this to your HF username if different

foreach ($space in $spaces) {
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
    Write-Host "📦 Creating: $($space.Name)" -ForegroundColor Cyan
    Write-Host "   Description: $($space.Description)" -ForegroundColor Gray
    
    $spacePath = $space.Path
    $spaceName = $space.Name
    
    # Check if directory exists
    if (-not (Test-Path $spacePath)) {
        Write-Host "   ❌ Directory not found: $spacePath" -ForegroundColor Red
        continue
    }
    
    # Navigate to space directory
    Push-Location $spacePath
    
    try {
        # Create Dockerfile if it doesn't exist
        if (-not (Test-Path "Dockerfile")) {
            Write-Host "   📝 Creating Dockerfile..." -ForegroundColor Yellow
            
            $dockerfile = @"
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
$(if (Test-Path "README.md") { "COPY README.md ." })

EXPOSE 7860

CMD ["python", "app.py"]
"@
            Set-Content -Path "Dockerfile" -Value $dockerfile
        }
        
        # Initialize git if not already
        if (-not (Test-Path ".git")) {
            Write-Host "   🔧 Initializing git repository..." -ForegroundColor Yellow
            git init | Out-Null
            git add . | Out-Null
            git commit -m "Initial $spaceName implementation" | Out-Null
        }
        
        # Create HuggingFace Space
        Write-Host "   🚀 Creating HuggingFace Space..." -ForegroundColor Yellow
        $createOutput = huggingface-cli repo create $spaceName --type space --space_sdk docker --org $username 2>&1
        
        if ($LASTEXITCODE -ne 0) {
            if ($createOutput -match "already exists") {
                Write-Host "   ⚠️  Space already exists, will update it" -ForegroundColor Yellow
            } else {
                Write-Host "   ❌ Failed to create Space: $createOutput" -ForegroundColor Red
                Pop-Location
                continue
            }
        }
        
        # Add remote if not already added
        $remoteUrl = "https://huggingface.co/spaces/$username/$spaceName"
        $existingRemote = git remote get-url origin 2>&1
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "   🔗 Adding remote origin..." -ForegroundColor Yellow
            git remote add origin $remoteUrl | Out-Null
        } else {
            Write-Host "   🔗 Updating remote origin..." -ForegroundColor Yellow
            git remote set-url origin $remoteUrl | Out-Null
        }
        
        # Push to HuggingFace
        Write-Host "   📤 Pushing to HuggingFace Space..." -ForegroundColor Yellow
        git branch -M main | Out-Null
        $pushOutput = git push origin main --force 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✓ Space created successfully!" -ForegroundColor Green
            Write-Host "   🔗 URL: https://huggingface.co/spaces/$username/$spaceName" -ForegroundColor Cyan
        } else {
            Write-Host "   ❌ Push failed: $pushOutput" -ForegroundColor Red
        }
        
    }
    catch {
        Write-Host "   ❌ Error: $_" -ForegroundColor Red
    }
    finally {
        Pop-Location
    }
    
    Write-Host ""
    Start-Sleep -Seconds 2
}

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""
Write-Host "✅ Space creation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Configure secrets for each Space in HuggingFace UI" -ForegroundColor White
Write-Host "2. Wait for Spaces to build (~5-15 minutes each)" -ForegroundColor White
Write-Host "3. Verify health endpoints" -ForegroundColor White
Write-Host "4. Update orchestrator with service URLs" -ForegroundColor White
Write-Host ""
Write-Host "🔗 Your Spaces:" -ForegroundColor Cyan
foreach ($space in $spaces) {
    Write-Host "   • https://huggingface.co/spaces/$username/$($space.Name)" -ForegroundColor Gray
}
Write-Host ""
Write-Host "📚 See CREATE_SPACES_GUIDE.md for configuration details" -ForegroundColor Yellow
Write-Host ""

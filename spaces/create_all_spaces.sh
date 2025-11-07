#!/bin/bash
# Bash Script to Create All HuggingFace Spaces
# Multi-Agent Portfolio Chatbot Architecture

set -e

echo "🚀 Multi-Agent Chatbot - HuggingFace Spaces Creator"
echo "================================================="
echo ""

# Check if HuggingFace CLI is installed
echo "📋 Checking prerequisites..."
if ! command -v huggingface-cli &> /dev/null; then
    echo "❌ HuggingFace CLI not found!"
    echo "   Install it with: pip install huggingface-hub"
    exit 1
fi

# Check if logged in to HuggingFace
echo "🔑 Checking HuggingFace authentication..."
if ! huggingface-cli whoami &> /dev/null; then
    echo "❌ Not logged in to HuggingFace!"
    echo "   Login with: huggingface-cli login"
    exit 1
fi

WHOAMI=$(huggingface-cli whoami)
echo "✓ Logged in as: $WHOAMI"
echo ""

# Define all spaces
USERNAME="harithkavish"  # Change this to your HF username if different

declare -a SPACES=(
    "perception-layer:spaces/perception-layer:Embeddings & NLU"
    "memory-layer:spaces/memory-layer:Vector DB & History"
    "reasoning-layer:spaces/reasoning-layer:LLM Generation"
    "execution-layer:spaces/execution-layer:Tool Calling"
    "monitoring-safety:spaces/monitoring-safety:Safety & Monitoring"
)

echo "📦 Creating ${#SPACES[@]} HuggingFace Spaces..."
echo ""

for SPACE_INFO in "${SPACES[@]}"; do
    IFS=':' read -r SPACE_NAME SPACE_PATH DESCRIPTION <<< "$SPACE_INFO"
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📦 Creating: $SPACE_NAME"
    echo "   Description: $DESCRIPTION"
    
    # Check if directory exists
    if [ ! -d "$SPACE_PATH" ]; then
        echo "   ❌ Directory not found: $SPACE_PATH"
        continue
    fi
    
    # Navigate to space directory
    cd "$SPACE_PATH"
    
    # Create Dockerfile if it doesn't exist
    if [ ! -f "Dockerfile" ]; then
        echo "   📝 Creating Dockerfile..."
        
        cat > Dockerfile << 'EOF'
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
EOF
        
        if [ -f "README.md" ]; then
            echo "COPY README.md ." >> Dockerfile
        fi
        
        cat >> Dockerfile << 'EOF'

EXPOSE 7860

CMD ["python", "app.py"]
EOF
    fi
    
    # Initialize git if not already
    if [ ! -d ".git" ]; then
        echo "   🔧 Initializing git repository..."
        git init > /dev/null 2>&1
        git add . > /dev/null 2>&1
        git commit -m "Initial $SPACE_NAME implementation" > /dev/null 2>&1
    fi
    
    # Create HuggingFace Space
    echo "   🚀 Creating HuggingFace Space..."
    if huggingface-cli repo create "$SPACE_NAME" --type space --space_sdk docker --org "$USERNAME" 2>&1 | grep -q "already exists"; then
        echo "   ⚠️  Space already exists, will update it"
    fi
    
    # Add remote if not already added
    REMOTE_URL="https://huggingface.co/spaces/$USERNAME/$SPACE_NAME"
    
    if ! git remote get-url origin > /dev/null 2>&1; then
        echo "   🔗 Adding remote origin..."
        git remote add origin "$REMOTE_URL" > /dev/null 2>&1
    else
        echo "   🔗 Updating remote origin..."
        git remote set-url origin "$REMOTE_URL" > /dev/null 2>&1
    fi
    
    # Push to HuggingFace
    echo "   📤 Pushing to HuggingFace Space..."
    git branch -M main > /dev/null 2>&1
    
    if git push origin main --force > /dev/null 2>&1; then
        echo "   ✓ Space created successfully!"
        echo "   🔗 URL: https://huggingface.co/spaces/$USERNAME/$SPACE_NAME"
    else
        echo "   ❌ Push failed"
    fi
    
    # Go back to root directory
    cd - > /dev/null
    
    echo ""
    sleep 2
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ Space creation complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Configure secrets for each Space in HuggingFace UI"
echo "2. Wait for Spaces to build (~5-15 minutes each)"
echo "3. Verify health endpoints"
echo "4. Update orchestrator with service URLs"
echo ""
echo "🔗 Your Spaces:"
for SPACE_INFO in "${SPACES[@]}"; do
    IFS=':' read -r SPACE_NAME _ _ <<< "$SPACE_INFO"
    echo "   • https://huggingface.co/spaces/$USERNAME/$SPACE_NAME"
done
echo ""
echo "📚 See CREATE_SPACES_GUIDE.md for configuration details"
echo ""

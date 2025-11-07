#!/bin/bash

# Hugging Face Spaces Deployment Script for NLWeb Portfolio Chat

echo "🚀 Preparing deployment to Hugging Face Spaces..."

# Check if git is configured
if ! git config user.name > /dev/null; then
    echo "❌ Git user not configured. Please run:"
    echo "git config --global user.name 'Your Name'"
    echo "git config --global user.email 'your.email@example.com'"
    exit 1
fi

# Create deployment directory
DEPLOY_DIR="nlweb-hf-deployment"
rm -rf $DEPLOY_DIR
mkdir $DEPLOY_DIR
cd $DEPLOY_DIR

# Initialize git repository
git init
git branch -M main

# Copy necessary files
cp ../app.py .
cp ../requirements.txt .
cp ../Dockerfile .
cp ../README.md .
cp ../.env.example .env

echo "✅ Files copied to deployment directory"

# Create gitignore
cat > .gitignore << EOL
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
EOL

echo "📝 Instructions for deployment:"
echo ""
echo "1. Go to https://huggingface.co/new-space"
echo "2. Create a new Space with these settings:"
echo "   - Owner: HarithKavish (or your username)"
echo "   - Space name: nlweb-portfolio-chat"
echo "   - License: MIT"
echo "   - SDK: Docker"
echo "   - Hardware: CPU basic (free tier)"
echo ""
echo "3. Clone the Space repository:"
echo "   git clone https://huggingface.co/spaces/HarithKavish/nlweb-portfolio-chat"
echo ""
echo "4. Copy the files from this deployment directory to the cloned Space"
echo ""
echo "5. Update the .env file with your MongoDB credentials"
echo ""
echo "6. Commit and push:"
echo "   git add ."
echo "   git commit -m 'Initial deployment of NLWeb Portfolio Chat'"
echo "   git push"
echo ""
echo "📍 The deployment files are ready in: $(pwd)"
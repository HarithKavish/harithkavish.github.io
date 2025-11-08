"""
Create HuggingFace Space for MCP Server using huggingface_hub API
"""
from huggingface_hub import HfApi, login
import os

# Configuration
SPACE_NAME = "mcp-server-stt-tts"
HF_USERNAME = "harithkavish"
HF_TOKEN = os.getenv("HF_TOKEN")

if not HF_TOKEN:
    print("❌ Error: HF_TOKEN environment variable not set")
    print("\nTo create a space, you need a HuggingFace token:")
    print("1. Go to: https://huggingface.co/settings/tokens")
    print("2. Create a new token with 'write' access")
    print("3. Run in PowerShell:")
    print('   $env:HF_TOKEN = "your_token_here"')
    print(f'   py create_space.py')
    print("\nOr create the space manually:")
    print("1. Go to: https://huggingface.co/new-space")
    print("2. Name: mcp-server-stt-tts")
    print("3. Space SDK: Docker")
    print("4. Hardware: CPU basic (free)")
    print("5. Visibility: Public")
    print("\nThen run:")
    print(f"  git remote set-url hf https://huggingface.co/spaces/{HF_USERNAME}/{SPACE_NAME}")
    print(f"  git push hf master:main --force")
    exit(1)

print(f"🔑 Logging in to HuggingFace...")
login(token=HF_TOKEN)

print(f"🔑 Logging in to HuggingFace...")
login(token=HF_TOKEN)

# Create space
api = HfApi()

print(f"🚀 Creating HuggingFace Space: {HF_USERNAME}/{SPACE_NAME}")

try:
    api.create_repo(
        repo_id=f"{HF_USERNAME}/{SPACE_NAME}",
        repo_type="space",
        space_sdk="docker",
        private=False
    )
    
    print("✅ Space created successfully!")
    print(f"\n🔗 URL: https://huggingface.co/spaces/{HF_USERNAME}/{SPACE_NAME}")
    print("\n📤 Now push the code:")
    print(f"  git remote set-url hf https://huggingface.co/spaces/{HF_USERNAME}/{SPACE_NAME}")
    print(f"  git push hf master:main --force")
    
except Exception as e:
    if "already exists" in str(e).lower():
        print(f"ℹ️  Space already exists: {HF_USERNAME}/{SPACE_NAME}")
        print(f"🔗 URL: https://huggingface.co/spaces/{HF_USERNAME}/{SPACE_NAME}")
        print("\n📤 Push the code:")
        print(f"  git remote set-url hf https://huggingface.co/spaces/{HF_USERNAME}/{SPACE_NAME}")
        print(f"  git push hf master:main --force")
    else:
        print(f"❌ Failed to create space: {e}")
        print("\n💡 Try creating manually at: https://huggingface.co/new-space")

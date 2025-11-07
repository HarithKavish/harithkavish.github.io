#!/usr/bin/env python3
"""
Create a Hugging Face Space for NLWeb Portfolio Chat
"""
import os
import subprocess
from huggingface_hub import HfApi, login

def create_hf_space():
    """Create Hugging Face Space and set up repository"""
    
    print("🚀 Creating Hugging Face Space for NLWeb Portfolio Chat...")
    
    # Initialize HF API
    api = HfApi()
    
    # Space configuration
    space_name = "nlweb-portfolio-chat"
    space_description = "AI-powered portfolio chat using NLWeb with MongoDB vector search and Hugging Face Transformers"
    
    try:
        # Check if user is logged in using HF_TOKEN environment variable
        token = os.getenv('HF_TOKEN')
        if not token:
            print("❌ Please set your Hugging Face token:")
            print("   1. Get token from: https://huggingface.co/settings/tokens")
            print("   2. Set environment: $env:HF_TOKEN='your_token_here'")
            print("   3. Or run: huggingface-cli login")
            return False
            
        # Get user info
        user_info = api.whoami(token=token)
        username = user_info["name"]
        print(f"✅ Logged in as: {username}")
        
        # Create the space
        print(f"📦 Creating space: {username}/{space_name}")
        
        repo_url = api.create_repo(
            repo_id=f"{username}/{space_name}",
            token=token,
            repo_type="space",
            space_sdk="docker",
            space_hardware="cpu-basic",
            private=False,
            exist_ok=True
        )
        
        print(f"✅ Space created successfully!")
        print(f"🌐 Space URL: https://huggingface.co/spaces/{username}/{space_name}")
        print(f"📋 Git URL: {repo_url}")
        
        # Set up git remote
        deployment_dir = "nlweb-hf-deployment"
        if os.path.exists(deployment_dir):
            os.chdir(deployment_dir)
            
            # Add HF remote
            try:
                subprocess.run(["git", "remote", "remove", "origin"], 
                             capture_output=True, check=False)
            except:
                pass
                
            subprocess.run([
                "git", "remote", "add", "origin", 
                f"https://huggingface.co/spaces/{username}/{space_name}"
            ], check=True)
            
            print(f"✅ Git remote configured")
            
            # Push to HF Space
            print("📤 Pushing deployment to Hugging Face Space...")
            result = subprocess.run([
                "git", "push", "-u", "origin", "main"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Deployment pushed successfully!")
                print(f"🎉 Your NLWeb Portfolio Chat is now live at:")
                print(f"   https://huggingface.co/spaces/{username}/{space_name}")
                return f"https://{username.lower()}-{space_name.replace('_', '-')}.hf.space"
            else:
                print(f"❌ Push failed: {result.stderr}")
                print("Attempting to push with force...")
                
                # Try force push
                force_result = subprocess.run([
                    "git", "push", "-f", "origin", "main"
                ], capture_output=True, text=True)
                
                if force_result.returncode == 0:
                    print("✅ Force push successful!")
                    return f"https://{username.lower()}-{space_name.replace('_', '-')}.hf.space"
                else:
                    print(f"❌ Force push also failed: {force_result.stderr}")
                    return None
        else:
            print(f"❌ Deployment directory '{deployment_dir}' not found")
            return None
            
    except Exception as e:
        print(f"❌ Error creating space: {str(e)}")
        return None

if __name__ == "__main__":
    space_url = create_hf_space()
    if space_url:
        print(f"\n🎊 SUCCESS! Your space is available at: {space_url}")
    else:
        print("\n💡 Manual steps needed:")
        print("1. Go to https://huggingface.co/new-space")
        print("2. Create space with name: nlweb-portfolio-chat")
        print("3. Select Docker SDK and CPU basic hardware")
        print("4. Then run git push manually from nlweb-hf-deployment/")
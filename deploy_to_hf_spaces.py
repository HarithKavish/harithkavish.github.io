"""
Deploy updated layer code to HuggingFace Spaces
Pushes specialized architecture changes to all spaces
"""
from huggingface_hub import HfApi, login, whoami
import os
from pathlib import Path

# Space configurations
SPACES = {
    "perception-layer": {
        "repo_id": "harithkavish/harithkavish-nlweb-perception",
        "local_path": "spaces/perception-layer",
        "files": ["app.py"]
    },
    "memory-layer": {
        "repo_id": "harithkavish/harithkavish-nlweb-memory",
        "local_path": "spaces/memory-layer",
        "files": ["app.py"]
    },
    "reasoning-layer": {
        "repo_id": "harithkavish/harithkavish-nlweb-reasoning",
        "local_path": "spaces/reasoning-layer",
        "files": ["app.py"]
    },
    "monitoring-safety": {
        "repo_id": "harithkavish/harithkavish-nlweb-monitoring",
        "local_path": "spaces/monitoring-safety",
        "files": ["app.py"]
    },
    "execution-layer": {
        "repo_id": "harithkavish/harithkavish-nlweb-execution",
        "local_path": "spaces/execution-layer",
        "files": ["app.py"]
    },
    "orchestrator": {
        "repo_id": "harithkavish/harithkavish-nlweb-orchestrator",
        "local_path": "spaces/orchestrator",
        "files": ["app.py"]
    }
}

def check_login():
    """Check if user is logged in to HuggingFace"""
    try:
        user_info = whoami()
        print(f"✓ Logged in as: {user_info['name']}")
        return True
    except Exception as e:
        print(f"✗ Not logged in to HuggingFace")
        print(f"  Run: huggingface-cli login")
        print(f"  Or set HF_TOKEN environment variable")
        return False

def deploy_space(space_name, config):
    """Deploy a single space to HuggingFace"""
    print(f"\n📦 Deploying {space_name}...")
    
    api = HfApi()
    repo_id = config["repo_id"]
    local_path = Path(config["local_path"])
    
    try:
        # Check if space exists
        try:
            api.repo_info(repo_id=repo_id, repo_type="space")
            print(f"   ✓ Space exists: {repo_id}")
        except Exception:
            print(f"   ✗ Space not found: {repo_id}")
            print(f"   → Create it manually at: https://huggingface.co/new-space")
            return False
        
        # Upload files
        for file in config["files"]:
            file_path = local_path / file
            
            if not file_path.exists():
                print(f"   ✗ File not found: {file_path}")
                continue
            
            print(f"   📤 Uploading {file}...")
            api.upload_file(
                path_or_fileobj=str(file_path),
                path_in_repo=file,
                repo_id=repo_id,
                repo_type="space",
                commit_message=f"Update {file} with specialized architecture"
            )
            print(f"   ✓ Uploaded {file}")
        
        print(f"✓ {space_name} deployed successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Failed to deploy {space_name}: {e}")
        return False

def main():
    print("╔════════════════════════════════════════════════════════════╗")
    print("║     🚀 HuggingFace Spaces Deployment Tool                ║")
    print("║     Specialized Architecture Deployment                   ║")
    print("╚════════════════════════════════════════════════════════════╝\n")
    
    # Check login status
    if not check_login():
        print("\n⚠️  Please log in to HuggingFace first:")
        print("   Option 1: Run 'huggingface-cli login' in terminal")
        print("   Option 2: Set HF_TOKEN environment variable")
        return
    
    print("\n📋 Spaces to deploy:")
    for name, config in SPACES.items():
        print(f"   • {name} → {config['repo_id']}")
    
    print("\n" + "="*60)
    
    # Deploy each space
    success_count = 0
    failed_count = 0
    
    for space_name, config in SPACES.items():
        if deploy_space(space_name, config):
            success_count += 1
        else:
            failed_count += 1
    
    # Summary
    print("\n" + "="*60)
    print("\n📊 DEPLOYMENT SUMMARY:")
    print(f"   ✓ Successful: {success_count}/{len(SPACES)}")
    print(f"   ✗ Failed: {failed_count}/{len(SPACES)}")
    
    if success_count == len(SPACES):
        print("\n🎉 All spaces deployed successfully!")
        print("\n⏳ Next steps:")
        print("   1. Visit each Space to verify deployment")
        print("   2. Check logs for 'Specialized for:' messages")
        print("   3. Test the chatbot widget on your site")
        print("\n   Spaces will rebuild automatically (~2-3 min each)")
    elif success_count > 0:
        print("\n⚠️  Some spaces failed. Check the errors above.")
        print("   You may need to create missing spaces manually.")
    else:
        print("\n✗ All deployments failed. Check your HuggingFace credentials.")

if __name__ == "__main__":
    main()

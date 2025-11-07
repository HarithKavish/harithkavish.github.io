"""
Create Vector Search Indexes in MongoDB Atlas using Admin API
"""
import os
import requests
import json
from dotenv import load_dotenv
import time

load_dotenv()

# MongoDB Atlas API Configuration
ATLAS_PUBLIC_KEY = os.getenv("ATLAS_PUBLIC_KEY")
ATLAS_PRIVATE_KEY = os.getenv("ATLAS_PRIVATE_KEY")
PROJECT_ID = os.getenv("ATLAS_PROJECT_ID")
CLUSTER_NAME = os.getenv("ATLAS_CLUSTER_NAME", "Cluster0")
DATABASE_NAME = "portfolio_db"

# Vector Index Definitions
INDEXES = [
    {
        "name": "assistant_vector_index",
        "collection": "assistant_identity",
        "definition": {
            "fields": [
                {
                    "type": "vector",
                    "path": "embedding",
                    "numDimensions": 384,
                    "similarity": "cosine"
                }
            ]
        }
    },
    {
        "name": "portfolio_vector_index",
        "collection": "harith_portfolio",
        "definition": {
            "fields": [
                {
                    "type": "vector",
                    "path": "embedding",
                    "numDimensions": 384,
                    "similarity": "cosine"
                }
            ]
        }
    },
    {
        "name": "knowledge_vector_index",
        "collection": "general_knowledge",
        "definition": {
            "fields": [
                {
                    "type": "vector",
                    "path": "embedding",
                    "numDimensions": 384,
                    "similarity": "cosine"
                }
            ]
        }
    }
]

def create_vector_index(collection_name: str, index_name: str, definition: dict):
    """Create a vector search index using MongoDB Atlas Admin API"""
    
    url = f"https://cloud.mongodb.com/api/atlas/v1.0/groups/{PROJECT_ID}/clusters/{CLUSTER_NAME}/fts/indexes"
    
    payload = {
        "collectionName": collection_name,
        "database": DATABASE_NAME,
        "name": index_name,
        "type": "vectorSearch",
        "definition": definition
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    response = requests.post(
        url,
        auth=(ATLAS_PUBLIC_KEY, ATLAS_PRIVATE_KEY),
        headers=headers,
        json=payload
    )
    
    return response

def check_index_status(index_id: str):
    """Check the status of a vector search index"""
    
    url = f"https://cloud.mongodb.com/api/atlas/v1.0/groups/{PROJECT_ID}/clusters/{CLUSTER_NAME}/fts/indexes/{index_id}"
    
    headers = {
        "Accept": "application/json"
    }
    
    response = requests.get(
        url,
        auth=(ATLAS_PUBLIC_KEY, ATLAS_PRIVATE_KEY),
        headers=headers
    )
    
    return response

def main():
    print("\n" + "="*60)
    print("🔧 MONGODB ATLAS VECTOR INDEX CREATOR")
    print("="*60 + "\n")
    
    # Validate credentials
    if not ATLAS_PUBLIC_KEY or not ATLAS_PRIVATE_KEY:
        print("❌ Error: ATLAS_PUBLIC_KEY and ATLAS_PRIVATE_KEY must be set in .env file")
        print("\n📝 To get API keys:")
        print("   1. Go to https://cloud.mongodb.com/")
        print("   2. Click your profile → 'Organization Access Manager'")
        print("   3. Select 'API Keys' tab")
        print("   4. Click 'Create API Key'")
        print("   5. Grant 'Project Owner' permissions")
        print("   6. Add to .env file:")
        print("      ATLAS_PUBLIC_KEY=your_public_key")
        print("      ATLAS_PRIVATE_KEY=your_private_key")
        return
    
    if not PROJECT_ID:
        print("❌ Error: ATLAS_PROJECT_ID must be set in .env file")
        print("\n📝 To get Project ID:")
        print("   1. Go to https://cloud.mongodb.com/")
        print("   2. Look at the URL: /v2/{PROJECT_ID}#/...")
        print("   3. Copy the PROJECT_ID from the URL")
        print("   4. Add to .env file:")
        print("      ATLAS_PROJECT_ID=your_project_id")
        return
    
    print(f"📊 Configuration:")
    print(f"   Project ID: {PROJECT_ID}")
    print(f"   Cluster: {CLUSTER_NAME}")
    print(f"   Database: {DATABASE_NAME}")
    print(f"   Indexes to create: {len(INDEXES)}\n")
    
    created_indexes = []
    
    # Create each index
    for idx_config in INDEXES:
        collection = idx_config["collection"]
        index_name = idx_config["name"]
        definition = idx_config["definition"]
        
        print(f"🔨 Creating index '{index_name}' on '{collection}'...")
        
        response = create_vector_index(collection, index_name, definition)
        
        if response.status_code in [200, 201]:
            result = response.json()
            index_id = result.get("indexID")
            created_indexes.append({
                "id": index_id,
                "name": index_name,
                "collection": collection
            })
            print(f"   ✅ Index created successfully! ID: {index_id}")
        elif response.status_code == 409:
            print(f"   ⚠️  Index already exists (skipping)")
        else:
            print(f"   ❌ Failed: {response.status_code}")
            print(f"   Response: {response.text}")
    
    if not created_indexes:
        print("\n✅ All indexes already exist or no new indexes were created.")
        return
    
    # Wait for indexes to build
    print(f"\n⏳ Waiting for {len(created_indexes)} index(es) to build...")
    print("   (This typically takes 2-5 minutes per index)")
    
    all_ready = False
    max_attempts = 60  # 10 minutes max
    attempt = 0
    
    while not all_ready and attempt < max_attempts:
        attempt += 1
        time.sleep(10)  # Check every 10 seconds
        
        statuses = []
        for idx in created_indexes:
            response = check_index_status(idx["id"])
            if response.status_code == 200:
                result = response.json()
                status = result.get("status", "UNKNOWN")
                statuses.append(status)
                
                if status == "READY":
                    print(f"   ✅ {idx['name']}: READY")
                else:
                    print(f"   ⏳ {idx['name']}: {status}")
            else:
                statuses.append("UNKNOWN")
                print(f"   ⚠️  {idx['name']}: Unable to check status")
        
        all_ready = all(s == "READY" for s in statuses)
        
        if not all_ready:
            print(f"   Checking again in 10 seconds... (attempt {attempt}/{max_attempts})")
    
    print("\n" + "="*60)
    if all_ready:
        print("🎉 ALL VECTOR SEARCH INDEXES ARE READY!")
    else:
        print("⚠️  Some indexes are still building. Check MongoDB Atlas console.")
    print("="*60 + "\n")
    
    print("📋 Summary:")
    for idx in created_indexes:
        print(f"   ✓ {idx['collection']}.{idx['name']}")
    
    print("\n🚀 Next Steps:")
    print("   1. Test the multi-domain search:")
    print("      python test_nlweb_retrieval.py")
    print("   2. Try queries like:")
    print("      - 'Who are you?'")
    print("      - 'What projects has Harith built?'")
    print("      - 'What is RAG?'")
    print("\n✨ Your three-vector database system is now LIVE!\n")

if __name__ == "__main__":
    main()

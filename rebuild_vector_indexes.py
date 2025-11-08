"""
Rebuild vector search indexes in MongoDB Atlas.
"""
import os
import requests
import json
from dotenv import load_dotenv
import time

load_dotenv()

# MongoDB Atlas API configuration
ATLAS_PUBLIC_KEY = os.getenv("ATLAS_PUBLIC_KEY")
ATLAS_PRIVATE_KEY = os.getenv("ATLAS_PRIVATE_KEY")
PROJECT_ID = os.getenv("ATLAS_PROJECT_ID")
CLUSTER_NAME = os.getenv("ATLAS_CLUSTER_NAME", "Cluster0")

DB_NAME = "portfolio_db"

# Index definitions
INDEXES = {
    "assistant_identity": {
        "name": "assistant_vector_index",
        "type": "vectorSearch",
        "definition": {
            "fields": [
                {
                    "type": "vector",
                    "path": "embedding",
                    "numDimensions": 384,
                    "similarity": "cosine"
                },
                {
                    "type": "filter",
                    "path": "metadata.name"
                }
            ]
        }
    },
    "harith_portfolio": {
        "name": "portfolio_vector_index",
        "type": "vectorSearch",
        "definition": {
            "fields": [
                {
                    "type": "vector",
                    "path": "embedding",
                    "numDimensions": 384,
                    "similarity": "cosine"
                },
                {
                    "type": "filter",
                    "path": "metadata.name"
                },
                {
                    "type": "filter",
                    "path": "metadata.@type"
                }
            ]
        }
    },
    "general_knowledge": {
        "name": "knowledge_vector_index",
        "type": "vectorSearch",
        "definition": {
            "fields": [
                {
                    "type": "vector",
                    "path": "embedding",
                    "numDimensions": 384,
                    "similarity": "cosine"
                },
                {
                    "type": "filter",
                    "path": "metadata.keywords"
                }
            ]
        }
    }
}

def check_atlas_credentials():
    """Check if Atlas API credentials are configured."""
    if not ATLAS_PUBLIC_KEY or not ATLAS_PRIVATE_KEY or not PROJECT_ID:
        print("❌ MongoDB Atlas API credentials not configured!\n")
        print("To use the API, add these to your .env file:")
        print("  ATLAS_PUBLIC_KEY=your_public_key")
        print("  ATLAS_PRIVATE_KEY=your_private_key")
        print("  ATLAS_PROJECT_ID=your_project_id")
        print("\nGet these from: https://cloud.mongodb.com/v2#/account/publicApi")
        print("\n" + "="*80)
        print("MANUAL STEPS TO REBUILD INDEXES:")
        print("="*80)
        print("\n1. Go to: https://cloud.mongodb.com/")
        print("2. Select your cluster → Browse Collections")
        print("3. Select 'portfolio_db' database")
        print("4. Click 'Search Indexes' tab (or 'Atlas Search')")
        print("\n5. For EACH collection (assistant_identity, harith_portfolio, general_knowledge):")
        print("   a. Click 'Create Search Index'")
        print("   b. Choose 'JSON Editor'")
        print("   c. Copy and paste the index definition below:")
        print("\n" + "-"*80)
        
        for collection, index_def in INDEXES.items():
            print(f"\n📋 INDEX FOR '{collection}' collection:")
            print(f"   Name: {index_def['name']}")
            print("\n   JSON Definition:")
            print(json.dumps(index_def['definition'], indent=2))
            print("\n" + "-"*80)
        
        print("\n6. Click 'Create Search Index' for each")
        print("7. Wait 2-5 minutes for indexes to build")
        print("8. Test your chatbot!")
        
        return False
    return True

def list_existing_indexes():
    """List existing search indexes."""
    url = f"https://cloud.mongodb.com/api/atlas/v2/groups/{PROJECT_ID}/clusters/{CLUSTER_NAME}/fts/indexes/{DB_NAME}"
    
    try:
        response = requests.get(
            url,
            auth=(ATLAS_PUBLIC_KEY, ATLAS_PRIVATE_KEY),
            headers={"Accept": "application/vnd.atlas.2023-01-01+json"}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"  ⚠️  Failed to list indexes: {response.status_code}")
            return None
    except Exception as e:
        print(f"  ⚠️  Error: {e}")
        return None

def delete_index(collection_name, index_id):
    """Delete a search index."""
    url = f"https://cloud.mongodb.com/api/atlas/v2/groups/{PROJECT_ID}/clusters/{CLUSTER_NAME}/fts/indexes/{index_id}"
    
    try:
        response = requests.delete(
            url,
            auth=(ATLAS_PUBLIC_KEY, ATLAS_PRIVATE_KEY),
            headers={"Accept": "application/vnd.atlas.2023-01-01+json"}
        )
        
        if response.status_code in [200, 202, 204]:
            return True
        else:
            print(f"    ⚠️  Failed to delete: {response.status_code}")
            return False
    except Exception as e:
        print(f"    ⚠️  Error: {e}")
        return False

def create_index(collection_name, index_config):
    """Create a new vector search index."""
    url = f"https://cloud.mongodb.com/api/atlas/v2/groups/{PROJECT_ID}/clusters/{CLUSTER_NAME}/fts/indexes"
    
    payload = {
        "database": DB_NAME,
        "collectionName": collection_name,
        "name": index_config["name"],
        "type": index_config["type"],
        "definition": index_config["definition"]
    }
    
    try:
        response = requests.post(
            url,
            auth=(ATLAS_PUBLIC_KEY, ATLAS_PRIVATE_KEY),
            headers={
                "Accept": "application/vnd.atlas.2023-01-01+json",
                "Content-Type": "application/json"
            },
            json=payload
        )
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            print(f"    ⚠️  Failed to create: {response.status_code}")
            print(f"    Response: {response.text}")
            return None
    except Exception as e:
        print(f"    ⚠️  Error: {e}")
        return None

def rebuild_indexes():
    """Rebuild all vector search indexes."""
    print("=" * 80)
    print("REBUILDING MONGODB ATLAS VECTOR SEARCH INDEXES")
    print("=" * 80 + "\n")
    
    if not check_atlas_credentials():
        return
    
    print("🔍 Checking existing indexes...\n")
    existing = list_existing_indexes()
    
    if existing:
        indexes_list = existing.get('results', [])
        if indexes_list:
            print(f"  Found {len(indexes_list)} existing indexes\n")
            
            # Delete old indexes
            print("🗑️  Deleting old indexes...\n")
            for idx in indexes_list:
                collection = idx.get('collectionName')
                index_name = idx.get('name')
                index_id = idx.get('indexID')
                
                if collection in INDEXES:
                    print(f"  Deleting: {collection}/{index_name}")
                    if delete_index(collection, index_id):
                        print(f"    ✓ Deleted")
                    time.sleep(1)
            
            print("\n⏳ Waiting for deletion to complete (10 seconds)...\n")
            time.sleep(10)
        else:
            print("  No existing indexes found\n")
    
    # Create new indexes
    print("📝 Creating new vector search indexes...\n")
    
    created = 0
    for collection_name, index_config in INDEXES.items():
        print(f"  Creating: {collection_name}/{index_config['name']}")
        
        result = create_index(collection_name, index_config)
        
        if result:
            print(f"    ✓ Created (ID: {result.get('indexID', 'unknown')})")
            created += 1
        
        time.sleep(2)
    
    print("\n" + "=" * 80)
    print("✅ INDEX REBUILD COMPLETE!")
    print("=" * 80)
    print(f"\n📊 Summary:")
    print(f"  • Indexes created: {created}/{len(INDEXES)}")
    print(f"\n⏳ Indexes are now building (takes 2-5 minutes)")
    print(f"\n🔧 Next steps:")
    print(f"  1. Wait for indexes to finish building")
    print(f"  2. Check status: https://cloud.mongodb.com/")
    print(f"  3. Test the chatbot!")

if __name__ == "__main__":
    rebuild_indexes()

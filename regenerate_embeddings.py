"""
Regenerate embeddings for MongoDB documents using HuggingFace Perception Layer.
"""
import os
from pymongo import MongoClient
from dotenv import load_dotenv
import requests
import time

load_dotenv()

# MongoDB configuration
MONGO_URI = os.getenv("MONGODB_URI")
DB_NAME = "portfolio_db"

# HuggingFace Perception Layer
PERCEPTION_URL = "https://harithkavish-harithkavish-nlweb-perception.hf.space"

def generate_embedding_batch(texts):
    """Generate embeddings using Perception Layer batch endpoint."""
    try:
        response = requests.post(
            f"{PERCEPTION_URL}/embed/batch",
            json={"texts": texts},
            timeout=60
        )
        if response.status_code == 200:
            return response.json()['embeddings']
        else:
            print(f"    ⚠️  API error: {response.status_code}")
            return None
    except Exception as e:
        print(f"    ⚠️  Request failed: {e}")
        return None

def regenerate_embeddings():
    """Regenerate all embeddings in MongoDB."""
    print("=" * 80)
    print("REGENERATING EMBEDDINGS FOR CURATED DATA")
    print("=" * 80 + "\n")
    
    # Connect
    print("🔌 Connecting to MongoDB Atlas...")
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    print("  ✓ Connected!\n")
    
    collections = ['assistant_identity', 'harith_portfolio', 'general_knowledge']
    
    total_updated = 0
    
    for coll_name in collections:
        print(f"📚 Processing collection: {coll_name}")
        collection = db[coll_name]
        
        documents = list(collection.find({}))
        print(f"  Found {len(documents)} documents\n")
        
        if not documents:
            continue
        
        # Batch process (max 10 at a time)
        batch_size = 10
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i+batch_size]
            
            # Prepare texts for embedding
            texts = []
            for doc in batch:
                text = doc.get('content', '')
                metadata = doc.get('metadata', {})
                if metadata.get('description'):
                    text += " " + metadata['description']
                texts.append(text)
            
            print(f"  🧮 Generating embeddings for batch {i//batch_size + 1}...")
            
            embeddings = generate_embedding_batch(texts)
            
            if not embeddings:
                print(f"    ⚠️  Batch failed, skipping...")
                continue
            
            # Update documents
            for doc, embedding in zip(batch, embeddings):
                collection.update_one(
                    {'_id': doc['_id']},
                    {'$set': {'embedding': embedding}}
                )
                total_updated += 1
            
            print(f"    ✓ Updated {len(batch)} documents")
            
            # Rate limiting
            time.sleep(1)
        
        print()
    
    print("=" * 80)
    print("✅ EMBEDDING REGENERATION COMPLETE!")
    print("=" * 80)
    print(f"\n📊 Updated {total_updated} documents with new embeddings")
    print(f"\n🔧 Next step: Rebuild vector indexes in MongoDB Atlas")
    
    client.close()

if __name__ == "__main__":
    regenerate_embeddings()

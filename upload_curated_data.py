"""
Upload curated portfolio data to MongoDB with embeddings.
"""
import os
import json
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# MongoDB configuration
MONGO_URI = os.getenv("MONGODB_URI")  # Use MONGODB_URI from .env
DB_NAME = "portfolio_db"

# Try to use local embedding generation
try:
    from sentence_transformers import SentenceTransformer
    print("✓ Using local embedding generation\n")
    embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    USE_LOCAL_EMBEDDINGS = True
except Exception as e:
    print(f"⚠️  Could not load local embedding model: {e}")
    print("   Will skip embedding generation\n")
    USE_LOCAL_EMBEDDINGS = False
    embedding_model = None

def generate_embedding(text):
    """Generate embedding using local model."""
    if not USE_LOCAL_EMBEDDINGS:
        # Return a dummy embedding if model not available
        return [0.0] * 384
    
    try:
        embedding = embedding_model.encode(text, convert_to_tensor=False)
        return embedding.tolist()
    except Exception as e:
        print(f"    ⚠️  Embedding generation failed: {e}")
        return [0.0] * 384

def categorize_document(doc):
    """Determine which collection a document belongs to."""
    metadata = doc.get('metadata', {})
    name = metadata.get('name', '').lower()
    doc_type = metadata.get('@type', '').lower()
    description = metadata.get('description', '').lower()
    
    # Neo AI identity
    if 'neo ai' in name or 'assistant' in name:
        return 'assistant_identity'
    
    # Portfolio projects
    if doc_type in ['softwareapplication', 'softwaresourcecode', 'website']:
        return 'harith_portfolio'
    
    # Skills and general knowledge
    if 'skill' in name or 'expertise' in name or 'person' in doc_type:
        return 'general_knowledge'
    
    # Default to portfolio
    return 'harith_portfolio'

def upload_curated_data():
    """Upload curated data to MongoDB."""
    print("=" * 80)
    print("UPLOADING CURATED DATA TO MONGODB")
    print("=" * 80 + "\n")
    
    # Connect to MongoDB
    print("🔌 Connecting to MongoDB Atlas...")
    if not MONGO_URI or "localhost" in MONGO_URI:
        print("  ❌ Error: MONGO_URI not configured or pointing to localhost")
        print("     Please set MONGO_URI in .env to your MongoDB Atlas connection string")
        return
    
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    print("  ✓ Connected!\n")
    
    # Clear existing collections
    print("🗑️  Clearing old collections...")
    collections = ['assistant_identity', 'harith_portfolio', 'general_knowledge']
    for coll_name in collections:
        db[coll_name].delete_many({})
        print(f"  ✓ Cleared {coll_name}")
    print()
    
    # Load curated data
    print("📂 Loading curated_portfolio_data.jsonl...")
    with open('curated_portfolio_data.jsonl', 'r', encoding='utf-8') as f:
        documents = [json.loads(line) for line in f]
    print(f"  ✓ Loaded {len(documents)} documents\n")
    
    # Process and upload each document
    print("⬆️  Uploading documents with embeddings...\n")
    
    stats = {
        'assistant_identity': 0,
        'harith_portfolio': 0,
        'general_knowledge': 0
    }
    
    for i, doc in enumerate(documents, 1):
        metadata = doc.get('metadata', {})
        name = metadata.get('name', f'Document {i}')
        
        print(f"  [{i}/{len(documents)}] Processing: {name}")
        
        # Generate embedding if not present
        if 'embedding' not in doc:
            text_for_embedding = doc['content']
            if metadata.get('description'):
                text_for_embedding += " " + metadata['description']
            
            print(f"      🧮 Generating embedding...")
            embedding = generate_embedding(text_for_embedding)
            doc['embedding'] = embedding
        
        # Determine collection
        collection_name = categorize_document(doc)
        collection = db[collection_name]
        
        # Upload
        result = collection.insert_one(doc)
        stats[collection_name] += 1
        
        print(f"      ✓ Uploaded to {collection_name} (ID: {str(result.inserted_id)[:8]}...)")
        print()
    
    print("=" * 80)
    print("✅ UPLOAD COMPLETE!")
    print("=" * 80)
    print(f"\n📊 Summary:")
    print(f"  • assistant_identity: {stats['assistant_identity']} documents")
    print(f"  • harith_portfolio: {stats['harith_portfolio']} documents")
    print(f"  • general_knowledge: {stats['general_knowledge']} documents")
    print(f"  • Total: {sum(stats.values())} documents")
    print(f"\n🔧 Next steps:")
    print(f"  1. Verify collections: py verify_collections.py")
    print(f"  2. Rebuild vector indexes in MongoDB Atlas")
    print(f"  3. Test the chatbot!")
    
    client.close()

if __name__ == "__main__":
    upload_curated_data()

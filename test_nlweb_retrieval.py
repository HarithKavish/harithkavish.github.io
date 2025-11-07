"""Test NLWeb retrieval to debug why queries aren't working."""
import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment
load_dotenv("C:/Dev/GitHub/NLWeb/.env")

# Get MongoDB connection
mongo_uri = os.getenv("MONGODB_URI")
print(f"MongoDB URI: {mongo_uri[:50]}...")

# Connect to MongoDB
client = MongoClient(mongo_uri)
db = client["nlweb"]
collection = db["portfolio_vectors"]

# Check collection stats
count = collection.count_documents({})
print(f"\n✓ Total documents in collection: {count}")

# Get sample document
sample = collection.find_one({})
if sample:
    print(f"\n✓ Sample document keys: {list(sample.keys())}")
    print(f"  - Has embedding: {'embedding' in sample}")
    if 'embedding' in sample:
        print(f"  - Embedding dimensions: {len(sample['embedding'])}")
    print(f"  - Content preview: {str(sample.get('content', ''))[:200]}...")

# List all indexes
print(f"\n✓ Indexes on collection:")
for index in collection.list_indexes():
    print(f"  - {index['name']}: {index.get('key', {})}")

# Check for vector search index
print(f"\n✓ Checking vector search indexes...")
try:
    # This requires special permissions, might fail
    search_indexes = list(collection.list_search_indexes())
    if search_indexes:
        print(f"  Found {len(search_indexes)} search index(es):")
        for idx in search_indexes:
            print(f"    - {idx.get('name')}: {idx.get('status')}")
    else:
        print("  ⚠ No vector search indexes found!")
except Exception as e:
    print(f"  ⚠ Could not list search indexes: {e}")

# Test Ollama connection
print(f"\n✓ Testing Ollama connection...")
try:
    import ollama
    models = ollama.list()
    print(f"  Available models: {[m['name'] for m in models['models']]}")
    
    # Test embedding generation
    print(f"\n✓ Testing embedding generation...")
    test_text = "What projects does Harith have?"
    response = ollama.embeddings(model="nomic-embed-text", prompt=test_text)
    embedding = response['embedding']
    print(f"  Generated embedding dimensions: {len(embedding)}")
    
except Exception as e:
    print(f"  ✗ Ollama error: {e}")

print("\n" + "="*60)

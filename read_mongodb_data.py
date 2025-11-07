"""
Read and display all data from MongoDB Atlas portfolio_vectors collection
"""
from pymongo import MongoClient
import json

# MongoDB connection string
MONGODB_URI = "mongodb+srv://harithkavish40:K11nPy9sv9ron4eQ@cluster0.wmcojpw.mongodb.net/nlweb?retryWrites=true&w=majority&appName=Cluster0"

def read_mongodb_data():
    try:
        print("🔌 Connecting to MongoDB Atlas...")
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        
        # Test connection
        client.admin.command('ping')
        print("✓ Connected successfully!\n")
        
        db = client["nlweb"]
        collection = db["portfolio_vectors"]
        
        # Get total count
        doc_count = collection.count_documents({})
        print(f"📊 Total documents in portfolio_vectors: {doc_count}\n")
        print("=" * 80)
        
        if doc_count == 0:
            print("❌ No documents found in the collection!")
            return
        
        # Read all documents
        documents = list(collection.find({}))
        
        for idx, doc in enumerate(documents, 1):
            print(f"\n📄 DOCUMENT {idx}/{doc_count}")
            print("-" * 80)
            
            # Basic info
            print(f"ID: {doc.get('_id')}")
            
            # Content
            content = doc.get('content', '')
            print(f"\nContent ({len(content)} chars):")
            if content:
                print(f"  {content}")
            else:
                print("  [EMPTY]")
            
            # Metadata
            metadata = doc.get('metadata', {})
            print(f"\nMetadata:")
            if metadata:
                for key, value in metadata.items():
                    if isinstance(value, list):
                        print(f"  {key}: {', '.join(map(str, value[:5]))}{'...' if len(value) > 5 else ''}")
                    elif isinstance(value, dict):
                        print(f"  {key}: {json.dumps(value, indent=4)}")
                    else:
                        value_str = str(value)
                        if len(value_str) > 200:
                            print(f"  {key}: {value_str[:200]}...")
                        else:
                            print(f"  {key}: {value_str}")
            else:
                print("  [NO METADATA]")
            
            # Embedding info
            if 'embedding' in doc:
                embedding = doc['embedding']
                print(f"\nEmbedding: Yes ({len(embedding)} dimensions)")
                print(f"  First 5 values: {embedding[:5]}")
            else:
                print(f"\nEmbedding: No")
            
            print("\n" + "=" * 80)
        
        client.close()
        print("\n✓ Finished reading MongoDB data")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    read_mongodb_data()

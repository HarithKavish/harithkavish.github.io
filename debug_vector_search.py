"""
Debug script to examine actual vector search results structure
"""
import asyncio
import motor.motor_asyncio
from sentence_transformers import SentenceTransformer
import os
from urllib.parse import quote_plus

# MongoDB connection settings
MONGODB_USER = "harithkavish"
MONGODB_PASS = "5Fa83dPSm6_2N2L"
MONGODB_HOST = "nlweb.yzhne.mongodb.net"
MONGODB_DB = "nlweb"

# Construct MongoDB connection string
encoded_password = quote_plus(MONGODB_PASS)
MONGODB_URI = f"mongodb+srv://{MONGODB_USER}:{encoded_password}@{MONGODB_HOST}/{MONGODB_DB}?retryWrites=true&w=majority&ssl=true&tlsAllowInvalidCertificates=false"

async def debug_vector_search():
    try:
        # Initialize MongoDB client
        client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI)
        db = client[MONGODB_DB]
        collection = db.portfolio_vectors
        
        # Initialize embedding model (must match the one used for ingestion)
        model = SentenceTransformer('all-mpnet-base-v2')
        
        # Test query
        query = "What are Harith's programming skills?"
        query_embedding = model.encode(query).tolist()
        
        print(f"🔍 Debugging Vector Search for: '{query}'")
        print("=" * 60)
        
        # Perform vector search
        pipeline = [
            {
                "$vectorSearch": {
                    "index": "vector_index",
                    "path": "embedding",
                    "queryVector": query_embedding,
                    "numCandidates": 100,
                    "limit": 5
                }
            },
            {
                "$project": {
                    "content": 1,
                    "metadata": 1,
                    "score": {"$meta": "vectorSearchScore"}
                }
            }
        ]
        
        results = []
        async for doc in collection.aggregate(pipeline):
            results.append(doc)
        
        print(f"📚 Found {len(results)} documents")
        print()
        
        for i, doc in enumerate(results, 1):
            score = doc.get('score', 0)
            content = doc.get('content', '')
            metadata = doc.get('metadata', {})
            
            print(f"📄 Document {i}:")
            print(f"   Score: {score:.4f}")
            print(f"   Content Length: {len(content)} characters")
            print(f"   Content Preview: {content[:100]}...")
            print(f"   Metadata: {metadata}")
            print(f"   Content (first 200 chars): '{content[:200]}'")
            
            # Check if content passes our threshold
            if score > 0.4 and content.strip():
                print(f"   ✅ PASSES: Score > 0.4 and has content")
            else:
                print(f"   ❌ FAILS: Score: {score} > 0.4? {score > 0.4}, Has content? {bool(content.strip())}")
            print("-" * 40)
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error during vector search debug: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_vector_search())
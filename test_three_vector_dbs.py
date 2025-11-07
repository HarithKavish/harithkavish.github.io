"""
Test the three vector databases with multi-domain search
Run this after the MongoDB Atlas indexes finish building (2-5 minutes)
"""
import os
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

# Load embedding model
print("Loading embedding model...")
embedder = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
print("✓ Model loaded\n")

async def test_vector_search():
    client = AsyncIOMotorClient(os.getenv("MONGODB_URI"))
    db = client["portfolio_db"]
    
    # Test queries
    test_queries = [
        {
            "query": "Who are you?",
            "collection": "assistant_identity",
            "index": "assistant_vector_index",
            "expected": "Should return Neo AI's identity"
        },
        {
            "query": "What projects has Harith built?",
            "collection": "harith_portfolio",
            "index": "portfolio_vector_index",
            "expected": "Should return Harith's projects"
        },
        {
            "query": "What is RAG?",
            "collection": "general_knowledge",
            "index": "knowledge_vector_index",
            "expected": "Should return AI/ML concepts"
        }
    ]
    
    print("="*70)
    print("TESTING THREE VECTOR DATABASES")
    print("="*70 + "\n")
    
    for i, test in enumerate(test_queries, 1):
        print(f"\n🔍 TEST {i}: {test['query']}")
        print(f"   Collection: {test['collection']}")
        print(f"   Expected: {test['expected']}")
        print("   " + "-"*66)
        
        try:
            # Generate query embedding
            query_embedding = embedder.encode(test["query"], normalize_embeddings=True)
            
            # Perform vector search
            collection = db[test["collection"]]
            pipeline = [
                {
                    "$vectorSearch": {
                        "index": test["index"],
                        "path": "embedding",
                        "queryVector": query_embedding.tolist(),
                        "numCandidates": 10,
                        "limit": 3
                    }
                },
                {
                    "$project": {
                        "name": 1,
                        "content": 1,
                        "score": {"$meta": "vectorSearchScore"}
                    }
                }
            ]
            
            results = await collection.aggregate(pipeline).to_list(length=3)
            
            if results:
                print(f"   ✅ Found {len(results)} results:")
                for idx, doc in enumerate(results, 1):
                    name = doc.get('name', 'N/A')
                    score = doc.get('score', 0)
                    content_preview = doc.get('content', '')[:100] + "..."
                    print(f"      {idx}. {name} (score: {score:.4f})")
                    print(f"         {content_preview}\n")
            else:
                print(f"   ❌ No results found!")
                print(f"   ⚠️  Index might still be building. Check MongoDB Atlas.")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            if "index not found" in str(e).lower():
                print(f"   ⚠️  Index '{test['index']}' is still building. Wait 2-5 minutes.")
            elif "namespace not found" in str(e).lower():
                print(f"   ⚠️  Collection '{test['collection']}' not found.")
    
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print("✅ If all tests passed: Your three-vector database system is LIVE!")
    print("⚠️  If tests failed: Wait for indexes to finish building in Atlas")
    print("📊 Check index status: https://cloud.mongodb.com/v2/67e97ed1211fd9376235aa9a#/clusters")
    print("="*70 + "\n")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(test_vector_search())

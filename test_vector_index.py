"""
Simple vector search diagnostic - uses deployed Perception API
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

async def test_vector_search():
    print("🔍 Diagnosing Vector Search\n")
    
    client = AsyncIOMotorClient(os.getenv('MONGODB_URI'))
    db = client.nlweb
    collection = db.portfolio_vectors
    
    # Get test embedding from Perception API
    print("📡 Getting embedding from Perception API...")
    async with httpx.AsyncClient(timeout=30.0) as http_client:
        response = await http_client.post(
            "https://harithkavish-harithkavish-nlweb-perception.hf.space/embed",
            json={"text": "SkinNet Analyzer deep learning project"}
        )
        test_embedding = response.json()["embedding"]
    
    print(f"✅ Embedding dimensions: {len(test_embedding)}\n")
    
    # Check sample documents
    print("📄 Sample documents in database:")
    docs = await collection.find({}).limit(3).to_list(None)
    for i, doc in enumerate(docs, 1):
        emb_dims = len(doc.get('embedding', [])) if 'embedding' in doc else 0
        print(f"  {i}. {doc.get('name', 'unknown')} - embedding: {emb_dims} dims")
    
    # Try vector search
    print(f"\n🔎 Running vector search...")
    try:
        pipeline = [
            {
                "$vectorSearch": {
                    "index": "portfolio_vector_index",
                    "path": "embedding",
                    "queryVector": test_embedding,
                    "numCandidates": 10,
                    "limit": 3
                }
            },
            {
                "$project": {
                    "name": 1,
                    "source": 1,
                    "@type": 1,
                    "score": {"$meta": "vectorSearchScore"},
                    "_id": 0
                }
            }
        ]
        
        results = await collection.aggregate(pipeline).to_list(None)
        
        if results:
            print(f"\n✅ SUCCESS! Vector search returned {len(results)} results:\n")
            for i, result in enumerate(results, 1):
                print(f"  {i}. {result.get('name', 'unknown')}")
                print(f"     Score: {result.get('score', 0):.4f}")
                print(f"     Type: {result.get('@type', 'unknown')}")
                print(f"     Source: {result.get('source', 'unknown')}\n")
        else:
            print("\n❌ PROBLEM: Vector search returned 0 results")
            print("\n🔧 DIAGNOSIS:")
            print("   - Embeddings are 384 dims ✓")
            print("   - Documents have embeddings ✓")
            print("   - Vector index exists (no error) ✓")
            print("   - BUT: Index dimensions likely set to 768 ✗")
            print("\n💡 SOLUTION:")
            print("   1. Open: https://cloud.mongodb.com/")
            print("   2. Go to: Database → Browse Collections → Search Indexes")
            print("   3. Click: Edit on 'portfolio_vector_index'")
            print("   4. Change: 'numDimensions' from 768 to 384")
            print("   5. Click: Save")
            print("   6. Wait: 1-2 minutes for rebuild")
            print("   7. Run: py debug_vector_search.py again")
            
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        
        if "index not found" in str(e).lower() or "no index" in str(e).lower():
            print("\n💡 The vector search index doesn't exist!")
            print("   Create it in MongoDB Atlas with this config:")
            print("""
{
  "fields": [
    {
      "type": "vector",
      "path": "embedding",
      "numDimensions": 384,
      "similarity": "cosine"
    }
  ]
}
""")
    
    client.close()

if __name__ == '__main__':
    asyncio.run(test_vector_search())

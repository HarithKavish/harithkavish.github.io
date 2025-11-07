"""
Detailed MongoDB Atlas Vector Search Diagnostic
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import httpx
import os
from dotenv import load_dotenv
import json

load_dotenv()

async def detailed_diagnostic():
    print("🔬 DETAILED VECTOR SEARCH DIAGNOSTIC\n")
    print("="*70)
    
    client = AsyncIOMotorClient(os.getenv('MONGODB_URI'))
    db = client.nlweb
    collection = db.portfolio_vectors
    
    # Step 1: Check documents
    print("\n1️⃣  CHECKING DOCUMENTS:")
    count = await collection.count_documents({})
    print(f"   Total documents: {count}")
    
    if count > 0:
        sample = await collection.find_one({})
        if sample:
            print(f"   Sample document has 'embedding' field: {'embedding' in sample}")
            if 'embedding' in sample:
                print(f"   Embedding dimensions: {len(sample['embedding'])}")
                print(f"   Embedding type: {type(sample['embedding'])}")
                print(f"   First 5 values: {sample['embedding'][:5]}")
    
    # Step 2: Get embedding from Perception API
    print("\n2️⃣  TESTING PERCEPTION API:")
    async with httpx.AsyncClient(timeout=30.0) as http_client:
        response = await http_client.post(
            "https://harithkavish-harithkavish-nlweb-perception.hf.space/embed",
            json={"text": "test query about SkinNet"}
        )
        query_embedding = response.json()["embedding"]
        print(f"   Query embedding dimensions: {len(query_embedding)}")
        print(f"   Query embedding type: {type(query_embedding)}")
        print(f"   First 5 values: {query_embedding[:5]}")
    
    # Step 3: Try different index names
    print("\n3️⃣  TRYING DIFFERENT INDEX NAMES:")
    
    index_names = [
        "portfolio_vector_index",
        "vector_index", 
        "default",
        "portfolio_vectors"
    ]
    
    for index_name in index_names:
        print(f"\n   Testing index: '{index_name}'")
        try:
            pipeline = [
                {
                    "$vectorSearch": {
                        "index": index_name,
                        "path": "embedding",
                        "queryVector": query_embedding,
                        "numCandidates": 10,
                        "limit": 3
                    }
                },
                {
                    "$project": {
                        "name": 1,
                        "score": {"$meta": "vectorSearchScore"},
                        "_id": 0
                    }
                }
            ]
            
            results = await collection.aggregate(pipeline).to_list(None)
            
            if results:
                print(f"   ✅ SUCCESS! Found {len(results)} results with index '{index_name}'")
                for i, r in enumerate(results, 1):
                    print(f"      {i}. {r.get('name')} (score: {r.get('score', 0):.4f})")
                break
            else:
                print(f"   ⚠️  No results with index '{index_name}'")
                
        except Exception as e:
            error_msg = str(e)
            if "index not found" in error_msg.lower():
                print(f"   ❌ Index '{index_name}' does not exist")
            else:
                print(f"   ❌ Error: {error_msg[:100]}")
    
    # Step 4: List actual indexes (if possible)
    print("\n4️⃣  CHECKING ACTUAL INDEXES:")
    try:
        indexes = await collection.list_indexes().to_list(None)
        print(f"   Found {len(indexes)} indexes:")
        for idx in indexes:
            print(f"      - {idx.get('name', 'unknown')}")
    except Exception as e:
        print(f"   Cannot list indexes: {e}")
    
    print("\n" + "="*70)
    print("\n💡 RECOMMENDATIONS:")
    print("   1. Verify in MongoDB Atlas UI that index shows 'Active' status")
    print("   2. Check index name is exactly 'portfolio_vector_index'")
    print("   3. Verify index type is 'Vector Search' (not 'Atlas Search')")
    print("   4. Confirm dimensions are set to 384")
    print("   5. Try deleting and recreating the index if issue persists")
    
    client.close()

if __name__ == '__main__':
    asyncio.run(detailed_diagnostic())

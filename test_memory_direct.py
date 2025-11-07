"""
Test Memory Layer directly to see what's happening
"""

import httpx
import asyncio

MEMORY_API = "https://harithkavish-harithkavish-nlweb-memory.hf.space"
PERCEPTION_API = "https://harithkavish-harithkavish-nlweb-perception.hf.space"

async def test_memory_layer():
    print("🧪 Testing Memory Layer directly\n")
    
    # Get embedding
    print("1. Getting embedding from Perception API...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{PERCEPTION_API}/embed",
            json={"text": "SkinNet Analyzer"}
        )
        embedding = response.json()["embedding"]
        print(f"   ✓ Got {len(embedding)}-dim embedding\n")
    
    # Call Memory Layer
    print("2. Calling Memory Layer /search...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{MEMORY_API}/search",
                json={"embedding": embedding, "top_k": 3}
            )
            
            result = response.json()
            print(f"   Response: {result}\n")
            
            if result.get('count', 0) > 0:
                print(f"✅ SUCCESS! Found {result['count']} results:")
                for i, doc in enumerate(result['results'], 1):
                    print(f"  {i}. Score: {doc.get('score', 0):.4f}")
                    print(f"     Content preview: {doc.get('content', 'N/A')[:100]}...")
            else:
                print("❌ Memory Layer returned 0 results")
                print("\n💡 Possible causes:")
                print("   1. VECTOR_INDEX env var might be wrong")
                print("   2. Index still rebuilding")
                print("   3. Index name mismatch")
                
        except Exception as e:
            print(f"   ✗ Error: {str(e)}")

if __name__ == '__main__':
    asyncio.run(test_memory_layer())

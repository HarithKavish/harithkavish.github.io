import httpx

# Test Perception API
r = httpx.post(
    'https://harithkavish-harithkavish-nlweb-perception.hf.space/embed',
    json={'text': 'test'},
    timeout=10
)

embedding = r.json()["embedding"]
print(f'Perception API embedding dims: {len(embedding)}')

# Check MongoDB vector index
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from dotenv import load_dotenv
import os

load_dotenv()

async def check_index():
    client = AsyncIOMotorClient(os.getenv('MONGODB_URI'))
    db = client.nlweb
    collection = db.portfolio_vectors
    
    # Get one document
    doc = await collection.find_one({})
    if doc and 'embedding' in doc:
        print(f'MongoDB embedding dims: {len(doc["embedding"])}')
        print(f'Sample doc: {doc.get("name", "unknown")}')
    else:
        print('No documents with embeddings found!')
    
    # Check collection stats
    count = await collection.count_documents({})
    print(f'Total documents: {count}')
    
    client.close()

asyncio.run(check_index())

"""
Clear MongoDB and re-upload ALL data with 384-dim embeddings from Perception API
"""

import asyncio
import httpx
import json
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

PERCEPTION_API = "https://harithkavish-harithkavish-nlweb-perception.hf.space"
MONGODB_URI = os.getenv('MONGODB_URI')

async def get_embedding(text: str) -> list:
    """Get 384-dim embedding from Perception API"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{PERCEPTION_API}/embed",
            json={"text": text}
        )
        response.raise_for_status()
        return response.json()["embedding"]

async def rebuild_database():
    print("🔄 Rebuilding MongoDB with 384-dim embeddings\n")
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client.nlweb
    collection = db.portfolio_vectors
    
    # Step 1: Clear collection
    print("🗑️  Clearing existing documents...")
    result = await collection.delete_many({})
    print(f"✅ Deleted {result.deleted_count} documents\n")
    
    # Step 2: Load all data sources
    all_data = []
    
    # Load portfolio data (if exists)
    portfolio_file = "portfolio_data.jsonl"
    if os.path.exists(portfolio_file):
        print(f"📂 Loading {portfolio_file}...")
        with open(portfolio_file, 'r', encoding='utf-8') as f:
            for line in f:
                data = json.loads(line.strip())
                all_data.append(("portfolio", data))
        print(f"✅ Loaded {len(all_data)} portfolio items\n")
    
    # Load GitHub projects
    github_file = "github_projects.json"
    if os.path.exists(github_file):
        print(f"📂 Loading {github_file}...")
        with open(github_file, 'r', encoding='utf-8') as f:
            projects = json.load(f)
            for project in projects:
                all_data.append(("github", project))
        print(f"✅ Loaded {len(projects)} GitHub projects\n")
    
    # Step 3: Upload with new embeddings
    print(f"📤 Uploading {len(all_data)} items with 384-dim embeddings...\n")
    
    uploaded = 0
    for i, (source, data) in enumerate(all_data, 1):
        try:
            # Prepare text
            if source == "portfolio":
                # Portfolio data
                text_parts = []
                for field in ['name', 'description', 'jobTitle', 'alternateName', 
                              'about', 'applicationCategory', 'applicationSubCategory']:
                    if field in data and data[field]:
                        text_parts.append(str(data[field]))
                
                if 'keywords' in data:
                    if isinstance(data['keywords'], list):
                        text_parts.extend(data['keywords'])
                    else:
                        text_parts.append(str(data['keywords']))
                
                text = ' '.join(text_parts)
                metadata = data
                doc_type = data.get('@type', 'Thing')
                name = data.get('name', f'Item {i}')
                
            else:  # github
                text = data['content']
                metadata = data['metadata']
                doc_type = 'SoftwareSourceCode'
                name = metadata['name']
            
            print(f"[{i}/{len(all_data)}] {name}")
            
            # Get embedding
            print(f"  Generating embedding...", end='', flush=True)
            embedding = await get_embedding(text)
            print(f" ✓ ({len(embedding)} dims)")
            
            # Prepare document
            document = {
                'text': text,
                'embedding': embedding,
                'metadata': metadata,
                '@type': doc_type,
                'name': name,
                'source': source
            }
            
            # Insert
            print(f"  Uploading...", end='', flush=True)
            await collection.insert_one(document)
            print(" ✓\n")
            
            uploaded += 1
            
        except Exception as e:
            print(f" ✗ Error: {e}\n")
    
    # Summary
    total = await collection.count_documents({})
    print(f"\n{'='*60}")
    print(f"✅ Database Rebuilt!")
    print(f"{'='*60}")
    print(f"Uploaded: {uploaded}")
    print(f"Total documents: {total}")
    print(f"Embedding dimensions: 384")
    print(f"\n⚠️  IMPORTANT: Update vector index to 384 dimensions in MongoDB Atlas!")
    print(f"   Index name: portfolio_vector_index")
    print(f"   Dimensions: 384")
    print(f"   Similarity: cosine")
    
    client.close()

if __name__ == '__main__':
    asyncio.run(rebuild_database())

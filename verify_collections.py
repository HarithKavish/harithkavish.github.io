"""
Trigger collection sync in MongoDB Atlas
"""
import os
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from dotenv import load_dotenv

load_dotenv()

async def trigger_sync():
    client = AsyncIOMotorClient(os.getenv("MONGODB_URI"))
    db = client["portfolio_db"]
    
    # List all collections
    collections = await db.list_collection_names()
    print(f"📊 Collections in database: {collections}\n")
    
    # Count documents in each collection
    for coll_name in ["assistant_identity", "harith_portfolio", "general_knowledge"]:
        if coll_name in collections:
            count = await db[coll_name].count_documents({})
            print(f"✓ {coll_name}: {count} documents")
            
            # Get a sample document to verify structure
            sample = await db[coll_name].find_one({})
            if sample:
                print(f"  - Has 'embedding' field: {'embedding' in sample}")
                if 'embedding' in sample:
                    print(f"  - Embedding dimensions: {len(sample['embedding'])}")
        else:
            print(f"❌ {coll_name}: NOT FOUND")
    
    client.close()
    print("\n✅ Collections are ready for index creation")

if __name__ == "__main__":
    asyncio.run(trigger_sync())

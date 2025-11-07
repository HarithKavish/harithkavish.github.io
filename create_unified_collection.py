"""
Create a SINGLE unified collection with domain field instead of three separate collections
This avoids the 3-index limit on MongoDB Atlas Free tier
"""
import os
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from dotenv import load_dotenv

load_dotenv()

async def create_unified_collection():
    client = AsyncIOMotorClient(os.getenv("MONGODB_URI"))
    db = client["portfolio_db"]
    
    # New unified collection
    unified_coll = db["portfolio_unified"]
    
    print("🔄 Creating unified collection...")
    
    # Clear existing
    await unified_coll.delete_many({})
    
    # Copy from assistant_identity
    print("   Copying assistant_identity...")
    docs = await db["assistant_identity"].find({}).to_list(None)
    for doc in docs:
        doc.pop('_id', None)
        doc['domain'] = 'assistant'
    if docs:
        await unified_coll.insert_many(docs)
        print(f"   ✓ {len(docs)} assistant documents")
    
    # Copy from harith_portfolio
    print("   Copying harith_portfolio...")
    docs = await db["harith_portfolio"].find({}).to_list(None)
    for doc in docs:
        doc.pop('_id', None)
        doc['domain'] = 'portfolio'
    if docs:
        await unified_coll.insert_many(docs)
        print(f"   ✓ {len(docs)} portfolio documents")
    
    # Copy from general_knowledge
    print("   Copying general_knowledge...")
    docs = await db["general_knowledge"].find({}).to_list(None)
    for doc in docs:
        doc.pop('_id', None)
        doc['domain'] = 'knowledge'
    if docs:
        await unified_coll.insert_many(docs)
        print(f"   ✓ {len(docs)} knowledge documents")
    
    # Summary
    total = await unified_coll.count_documents({})
    print(f"\n✅ Unified collection created: {total} total documents")
    print(f"   - assistant: {await unified_coll.count_documents({'domain': 'assistant'})}")
    print(f"   - portfolio: {await unified_coll.count_documents({'domain': 'portfolio'})}")
    print(f"   - knowledge: {await unified_coll.count_documents({'domain': 'knowledge'})}")
    
    print("\n📝 Next steps:")
    print("   1. Create ONE vector search index on 'portfolio_unified' collection")
    print("   2. Update Memory Layer to query with domain filters")
    print("   3. This uses only 1 index instead of 3!")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(create_unified_collection())

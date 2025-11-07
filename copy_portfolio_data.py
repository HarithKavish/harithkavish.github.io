"""
Copy portfolio_vectors from nlweb database to portfolio_db.harith_portfolio
"""
import os
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from dotenv import load_dotenv

load_dotenv()

async def copy_portfolio_data():
    client = AsyncIOMotorClient(os.getenv("MONGODB_URI"))
    
    # Source: nlweb.portfolio_vectors
    source_db = client["nlweb"]
    source_coll = source_db["portfolio_vectors"]
    
    # Destination: portfolio_db.harith_portfolio
    dest_db = client["portfolio_db"]
    dest_coll = dest_db["harith_portfolio"]
    
    print("📊 Copying portfolio data...")
    
    # Get all documents from source
    docs = await source_coll.find({}).to_list(None)
    print(f"   Found {len(docs)} documents in nlweb.portfolio_vectors")
    
    if docs:
        # Remove _id for re-insertion
        for doc in docs:
            doc.pop('_id', None)
        
        # Clear destination and insert
        await dest_coll.delete_many({})
        await dest_coll.insert_many(docs)
        print(f"   ✓ Copied {len(docs)} documents to portfolio_db.harith_portfolio")
    else:
        print("   ❌ No documents found to copy")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(copy_portfolio_data())

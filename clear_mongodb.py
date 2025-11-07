"""
Clear MongoDB and start fresh
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def clear_mongodb():
    print("🗑️  Clearing MongoDB Database\n")
    
    client = AsyncIOMotorClient(os.getenv('MONGODB_URI'))
    db = client.nlweb
    
    # Collections to clear
    collections = ['portfolio_vectors', 'conversation_history']
    
    for coll_name in collections:
        print(f"Clearing collection: {coll_name}")
        collection = db[coll_name]
        
        # Count before
        count_before = await collection.count_documents({})
        print(f"  Documents before: {count_before}")
        
        if count_before > 0:
            # Delete all
            result = await collection.delete_many({})
            print(f"  ✅ Deleted: {result.deleted_count} documents")
        else:
            print(f"  Already empty")
        print()
    
    # Verify
    print("📊 Final Status:")
    for coll_name in collections:
        collection = db[coll_name]
        count = await collection.count_documents({})
        print(f"  {coll_name}: {count} documents")
    
    client.close()
    
    print("\n✅ MongoDB cleared!")
    print("\n📋 Next Steps:")
    print("   1. Delete the old vector search index in MongoDB Atlas UI")
    print("   2. Run: py rebuild_with_384dims.py  (to re-upload all data)")
    print("   3. Create NEW vector search index with 384 dimensions")
    print("   4. Test: py test_vector_index.py")

if __name__ == '__main__':
    asyncio.run(clear_mongodb())

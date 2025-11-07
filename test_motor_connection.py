"""
Test Motor (async MongoDB driver) connection
"""
import os
import asyncio
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import certifi

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
print(f"MongoDB URI loaded: {MONGODB_URI[:50]}...")

async def test_motor_connection():
    print("\n--- Test 1: Motor with default settings ---")
    try:
        client = AsyncIOMotorClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        await client.admin.command('ping')
        print("✓ Motor connection successful!")
        
        # Test query
        db = client["nlweb"]
        collection = db["portfolio_vectors"]
        count = await collection.count_documents({})
        print(f"✓ Collection has {count} documents")
        
        client.close()
    except Exception as e:
        print(f"✗ Failed: {type(e).__name__}: {str(e)[:300]}")
    
    print("\n--- Test 2: Motor with SSL context ---")
    try:
        import ssl
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        
        client = AsyncIOMotorClient(
            MONGODB_URI,
            serverSelectionTimeoutMS=5000,
            tlsCAFile=certifi.where()
        )
        await client.admin.command('ping')
        print("✓ Motor with SSL context successful!")
        client.close()
    except Exception as e:
        print(f"✗ Failed: {type(e).__name__}: {str(e)[:300]}")

if __name__ == "__main__":
    asyncio.run(test_motor_connection())

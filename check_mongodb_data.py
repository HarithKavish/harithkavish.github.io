"""
Simple debug script to check if MongoDB has any portfolio data
"""
import asyncio
import motor.motor_asyncio
from urllib.parse import quote_plus

# MongoDB connection string from the working HF deployment
MONGODB_URI = "mongodb+srv://harithkavish40:K11nPy9sv9ron4eQ@cluster0.wmcojpw.mongodb.net/nlweb?retryWrites=true&w=majority&appName=Cluster0"

async def check_mongodb_data():
    try:
        # Initialize MongoDB client
        client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI)
        db = client["nlweb"]
        collection = db.portfolio_vectors
        
        print("🔍 Checking MongoDB Portfolio Data")
        print("=" * 50)
        
        # Check if collection exists and has documents
        doc_count = await collection.count_documents({})
        print(f"📊 Total documents in portfolio_vectors: {doc_count}")
        
        if doc_count == 0:
            print("❌ PROBLEM: MongoDB collection is EMPTY!")
            print("   This means no portfolio data was ingested.")
            print("   You need to run the ingestion script to populate the database.")
            return
        
        # Get a few sample documents to see their structure
        print(f"\n📄 Sample documents:")
        async for doc in collection.find({}).limit(3):
            print(f"   Document ID: {doc.get('_id')}")
            print(f"   Content length: {len(doc.get('content', ''))}")
            print(f"   Content preview: {doc.get('content', '')[:100]}...")
            print(f"   Metadata: {doc.get('metadata', {})}")
            print(f"   Has embedding: {'embedding' in doc}")
            if 'embedding' in doc:
                print(f"   Embedding length: {len(doc['embedding'])}")
            print("-" * 30)
        
        # Check for specific portfolio items
        print(f"\n🔎 Searching for specific portfolio items:")
        
        # Look for SkinNet Analyzer
        skinnet_docs = await collection.count_documents({"content": {"$regex": "SkinNet", "$options": "i"}})
        print(f"   Documents mentioning 'SkinNet': {skinnet_docs}")
        
        # Look for Object Detector
        object_detector_docs = await collection.count_documents({"content": {"$regex": "Object Detector", "$options": "i"}})
        print(f"   Documents mentioning 'Object Detector': {object_detector_docs}")
        
        # Look for programming skills
        skills_docs = await collection.count_documents({"content": {"$regex": "programming|skills|Python|JavaScript", "$options": "i"}})
        print(f"   Documents mentioning programming/skills: {skills_docs}")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error connecting to MongoDB: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_mongodb_data())
"""
MongoDB Atlas Setup Script for NLWeb
Creates the necessary database and vector search index
"""

import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    END = '\033[0m'

def setup_mongodb():
    print(f"{Colors.CYAN}🔧 MongoDB Atlas Setup{Colors.END}\n")
    
    # Load environment variables
    load_dotenv('C:/Dev/GitHub/NLWeb/.env')
    
    mongodb_uri = os.getenv('MONGODB_URI')
    if not mongodb_uri or 'YOUR_USERNAME' in mongodb_uri:
        print(f"{Colors.RED}❌ Error: MongoDB URI not configured!{Colors.END}")
        print(f"\nPlease edit: C:\\Dev\\GitHub\\NLWeb\\.env")
        print(f"And replace MONGODB_URI with your actual connection string\n")
        print(f"Get it from: https://cloud.mongodb.com → Connect → Connect your application")
        return False
    
    try:
        # Connect to MongoDB
        print(f"{Colors.YELLOW}Connecting to MongoDB Atlas...{Colors.END}")
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
        
        # Test connection
        client.admin.command('ping')
        print(f"{Colors.GREEN}✓ Successfully connected to MongoDB Atlas!{Colors.END}\n")
        
        # Get database and collection names
        db_name = os.getenv('MONGODB_DATABASE', 'nlweb')
        collection_name = os.getenv('MONGODB_COLLECTION', 'portfolio_vectors')
        
        # Create database and collection
        db = client[db_name]
        collection = db[collection_name]
        
        print(f"{Colors.YELLOW}Database: {db_name}{Colors.END}")
        print(f"{Colors.YELLOW}Collection: {collection_name}{Colors.END}\n")
        
        # Check if collection exists
        if collection_name in db.list_collection_names():
            doc_count = collection.count_documents({})
            print(f"{Colors.GREEN}✓ Collection already exists with {doc_count} documents{Colors.END}\n")
        else:
            # Create collection with a sample document
            collection.insert_one({"_init": True})
            collection.delete_one({"_init": True})
            print(f"{Colors.GREEN}✓ Collection created!{Colors.END}\n")
        
        # Instructions for Vector Search Index
        print(f"{Colors.CYAN}📋 Vector Search Index Setup{Colors.END}\n")
        print(f"To enable vector search, you need to create a Search Index in MongoDB Atlas:\n")
        print(f"{Colors.YELLOW}Steps:{Colors.END}")
        print(f"1. Go to: https://cloud.mongodb.com")
        print(f"2. Navigate to your cluster → 'Atlas Search' tab")
        print(f"3. Click 'Create Search Index'")
        print(f"4. Choose 'JSON Editor'")
        print(f"5. Use this configuration:\n")
        
        index_config = """{
  "mappings": {
    "dynamic": true,
    "fields": {
      "embedding": {
        "type": "knnVector",
        "dimensions": 768,
        "similarity": "cosine"
      },
      "text": {
        "type": "string"
      },
      "metadata": {
        "type": "document",
        "dynamic": true
      }
    }
  }
}"""
        
        print(f"{Colors.CYAN}{index_config}{Colors.END}\n")
        print(f"6. Set Index Name: {Colors.YELLOW}vector_index{Colors.END}")
        print(f"7. Database: {Colors.YELLOW}{db_name}{Colors.END}")
        print(f"8. Collection: {Colors.YELLOW}{collection_name}{Colors.END}")
        print(f"9. Click 'Create Search Index'\n")
        
        print(f"{Colors.GREEN}✅ MongoDB setup complete!{Colors.END}\n")
        print(f"After creating the index, run: python nlweb_ingest_data.py\n")
        
        return True
        
    except Exception as e:
        print(f"{Colors.RED}❌ Error: {str(e)}{Colors.END}\n")
        return False

if __name__ == '__main__':
    setup_mongodb()

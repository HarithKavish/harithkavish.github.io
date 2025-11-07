"""
List all search indexes in MongoDB Atlas
"""
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGODB_URI"))

# Check nlweb database
print("\n📊 Indexes in nlweb database:")
db = client["nlweb"]
for coll_name in db.list_collection_names():
    coll = db[coll_name]
    indexes = list(coll.list_indexes())
    if indexes:
        print(f"\n  Collection: {coll_name}")
        for idx in indexes:
            print(f"    - {idx['name']}: {idx.get('key', {})}")

# Check portfolio_db database
print("\n📊 Indexes in portfolio_db database:")
db = client["portfolio_db"]
for coll_name in db.list_collection_names():
    coll = db[coll_name]
    indexes = list(coll.list_indexes())
    if indexes:
        print(f"\n  Collection: {coll_name}")
        for idx in indexes:
            print(f"    - {idx['name']}: {idx.get('key', {})}")

client.close()
print("\n✅ Done")

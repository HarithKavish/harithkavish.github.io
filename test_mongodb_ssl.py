"""
Debug MongoDB Atlas SSL connection
"""
import os
from dotenv import load_dotenv
from pymongo import MongoClient
import ssl
import certifi

# Load environment variables
load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
print(f"MongoDB URI loaded: {MONGODB_URI[:50]}...")

print(f"\nSSL Info:")
print(f"- OpenSSL version: {ssl.OPENSSL_VERSION}")
print(f"- Certifi CA bundle: {certifi.where()}")

print("\n--- Test 1: Basic connection with default settings ---")
try:
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    print("✓ Success with default settings!")
    client.close()
except Exception as e:
    print(f"✗ Failed: {type(e).__name__}: {str(e)[:200]}")

print("\n--- Test 2: Connection with explicit TLS settings ---")
try:
    client = MongoClient(
        MONGODB_URI,
        serverSelectionTimeoutMS=5000,
        tls=True,
        tlsAllowInvalidCertificates=False
    )
    client.admin.command('ping')
    print("✓ Success with TLS settings!")
    client.close()
except Exception as e:
    print(f"✗ Failed: {type(e).__name__}: {str(e)[:200]}")

print("\n--- Test 3: Connection with certifi CA bundle ---")
try:
    client = MongoClient(
        MONGODB_URI,
        serverSelectionTimeoutMS=5000,
        tls=True,
        tlsCAFile=certifi.where()
    )
    client.admin.command('ping')
    print("✓ Success with certifi CA bundle!")
    
    # If successful, test a query
    db = client["nlweb"]
    collection = db["portfolio_vectors"]
    count = collection.count_documents({})
    print(f"✓ Collection has {count} documents")
    
    client.close()
except Exception as e:
    print(f"✗ Failed: {type(e).__name__}: {str(e)[:200]}")

print("\n--- Test 4: Connection allowing invalid certificates (NOT RECOMMENDED for production) ---")
try:
    client = MongoClient(
        MONGODB_URI,
        serverSelectionTimeoutMS=5000,
        tls=True,
        tlsAllowInvalidCertificates=True
    )
    client.admin.command('ping')
    print("✓ Success with invalid certificates allowed!")
    client.close()
except Exception as e:
    print(f"✗ Failed: {type(e).__name__}: {str(e)[:200]}")

"""
MongoDB Atlas Connection Helper
This script will guide you through getting and testing your MongoDB connection
"""

import webbrowser
import time

print("\n" + "="*60)
print("MongoDB Atlas Connection Setup")
print("="*60 + "\n")

print("Step 1: Opening MongoDB Atlas in your browser...")
print("Please log in to your account\n")

webbrowser.open("https://cloud.mongodb.com")
time.sleep(2)

print("\nStep 2: Get your connection string")
print("-" * 60)
print("In MongoDB Atlas:")
print("1. Click 'Database' in the left sidebar")
print("2. Click 'Connect' button on your cluster")
print("3. Choose 'Drivers' (not Compass or Shell)")
print("4. Select 'Python' as driver")
print("5. Copy the connection string\n")

print("It will look like:")
print("mongodb+srv://username:<password>@cluster0.xxxxx.mongodb.net/\n")

print("Step 3: Replace <password> with your actual password\n")

print("Step 4: Paste it below:")
connection_string = input("MongoDB Connection String: ").strip()

if not connection_string or connection_string == "":
    print("\n❌ No connection string provided!")
    print("Please run this script again and paste your connection string.\n")
    exit(1)

# Update .env file
print("\n✅ Updating .env file...")
env_path = r"C:\Dev\GitHub\NLWeb\.env"

with open(env_path, 'r') as f:
    content = f.read()

# Replace the placeholder
content = content.replace(
    'MONGODB_URI=mongodb+srv://YOUR_USERNAME:YOUR_PASSWORD@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority',
    f'MONGODB_URI={connection_string}'
)

with open(env_path, 'w') as f:
    f.write(content)

print("✅ Configuration updated!\n")

# Test connection
print("Testing connection...")
try:
    from pymongo import MongoClient
    client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    print("✅ Successfully connected to MongoDB Atlas!\n")
    
    # Show databases
    dbs = client.list_database_names()
    print(f"Available databases: {', '.join(dbs)}\n")
    
    print("="*60)
    print("✅ Setup Complete!")
    print("="*60)
    print("\nNext steps:")
    print("1. Run: python C:\\Dev\\GitHub\\harithkavish_github_io\\nlweb_setup_mongodb.py")
    print("2. Create Vector Search Index in Atlas (follow instructions)")
    print("3. Run: python C:\\Dev\\GitHub\\harithkavish_github_io\\nlweb_ingest_data.py\n")
    
except Exception as e:
    print(f"❌ Connection failed: {str(e)}\n")
    print("Common issues:")
    print("- Wrong password in connection string")
    print("- IP address not whitelisted")
    print("  → Go to Network Access → Add IP Address → Add Current IP")
    print("- Cluster not ready (wait a few minutes)\n")

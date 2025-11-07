"""
Atlas Vector Search Index Creator
Opens Atlas UI and guides you through creating the index
"""

import webbrowser
import json

print("\n" + "="*70)
print("Creating Vector Search Index in MongoDB Atlas")
print("="*70 + "\n")

# The JSON configuration
index_config = {
    "mappings": {
        "dynamic": True,
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
                "dynamic": True
            }
        }
    }
}

print("✅ Data ingested: 6 documents with embeddings")
print("✅ Database: nlweb")
print("✅ Collection: portfolio_vectors\n")

print("Now creating Vector Search Index...\n")

print("Opening MongoDB Atlas Search page...")
webbrowser.open("https://cloud.mongodb.com")

print("\n" + "-"*70)
print("MANUAL STEPS IN ATLAS UI:")
print("-"*70)
print("\n1. Click on your cluster (Cluster0)")
print("2. Click 'Atlas Search' tab (or 'Search' tab)")
print("3. Click 'Create Search Index' button")
print("4. Choose 'JSON Editor' option")
print("5. In the configuration box, paste this JSON:\n")

# Pretty print the JSON
print(json.dumps(index_config, indent=2))

print("\n6. Set these values:")
print("   - Index Name: vector_index")
print("   - Database: nlweb")
print("   - Collection: portfolio_vectors")
print("\n7. Click 'Create Search Index'")
print("\n8. Wait 1-2 minutes for the index to build (status will show 'Active')\n")

print("="*70)
print("After the index is 'Active', press Enter to continue...")
input()

print("\n✅ Great! Vector Search Index should be ready.")
print("\n Next: Testing NLWeb locally...")
print("\nCommands to run:")
print("1. cd C:\\Dev\\GitHub\\NLWeb")
print("2. Start server (I'll do this for you)\n")

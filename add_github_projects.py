"""
Add Harith Kavish's GitHub projects to MongoDB for RAG
Fetches repos and creates embeddings for vector search
"""

import os
import requests
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from sentence_transformers import SentenceTransformer
import asyncio

# Configuration
GITHUB_USERNAME = "HarithKavish"
GITHUB_API = f"https://api.github.com/users/{GITHUB_USERNAME}/repos"

# MongoDB Config
MONGO_URI = os.getenv("MONGODB_URI")
if not MONGO_URI:
    print("⚠️  MONGODB_URI environment variable not set")
    print("💡 You can:")
    print("   1. Set it: $env:MONGODB_URI = 'your_uri_here'")
    print("   2. Or edit this file and paste your URI directly")
    MONGO_URI = input("\n📝 Enter your MongoDB URI: ").strip()

DB_NAME = "portfolio_chatbot"
COLLECTION_NAME = "portfolio_data"

# Initialize embedding model
print("🔄 Loading embedding model...")
embedder = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
print("✅ Model loaded!")


def fetch_github_repos():
    """Fetch all public repositories from GitHub."""
    print(f"\n📡 Fetching repos for {GITHUB_USERNAME}...")
    
    repos = []
    page = 1
    
    while True:
        response = requests.get(
            GITHUB_API,
            params={"page": page, "per_page": 100, "sort": "updated"},
            headers={"Accept": "application/vnd.github.v3+json"}
        )
        
        if response.status_code != 200:
            print(f"❌ GitHub API error: {response.status_code}")
            break
        
        page_repos = response.json()
        if not page_repos:
            break
        
        repos.extend(page_repos)
        page += 1
    
    print(f"✅ Found {len(repos)} repositories")
    return repos


def create_project_document(repo):
    """Convert GitHub repo to MongoDB document with embedding."""
    
    # Build comprehensive description
    description = repo.get('description', '') or f"{repo['name']} - A project by Harith Kavish"
    
    topics = repo.get('topics', [])
    language = repo.get('language', 'Unknown')
    stars = repo.get('stargazers_count', 0)
    
    # Enhanced content for better RAG
    content = f"""
Project: {repo['name']}
Creator: Harith Kavish
Description: {description}
Primary Language: {language}
Topics: {', '.join(topics) if topics else 'General'}
Stars: {stars}
GitHub: {repo['html_url']}
"""
    
    if repo.get('homepage'):
        content += f"Live Demo: {repo['homepage']}\n"
    
    # Generate embedding
    embedding = embedder.encode(content).tolist()
    
    # Create document
    document = {
        "content": content.strip(),
        "embedding": embedding,
        "metadata": {
            "@context": "https://schema.org",
            "@type": "SoftwareSourceCode",
            "name": repo['name'],
            "description": description,
            "author": {
                "@type": "Person",
                "name": "Harith Kavish",
                "url": f"https://github.com/{GITHUB_USERNAME}"
            },
            "programmingLanguage": language,
            "codeRepository": repo['html_url'],
            "keywords": topics,
            "dateCreated": repo['created_at'],
            "dateModified": repo['updated_at'],
            "stars": stars,
            "forks": repo.get('forks_count', 0),
            "url": repo.get('homepage', repo['html_url'])
        },
        "source": "github",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    return document


async def upload_to_mongodb(documents):
    """Upload documents to MongoDB Atlas."""
    print(f"\n📤 Uploading {len(documents)} projects to MongoDB...")
    
    try:
        client = AsyncIOMotorClient(MONGO_URI)
        await client.admin.command('ping')
        print("✅ Connected to MongoDB Atlas")
        
        collection = client[DB_NAME][COLLECTION_NAME]
        
        # Insert documents
        if documents:
            # Remove existing GitHub projects to avoid duplicates
            delete_result = await collection.delete_many({"source": "github"})
            print(f"🗑️  Removed {delete_result.deleted_count} old GitHub projects")
            
            # Insert new ones
            result = await collection.insert_many(documents)
            print(f"✅ Inserted {len(result.inserted_ids)} new projects")
            
            # Verify count
            total = await collection.count_documents({})
            github_count = await collection.count_documents({"source": "github"})
            print(f"📊 Total documents in database: {total}")
            print(f"📊 GitHub projects: {github_count}")
        
        await client.close()
        
    except Exception as e:
        print(f"❌ MongoDB error: {e}")
        raise


async def main():
    """Main function."""
    print("="*60)
    print("🚀 GitHub Projects → MongoDB Vector Database")
    print("="*60)
    
    # Fetch repos
    repos = fetch_github_repos()
    
    if not repos:
        print("❌ No repositories found!")
        return
    
    # Filter and process repos (optional: filter out forks, archived, etc.)
    active_repos = [
        repo for repo in repos 
        if not repo.get('fork', False)  # Exclude forks
        and not repo.get('archived', False)  # Exclude archived
    ]
    
    print(f"\n🔧 Processing {len(active_repos)} active repositories...")
    
    # Create documents
    documents = []
    for i, repo in enumerate(active_repos, 1):
        print(f"  [{i}/{len(active_repos)}] {repo['name']}...", end=' ')
        doc = create_project_document(repo)
        documents.append(doc)
        print("✓")
    
    # Upload to MongoDB
    await upload_to_mongodb(documents)
    
    print("\n" + "="*60)
    print("✅ COMPLETE! Your GitHub projects are now in MongoDB")
    print("="*60)
    print("\n📝 Next steps:")
    print("   1. Ensure your MongoDB vector index exists")
    print("   2. Test the chatbot with project-related questions")
    print("   3. The RAG system will now use your GitHub data!")


if __name__ == "__main__":
    asyncio.run(main())

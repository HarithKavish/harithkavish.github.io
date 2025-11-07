"""
Fetch Harith Kavish's GitHub projects and prepare for MongoDB
This version just fetches and displays - you add embeddings via the Memory Layer API
"""

import requests
import json

# Configuration
GITHUB_USERNAME = "HarithKavish"
GITHUB_API = f"https://api.github.com/users/{GITHUB_USERNAME}/repos"


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


def create_project_data(repo):
    """Convert GitHub repo to structured data."""
    
    description = repo.get('description', '') or f"{repo['name']} - A project by Harith Kavish"
    topics = repo.get('topics', [])
    language = repo.get('language', 'Unknown')
    stars = repo.get('stargazers_count', 0)
    
    # Enhanced content for RAG
    content = f"""Harith Kavish created {repo['name']}, {description}. 
This project uses {language} and has {stars} stars on GitHub. 
{f"Technologies: {', '.join(topics)}" if topics else ''}
View it at {repo['html_url']}"""
    
    if repo.get('homepage'):
        content += f". Live demo: {repo['homepage']}"
    
    # Create document (without embedding - that's done by API)
    document = {
        "content": content.strip(),
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
        "source": "github"
    }
    
    return document


def main():
    """Main function."""
    print("="*60)
    print("🚀 GitHub Projects Extractor for Harith Kavish")
    print("="*60)
    
    # Fetch repos
    repos = fetch_github_repos()
    
    if not repos:
        print("❌ No repositories found!")
        return
    
    # Filter active repos
    active_repos = [
        repo for repo in repos 
        if not repo.get('fork', False)
        and not repo.get('archived', False)
    ]
    
    print(f"\n🔧 Processing {len(active_repos)} active repositories...")
    
    # Create documents
    documents = []
    for i, repo in enumerate(active_repos, 1):
        print(f"\n[{i}/{len(active_repos)}] {repo['name']}")
        print(f"   Language: {repo.get('language', 'Unknown')}")
        print(f"   Stars: {repo.get('stargazers_count', 0)}")
        desc = repo.get('description') or 'No description'
        print(f"   Description: {desc[:60]}...")
        
        doc = create_project_data(repo)
        documents.append(doc)
    
    # Save to JSON
    output_file = "github_projects.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(documents, f, indent=2, ensure_ascii=False)
    
    print("\n" + "="*60)
    print(f"✅ Saved {len(documents)} projects to {output_file}")
    print("="*60)
    
    print("\n📝 Next steps:")
    print("   1. Review the generated github_projects.json file")
    print("   2. Use the nlweb_ingest_data.py script to upload to MongoDB")
    print("   3. Or manually import via MongoDB Compass")
    print(f"\n📊 Summary:")
    print(f"   - Total repos fetched: {len(repos)}")
    print(f"   - Active (non-fork, non-archived): {len(active_repos)}")
    print(f"   - Documented projects: {len(documents)}")


if __name__ == "__main__":
    main()

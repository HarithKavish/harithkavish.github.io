"""
Upload GitHub Projects to MongoDB using deployed Perception API
"""

import json
import os
import motor.motor_asyncio
import asyncio
import httpx
from dotenv import load_dotenv

# Colors for output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    GRAY = '\033[90m'
    END = '\033[0m'

# Load environment
load_dotenv()

# Configuration
MONGODB_URI = os.getenv('MONGODB_URI')
PERCEPTION_API = "https://harithkavish-harithkavish-nlweb-perception.hf.space"
GITHUB_PROJECTS_FILE = "github_projects.json"

async def get_embedding(text: str) -> list:
    """Get embedding from deployed Perception API"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{PERCEPTION_API}/embed",
            json={"text": text}
        )
        response.raise_for_status()
        return response.json()["embedding"]

async def upload_projects():
    print(f"{Colors.CYAN}📤 Uploading GitHub Projects to MongoDB{Colors.END}\n")
    
    # Check MongoDB URI
    if not MONGODB_URI or 'mongodb+srv' not in MONGODB_URI:
        print(f"{Colors.RED}❌ Error: MONGODB_URI not configured in .env{Colors.END}")
        return
    
    # Load GitHub projects
    print(f"{Colors.YELLOW}📂 Loading {GITHUB_PROJECTS_FILE}...{Colors.END}")
    with open(GITHUB_PROJECTS_FILE, 'r', encoding='utf-8') as f:
        projects = json.load(f)
    
    print(f"{Colors.GREEN}✓ Loaded {len(projects)} projects{Colors.END}\n")
    
    # Connect to MongoDB
    print(f"{Colors.YELLOW}🔗 Connecting to MongoDB...{Colors.END}")
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI)
    db = client.nlweb
    collection = db.portfolio_vectors
    print(f"{Colors.GREEN}✓ Connected!{Colors.END}\n")
    
    # Process each project
    uploaded = 0
    errors = 0
    
    for i, project in enumerate(projects, 1):
        try:
            # Get project info
            name = project['metadata']['name']
            print(f"{Colors.CYAN}[{i}/{len(projects)}] {name}{Colors.END}")
            
            # Generate text for embedding
            text = project['content']
            
            # Get embedding from Perception API
            print(f"{Colors.GRAY}    Generating embedding via Perception API...{Colors.END}", end='', flush=True)
            embedding = await get_embedding(text)
            print(f"{Colors.GREEN} ✓ ({len(embedding)} dims){Colors.END}")
            
            # Prepare document
            document = {
                'text': text,
                'embedding': embedding,
                'metadata': project['metadata'],
                '@type': 'SoftwareSourceCode',
                'name': name,
                'source': 'github'
            }
            
            # Insert into MongoDB
            print(f"{Colors.GRAY}    Uploading to MongoDB...{Colors.END}", end='', flush=True)
            await collection.insert_one(document)
            print(f"{Colors.GREEN} ✓{Colors.END}")
            
            uploaded += 1
            print(f"{Colors.GREEN}✓ Uploaded: {name}{Colors.END}\n")
            
        except Exception as e:
            errors += 1
            print(f"{Colors.RED} ✗ Error: {str(e)}{Colors.END}\n")
    
    # Summary
    print(f"\n{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.GREEN}✅ Upload Complete!{Colors.END}")
    print(f"{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"✓ Uploaded: {Colors.GREEN}{uploaded}{Colors.END}")
    print(f"✗ Errors: {Colors.RED}{errors}{Colors.END}")
    
    # Check total count
    total = await collection.count_documents({})
    print(f"📊 Total documents in MongoDB: {Colors.YELLOW}{total}{Colors.END}\n")
    
    client.close()

if __name__ == '__main__':
    asyncio.run(upload_projects())

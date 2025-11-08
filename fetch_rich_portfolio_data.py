"""
Fetch rich portfolio data from GitHub repos and profile page.
Creates a curated dataset with detailed content for better RAG performance.
"""
import os
import json
import requests
from bs4 import BeautifulSoup
import time
from dotenv import load_dotenv

load_dotenv()

# Try to import sentence transformers, but make it optional
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except Exception as e:
    print(f"⚠️  Warning: Could not import SentenceTransformer: {e}")
    print("   Embeddings will be generated during MongoDB upload instead.\n")
    EMBEDDINGS_AVAILABLE = False

# Configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USERNAME = "HarithKavish"
PROFILE_URL = "https://harithkavish.github.io/HarithKavish/"

# Priority repos (curated list - real projects only)
PRIORITY_REPOS = [
    "SkinNet-Analyzer",
    "Multi-Object-Detection-using-YOLO",
    "harithkavish.github.io",
    "AgroCloud-Finance-Pro",
    "Online-Tutoring-Platform",
    "Hands-on_-_Cloud_Computing_using_AWS",
    "Road-Contract-App"
]

headers = {}
if GITHUB_TOKEN:
    headers["Authorization"] = f"token {GITHUB_TOKEN}"

def fetch_github_readme(repo_name):
    """Fetch README content from a GitHub repository."""
    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}/readme"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            readme_data = response.json()
            # Get the download URL for raw content
            download_url = readme_data.get('download_url')
            if download_url:
                readme_response = requests.get(download_url)
                if readme_response.status_code == 200:
                    return readme_response.text
        return None
    except Exception as e:
        print(f"  ⚠️  Error fetching README for {repo_name}: {e}")
        return None

def fetch_repo_details(repo_name):
    """Fetch repository details from GitHub API."""
    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"  ⚠️  Error fetching repo details for {repo_name}: {e}")
        return None

def fetch_profile_page():
    """Fetch content from Harith's profile page."""
    try:
        response = requests.get(PROFILE_URL)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract text content
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text
            text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text
        return None
    except Exception as e:
        print(f"  ⚠️  Error fetching profile page: {e}")
        return None

def clean_readme_content(readme_text):
    """Clean and extract meaningful content from README."""
    if not readme_text:
        return ""
    
    # Remove common markdown artifacts
    lines = readme_text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        line = line.strip()
        # Skip empty lines, image tags, and excessive markdown
        if line and not line.startswith('![') and not line.startswith('<!--'):
            # Remove markdown headers
            if line.startswith('#'):
                line = line.lstrip('#').strip()
            cleaned_lines.append(line)
    
    content = ' '.join(cleaned_lines)
    
    # Limit content length (first 1500 chars for embedding quality)
    if len(content) > 1500:
        content = content[:1500] + "..."
    
    return content

def build_curated_dataset():
    """Build curated portfolio dataset with rich content."""
    print("🚀 Building Curated Portfolio Dataset\n")
    
    dataset = []
    
    # 1. Add Neo AI Identity
    print("📝 Adding Neo AI Identity...")
    neo_identity = {
        "content": """Neo AI is Harith Kavish's intelligent portfolio assistant, powered by a sophisticated multi-agent RAG (Retrieval-Augmented Generation) system. Neo AI specializes in providing detailed, accurate information about Harith's work, projects, skills, and experience. The system uses specialized layers including Perception (embedding and intent classification), Memory (vector database search across three domains: assistant identity, portfolio projects, and general knowledge), Reasoning (LLM-powered response generation using FLAN-T5), Safety (content validation), and Orchestration (coordinating all services). Neo AI can answer questions about Harith's AI/ML projects, full-stack development work, technical skills in Python, TensorFlow, PyTorch, React, and more. The assistant provides complete, detailed answers with source citations and maintains a conversational, professional tone while always speaking about Harith in third person.""",
        "metadata": {
            "@type": "SoftwareApplication",
            "name": "Neo AI",
            "applicationCategory": "Portfolio Assistant",
            "description": "Intelligent AI assistant for Harith Kavish's portfolio using multi-agent RAG architecture",
            "author": "Harith Kavish",
            "keywords": "AI Assistant, RAG System, Portfolio Chatbot, Multi-Agent Architecture, Natural Language Processing",
            "capabilities": "Answer questions about projects, skills, experience, provide technical details, cite sources"
        }
    }
    dataset.append(neo_identity)
    print("  ✓ Neo AI identity added\n")
    
    # 2. Add Harith's Profile Information
    print("📄 Fetching profile page...")
    profile_content = fetch_profile_page()
    if profile_content:
        # Extract key sections
        profile_doc = {
            "content": f"""Harith Kavish is an AI Developer and Full-Stack Engineer specializing in machine learning, deep learning, computer vision, and intelligent application development. He has expertise in Python, TensorFlow, PyTorch, Keras, scikit-learn for AI/ML work, and modern web technologies including React, Node.js, JavaScript, HTML/CSS for full-stack development. Harith has experience with cloud computing (AWS, Azure), DevOps tools, database systems (MongoDB, MySQL, PostgreSQL), and version control with Git/GitHub. His work spans multiple domains including healthcare AI (medical image analysis), computer vision (object detection, facial recognition), NLP applications, and full-stack web platforms. {profile_content[:800]}""",
            "metadata": {
                "@type": "Person",
                "name": "Harith Kavish",
                "jobTitle": "AI Developer",
                "alternateName": "Full-Stack Engineer",
                "description": "AI Developer and Full-Stack Engineer specializing in machine learning, deep learning, computer vision, and intelligent application development",
                "url": "https://harithkavish.github.io/",
                "sameAs": ["https://github.com/HarithKavish", "https://www.linkedin.com/in/harithkavish/"],
                "knowsAbout": "Machine Learning, Deep Learning, Computer Vision, NLP, Full-Stack Development, Python, TensorFlow, PyTorch, React, AWS",
                "skills": "Python, TensorFlow, PyTorch, Keras, scikit-learn, React, Node.js, JavaScript, AWS, MongoDB, MySQL"
            }
        }
        dataset.append(profile_doc)
        print("  ✓ Profile information added\n")
    
    # 3. Fetch Priority Repos with READMEs
    print("📚 Fetching priority repositories...\n")
    for repo_name in PRIORITY_REPOS:
        print(f"  🔍 Processing: {repo_name}")
        
        # Get repo details
        repo_details = fetch_repo_details(repo_name)
        if not repo_details:
            print(f"    ⚠️  Skipped (API error)\n")
            continue
        
        # Get README
        readme_content = fetch_github_readme(repo_name)
        cleaned_readme = clean_readme_content(readme_content)
        
        # Build rich content
        description = repo_details.get('description', '') or ''
        language = repo_details.get('language', 'Unknown') or 'Unknown'
        topics = repo_details.get('topics', []) or []
        stars = repo_details.get('stargazers_count', 0) or 0
        
        # Combine all information
        full_content = f"{repo_name}: {description}"
        if cleaned_readme:
            full_content += f" {cleaned_readme}"
        
        if not full_content.strip() or len(full_content) < 50:
            print(f"    ⚠️  Skipped (insufficient content)\n")
            continue
        
        # Determine project category
        topics_str = ', '.join(topics) if topics else ''
        category = "SoftwareApplication"
        subcategory = "Development Tool"
        
        if "healthcare" in description.lower() or "medical" in description.lower() or "skin" in repo_name.lower():
            category = "SoftwareApplication"
            subcategory = "Healthcare AI"
        elif "yolo" in repo_name.lower() or "detection" in description.lower() or "vision" in description.lower():
            category = "SoftwareApplication"
            subcategory = "Computer Vision"
        elif "cloud" in repo_name.lower() or "aws" in description.lower():
            category = "LearningResource"
            subcategory = "Cloud Computing"
        elif "tutoring" in repo_name.lower() or "platform" in description.lower():
            category = "SoftwareApplication"
            subcategory = "Web Application"
        
        project_doc = {
            "content": full_content,
            "metadata": {
                "@type": category,
                "name": repo_name.replace('-', ' ').replace('_', ' '),
                "applicationCategory": subcategory,
                "description": description,
                "programmingLanguage": language,
                "url": f"https://github.com/{GITHUB_USERNAME}/{repo_name}",
                "codeRepository": f"https://github.com/{GITHUB_USERNAME}/{repo_name}",
                "keywords": topics_str if topics_str else language,
                "author": "Harith Kavish",
                "stars": stars
            }
        }
        
        dataset.append(project_doc)
        print(f"    ✓ Added ({len(full_content)} chars)\n")
        
        # Rate limiting
        time.sleep(0.5)
    
    # 4. Add Skills and Expertise Documents
    print("🎯 Adding skills and expertise...")
    
    skills_doc = {
        "content": """Harith Kavish's technical skills include: AI/ML frameworks - TensorFlow, PyTorch, Keras, scikit-learn for building deep learning models; Computer Vision - OpenCV, YOLO, CNNs for object detection and image analysis; NLP - transformers, BERT, GPT for natural language processing; Web Development - React, Node.js, JavaScript, HTML/CSS, RESTful APIs; Backend - Python FastAPI, Flask, Java Spring Boot; Databases - MongoDB, MySQL, PostgreSQL, vector databases; Cloud & DevOps - AWS (EC2, S3, Lambda), Docker, Git/GitHub; Tools - Jupyter, VS Code, Postman, Linux/Windows environments. He has hands-on experience in medical AI (skin disease detection), computer vision (multi-object detection), full-stack web applications (tutoring platforms, financial systems), and cloud infrastructure setup.""",
        "metadata": {
            "@type": "ItemList",
            "name": "Technical Skills & Expertise",
            "description": "Comprehensive technical skill set and areas of expertise",
            "itemListElement": [
                "Python", "TensorFlow", "PyTorch", "Keras", "scikit-learn",
                "Computer Vision", "Deep Learning", "Machine Learning", "NLP",
                "React", "Node.js", "JavaScript", "FastAPI", "Spring Boot",
                "MongoDB", "AWS", "Docker", "Git"
            ]
        }
    }
    dataset.append(skills_doc)
    
    expertise_doc = {
        "content": """Harith Kavish specializes in several key areas: Healthcare AI - developing medical imaging systems for skin disease detection using convolutional neural networks and transfer learning; Computer Vision - building real-time object detection systems using YOLO architecture, image classification, and facial recognition; Full-Stack Development - creating complete web applications with React frontends and Node.js/Python backends; Cloud Computing - hands-on AWS experience including EC2 instances, S3 storage, IAM configuration, and serverless architectures; AI/ML Engineering - designing and training deep learning models for various applications from medical diagnosis to autonomous systems. He combines theoretical knowledge with practical implementation skills to build production-ready intelligent applications.""",
        "metadata": {
            "@type": "CreativeWork",
            "name": "Areas of Expertise",
            "description": "Specialized domains and professional expertise",
            "keywords": "Healthcare AI, Computer Vision, Medical Imaging, Object Detection, Full-Stack Development, Cloud Architecture, Machine Learning Engineering"
        }
    }
    dataset.append(expertise_doc)
    print("  ✓ Skills and expertise added\n")
    
    return dataset

def save_dataset(dataset, filename="curated_portfolio_data.jsonl"):
    """Save dataset to JSONL file."""
    print(f"💾 Saving dataset to {filename}...")
    
    with open(filename, 'w', encoding='utf-8') as f:
        for doc in dataset:
            f.write(json.dumps(doc, ensure_ascii=False) + '\n')
    
    print(f"  ✓ Saved {len(dataset)} documents\n")

def generate_embeddings(dataset):
    """Generate embeddings for the dataset."""
    if not EMBEDDINGS_AVAILABLE:
        print("⚠️  Skipping embedding generation (will be done during upload)\n")
        return dataset
    
    print("🧮 Generating embeddings...")
    
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    
    for i, doc in enumerate(dataset):
        # Combine content and metadata for embedding
        text_for_embedding = doc['content']
        if doc['metadata'].get('description'):
            text_for_embedding += " " + doc['metadata']['description']
        
        embedding = model.encode(text_for_embedding, convert_to_tensor=False)
        doc['embedding'] = embedding.tolist()
        
        print(f"  ✓ Generated embedding {i+1}/{len(dataset)}")
    
    print("\n✅ All embeddings generated!\n")
    return dataset

if __name__ == "__main__":
    print("=" * 80)
    print("CURATED PORTFOLIO DATASET BUILDER")
    print("=" * 80 + "\n")
    
    # Build dataset
    dataset = build_curated_dataset()
    
    # Generate embeddings
    dataset_with_embeddings = generate_embeddings(dataset)
    
    # Save to file
    save_dataset(dataset_with_embeddings)
    
    print("=" * 80)
    print("✅ DATASET CREATION COMPLETE!")
    print("=" * 80)
    print(f"\n📊 Summary:")
    print(f"  • Total documents: {len(dataset)}")
    print(f"  • File: curated_portfolio_data.jsonl")
    print(f"\n🔧 Next steps:")
    print(f"  1. Clear old MongoDB data: py clear_mongodb.py")
    print(f"  2. Upload new data: py upload_curated_data.py")
    print(f"  3. Rebuild vector indexes in MongoDB Atlas")
    print(f"  4. Test the chatbot!")

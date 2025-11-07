"""
Setup Three Vector Databases in MongoDB Atlas
1. assistant_identity - Information about the chatbot itself
2. harith_portfolio - Information about Harith and his projects
3. general_knowledge - General tech/AI knowledge and external context
"""
from motor.motor_asyncio import AsyncIOMotorClient
from sentence_transformers import SentenceTransformer
import os
import asyncio
from datetime import datetime

# MongoDB configuration
MONGO_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME", "nlweb")

# Collections
ASSISTANT_COLLECTION = "assistant_identity"
PORTFOLIO_COLLECTION = "harith_portfolio"
KNOWLEDGE_COLLECTION = "general_knowledge"

# Initialize embedding model
print("Loading embedding model...")
embedder = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
print("✓ Model loaded")

# Assistant Identity Data
ASSISTANT_DATA = [
    {
        "name": "Neo AI - Introduction",
        "content": """Neo AI is Harith Kavish's intelligent portfolio assistant, designed to provide 
        comprehensive information about Harith's work, skills, and projects. Neo AI uses advanced 
        RAG (Retrieval-Augmented Generation) technology with a multi-agent architecture to deliver 
        accurate, contextual responses.""",
        "metadata": {
            "@type": "AssistantProfile",
            "category": "Identity",
            "tags": ["assistant", "neo-ai", "about-chatbot"]
        }
    },
    {
        "name": "Neo AI - Capabilities",
        "content": """Neo AI can answer questions about Harith Kavish's technical skills, projects, 
        experience, and expertise. The assistant provides detailed information about his AI/ML projects, 
        full-stack development work, and areas of specialization including computer vision, deep learning, 
        and intelligent application development.""",
        "metadata": {
            "@type": "AssistantProfile",
            "category": "Capabilities",
            "tags": ["assistant", "features", "capabilities"]
        }
    },
    {
        "name": "Neo AI - Personality",
        "content": """Neo AI communicates professionally and informatively, always referring to Harith 
        in the third person (he/his). The assistant is helpful, knowledgeable, and focused on showcasing 
        Harith's qualifications and work. Neo AI provides complete, detailed answers and cites sources 
        for transparency.""",
        "metadata": {
            "@type": "AssistantProfile",
            "category": "Personality",
            "tags": ["assistant", "personality", "communication-style"]
        }
    },
    {
        "name": "Neo AI - Technology Stack",
        "content": """Neo AI is built using a sophisticated multi-agent architecture with specialized 
        layers: Perception Layer (MiniLM + BART for NLU), Memory Layer (MongoDB Atlas Vector Search), 
        Reasoning Layer (FLAN-T5 for response generation), Safety Layer (pattern-based validation), 
        and Execution Layer (tool calling). The system uses 384-dimensional embeddings and cosine 
        similarity for semantic search.""",
        "metadata": {
            "@type": "AssistantProfile",
            "category": "Technology",
            "tags": ["assistant", "technology", "architecture"]
        }
    }
]

# General Knowledge Data
GENERAL_KNOWLEDGE = [
    {
        "name": "AI & Machine Learning Overview",
        "content": """Artificial Intelligence (AI) and Machine Learning (ML) are fields focused on 
        creating systems that can learn from data and make intelligent decisions. Key areas include 
        supervised learning, unsupervised learning, reinforcement learning, deep learning, and 
        neural networks. Popular frameworks include TensorFlow, PyTorch, and scikit-learn.""",
        "metadata": {
            "@type": "GeneralKnowledge",
            "category": "AI/ML Concepts",
            "tags": ["ai", "machine-learning", "overview"]
        }
    },
    {
        "name": "Computer Vision Technologies",
        "content": """Computer Vision enables computers to interpret and understand visual information 
        from the world. Key technologies include Convolutional Neural Networks (CNNs), object detection 
        (YOLO, R-CNN), image segmentation, facial recognition, and image classification. Applications 
        range from medical imaging to autonomous vehicles.""",
        "metadata": {
            "@type": "GeneralKnowledge",
            "category": "Computer Vision",
            "tags": ["computer-vision", "cnn", "image-processing"]
        }
    },
    {
        "name": "Full-Stack Development",
        "content": """Full-stack development involves both frontend and backend development. Frontend 
        technologies include HTML, CSS, JavaScript, React, Vue, and Angular. Backend technologies 
        include Node.js, Python (Flask, FastAPI, Django), databases (SQL, NoSQL), and API development. 
        Modern full-stack developers also work with cloud platforms, DevOps, and containerization.""",
        "metadata": {
            "@type": "GeneralKnowledge",
            "category": "Web Development",
            "tags": ["full-stack", "web-development", "frontend", "backend"]
        }
    },
    {
        "name": "RAG Systems",
        "content": """Retrieval-Augmented Generation (RAG) combines information retrieval with language 
        generation. It retrieves relevant documents from a knowledge base using vector search, then 
        uses an LLM to generate contextual responses. Benefits include reduced hallucinations, 
        up-to-date information, and source attribution. Key components are embeddings, vector databases, 
        and language models.""",
        "metadata": {
            "@type": "GeneralKnowledge",
            "category": "RAG/NLP",
            "tags": ["rag", "nlp", "vector-search", "llm"]
        }
    }
]


async def setup_collections():
    """Create and populate the three vector collections"""
    
    if not MONGO_URI:
        print("✗ MONGODB_URI not set in environment")
        return
    
    print(f"\n{'='*60}")
    print("Setting up Three Vector Database Collections")
    print(f"{'='*60}\n")
    
    # Connect to MongoDB
    print("Connecting to MongoDB Atlas...")
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
    
    # Test connection
    await client.admin.command('ping')
    print("✓ Connected to MongoDB\n")
    
    # Collection references
    assistant_coll = db[ASSISTANT_COLLECTION]
    portfolio_coll = db[PORTFOLIO_COLLECTION]
    knowledge_coll = db[KNOWLEDGE_COLLECTION]
    
    # 1. Setup Assistant Identity Collection
    print(f"1️⃣  Setting up {ASSISTANT_COLLECTION}...")
    await assistant_coll.delete_many({})  # Clear existing
    
    assistant_docs = []
    for item in ASSISTANT_DATA:
        embedding = embedder.encode(item["content"], normalize_embeddings=True)
        doc = {
            "name": item["name"],
            "content": item["content"],
            "embedding": embedding.tolist(),
            "metadata": item["metadata"],
            "created_at": datetime.utcnow()
        }
        assistant_docs.append(doc)
    
    if assistant_docs:
        await assistant_coll.insert_many(assistant_docs)
        print(f"   ✓ Inserted {len(assistant_docs)} assistant identity documents")
    
    # 2. Migrate existing portfolio data
    print(f"\n2️⃣  Setting up {PORTFOLIO_COLLECTION}...")
    old_portfolio_coll = db["portfolio_vectors"]
    
    # Copy existing portfolio data to new collection
    existing_docs = await old_portfolio_coll.find({}).to_list(None)
    if existing_docs:
        # Remove _id for re-insertion
        for doc in existing_docs:
            doc.pop('_id', None)
        await portfolio_coll.delete_many({})  # Clear existing
        await portfolio_coll.insert_many(existing_docs)
        print(f"   ✓ Migrated {len(existing_docs)} portfolio documents")
    else:
        print(f"   ⚠️  No existing portfolio data found")
    
    # 3. Setup General Knowledge Collection
    print(f"\n3️⃣  Setting up {KNOWLEDGE_COLLECTION}...")
    await knowledge_coll.delete_many({})  # Clear existing
    
    knowledge_docs = []
    for item in GENERAL_KNOWLEDGE:
        embedding = embedder.encode(item["content"], normalize_embeddings=True)
        doc = {
            "name": item["name"],
            "content": item["content"],
            "embedding": embedding.tolist(),
            "metadata": item["metadata"],
            "created_at": datetime.utcnow()
        }
        knowledge_docs.append(doc)
    
    if knowledge_docs:
        await knowledge_coll.insert_many(knowledge_docs)
        print(f"   ✓ Inserted {len(knowledge_docs)} general knowledge documents")
    
    # Summary
    print(f"\n{'='*60}")
    print("Summary:")
    print(f"{'='*60}")
    print(f"✓ {ASSISTANT_COLLECTION}: {await assistant_coll.count_documents({})} documents")
    print(f"✓ {PORTFOLIO_COLLECTION}: {await portfolio_coll.count_documents({})} documents")
    print(f"✓ {KNOWLEDGE_COLLECTION}: {await knowledge_coll.count_documents({})} documents")
    
    print(f"\n{'='*60}")
    print("Next Steps:")
    print(f"{'='*60}")
    print("1. Create vector search indexes in MongoDB Atlas:")
    print(f"   - Collection: {ASSISTANT_COLLECTION}, Index: assistant_vector_index")
    print(f"   - Collection: {PORTFOLIO_COLLECTION}, Index: portfolio_vector_index")
    print(f"   - Collection: {KNOWLEDGE_COLLECTION}, Index: knowledge_vector_index")
    print("\n2. All indexes should use:")
    print("   - Vector field: embedding")
    print("   - Dimensions: 384")
    print("   - Similarity: cosine")
    print("\n3. Update Memory Layer environment variables")
    
    client.close()
    print("\n✓ Setup complete!")


if __name__ == "__main__":
    asyncio.run(setup_collections())

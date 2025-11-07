"""
Rebuild MongoDB database with proper structure - content in content field, metadata separate
"""
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
import json

# MongoDB connection string
MONGODB_URI = "mongodb+srv://harithkavish40:K11nPy9sv9ron4eQ@cluster0.wmcojpw.mongodb.net/nlweb?retryWrites=true&w=majority&appName=Cluster0"

# Portfolio data with proper structure
PORTFOLIO_DATA = [
    {
        "content": "Harith Kavish is an AI Developer and Full-Stack Engineer specializing in machine learning, deep learning, computer vision, and intelligent application development. He is an expert in Python, TensorFlow, PyTorch, and modern web technologies. His skills include Machine Learning, Deep Learning, Computer Vision, Natural Language Processing, Full-Stack Development, and more. You can find him on GitHub, LinkedIn, Twitter, Instagram, Facebook, HuggingFace, YouTube, Docker Hub, and Discord.",
        "metadata": {
            "type": "Person",
            "name": "Harith Kavish",
            "jobTitle": "AI Developer",
            "alternateName": "Full-Stack Engineer",
            "url": "https://harithkavish.github.io/",
            "category": "profile",
            "gender": "male",
            "pronouns": "he/him/his"
        }
    },
    {
        "content": "SkinNet Analyzer is an advanced AI-powered skin condition detection and analysis system developed by Harith. It uses deep learning and convolutional neural networks to provide real-time skin health assessment with high accuracy. Built with TensorFlow and deployed as a web application for easy access. Key features include real-time skin analysis, AI-powered detection using deep learning CNN, comprehensive health assessment, and a user-friendly interface. This is a health application focused on medical AI technology.",
        "metadata": {
            "type": "Project",
            "name": "SkinNet Analyzer",
            "category": "HealthApplication",
            "subcategory": "Medical AI",
            "url": "https://harithkavish.github.io/SkinNet-Analyzer/",
            "technologies": ["AI", "Machine Learning", "TensorFlow", "Deep Learning", "Computer Vision", "CNN"],
            "features": ["Real-time skin analysis", "AI-powered detection", "Deep learning CNN", "Health assessment", "User-friendly interface"],
            "price": "Free"
        }
    },
    {
        "content": "Object Detector is a multi-object detection application developed by Harith, powered by YOLO (You Only Look Once) algorithm for real-time object recognition, classification, and localization. It is capable of detecting multiple objects simultaneously with high speed and accuracy. The application runs in web browsers and features real-time object detection, YOLO algorithm implementation, multi-object recognition, high-speed processing, and bounding box visualization for detected objects. This computer vision application demonstrates Harith's expertise in real-time AI processing.",
        "metadata": {
            "type": "Project",
            "name": "Object Detector",
            "category": "MultimediaApplication",
            "subcategory": "Computer Vision",
            "url": "https://harithkavish.github.io/Multi-Object-Detection-using-YOLO/",
            "technologies": ["YOLO", "Object Detection", "Computer Vision", "Machine Learning", "Deep Learning", "Real-time Processing"],
            "features": ["Real-time object detection", "YOLO algorithm", "Multi-object recognition", "High-speed processing", "Bounding box visualization"],
            "price": "Free"
        }
    },
    {
        "content": "Harith Kavish's professional portfolio website showcases his AI projects, machine learning applications, full-stack development work, and technical expertise. The website features interactive demonstrations of cutting-edge AI technologies including SkinNet Analyzer for medical AI and Object Detector for computer vision. It serves as a comprehensive showcase of his work in artificial intelligence and web development.",
        "metadata": {
            "type": "Website",
            "name": "Harith Kavish Portfolio",
            "url": "https://harithkavish.github.io/",
            "category": "Portfolio",
            "topics": ["AI Projects", "Machine Learning", "Web Development", "Projects Showcase"]
        }
    },
    {
        "content": "Harith possesses a comprehensive technical skill set covering multiple domains. In AI and Machine Learning, he is proficient in Python, TensorFlow, PyTorch, Keras, scikit-learn, OpenCV, and YOLO. For web development, he has expertise in JavaScript, React, Node.js, HTML, and CSS. His technical abilities extend to DevOps and cloud technologies including Docker, Git, MongoDB, SQL, and REST API development. He specializes in Machine Learning, Deep Learning, Computer Vision, Natural Language Processing (NLP), and Full-Stack Development.",
        "metadata": {
            "type": "Skills",
            "name": "Technical Skills",
            "category": "Expertise",
            "programming_languages": ["Python", "JavaScript"],
            "ai_frameworks": ["TensorFlow", "PyTorch", "Keras", "scikit-learn", "OpenCV", "YOLO"],
            "web_technologies": ["React", "Node.js", "HTML", "CSS"],
            "tools": ["Docker", "Git", "MongoDB", "SQL"],
            "domains": ["Machine Learning", "Deep Learning", "Computer Vision", "NLP", "Full-Stack Development"]
        }
    },
    {
        "content": "Harith has specialized expertise in developing intelligent applications using state-of-the-art AI technologies. His areas of expertise include Artificial Intelligence, Machine Learning Engineering, Deep Learning, Computer Vision, Medical AI applications, Object Detection systems, Image Classification, Neural Networks design and implementation, Model Training and optimization, Model Deployment, Web Application Development, API Development, and Cloud Deployment. He combines theoretical knowledge with practical implementation skills to create innovative AI solutions.",
        "metadata": {
            "type": "Expertise",
            "name": "Areas of Expertise",
            "category": "Professional",
            "domains": [
                "Artificial Intelligence",
                "Machine Learning Engineering",
                "Deep Learning",
                "Computer Vision",
                "Medical AI",
                "Object Detection",
                "Image Classification",
                "Neural Networks",
                "Model Training",
                "Model Deployment",
                "Web Application Development",
                "API Development",
                "Cloud Deployment"
            ]
        }
    }
]

def rebuild_database():
    try:
        print("🔌 Connecting to MongoDB Atlas...")
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=10000)
        client.admin.command('ping')
        print("✓ Connected successfully!\n")
        
        db = client["nlweb"]
        collection = db["portfolio_vectors"]
        
        # Clear existing data
        print("🗑️  Clearing existing collection...")
        result = collection.delete_many({})
        print(f"✓ Deleted {result.deleted_count} old documents\n")
        
        # Initialize embedding model
        print("🤖 Loading embedding model (sentence-transformers/all-mpnet-base-v2)...")
        embedder = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
        print("✓ Embedding model loaded\n")
        
        # Insert new structured data
        print("📝 Inserting new properly structured documents...")
        print("=" * 80)
        
        documents_to_insert = []
        
        for idx, item in enumerate(PORTFOLIO_DATA, 1):
            content = item['content']
            metadata = item['metadata']
            
            print(f"\n{idx}. {metadata['name']}")
            print(f"   Type: {metadata['type']}")
            print(f"   Content length: {len(content)} characters")
            print(f"   Generating embedding...")
            
            # Generate embedding from content
            embedding = embedder.encode(content).tolist()
            print(f"   ✓ Embedding generated ({len(embedding)} dimensions)")
            
            # Create document with proper structure
            document = {
                "content": content,
                "metadata": metadata,
                "embedding": embedding
            }
            
            documents_to_insert.append(document)
        
        # Bulk insert
        print(f"\n📤 Inserting {len(documents_to_insert)} documents into MongoDB...")
        result = collection.insert_many(documents_to_insert)
        print(f"✓ Successfully inserted {len(result.inserted_ids)} documents")
        
        print("\n" + "=" * 80)
        print("✅ Database restructured successfully!")
        print(f"\n📊 Summary:")
        print(f"   Total documents: {collection.count_documents({})}")
        print(f"   Database: nlweb")
        print(f"   Collection: portfolio_vectors")
        
        # Verify structure
        print(f"\n🔍 Verifying structure...")
        sample_doc = collection.find_one({})
        if sample_doc:
            print(f"   ✓ Content field: {'Present' if sample_doc.get('content') else 'Missing'}")
            print(f"   ✓ Metadata field: {'Present' if sample_doc.get('metadata') else 'Missing'}")
            print(f"   ✓ Embedding field: {'Present' if sample_doc.get('embedding') else 'Missing'}")
            if sample_doc.get('content'):
                print(f"   ✓ Content length: {len(sample_doc['content'])} chars")
            if sample_doc.get('embedding'):
                print(f"   ✓ Embedding dimensions: {len(sample_doc['embedding'])}")
        
        client.close()
        print("\n✅ Done! Your MongoDB database now has a proper structure.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 80)
    print("MongoDB Database Restructuring Tool")
    print("=" * 80)
    print("\nThis will:")
    print("  1. Delete all existing documents")
    print("  2. Create new documents with proper structure (content + metadata)")
    print("  3. Generate fresh embeddings for all content")
    print("\n⚠️  WARNING: This will replace all existing data!")
    
    response = input("\nContinue? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        print("\n🚀 Starting database restructuring...\n")
        rebuild_database()
    else:
        print("\n❌ Cancelled. No changes made.")

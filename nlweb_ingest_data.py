"""
Data Ingestion Script for NLWeb
Ingests portfolio data into MongoDB Atlas with vector embeddings
"""

import os
import json
from pymongo import MongoClient
from ollama import Client as OllamaClient
from dotenv import load_dotenv
import time

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    GRAY = '\033[90m'
    END = '\033[0m'

def get_embedding(ollama_client, model, text):
    """Generate embedding using Ollama"""
    try:
        response = ollama_client.embeddings(model=model, prompt=text)
        return response['embedding']
    except Exception as e:
        print(f"{Colors.RED}Error generating embedding: {str(e)}{Colors.END}")
        return None

def ingest_portfolio_data():
    print(f"{Colors.CYAN}📥 NLWeb Data Ingestion{Colors.END}\n")
    
    # Load environment variables
    load_dotenv('C:/Dev/GitHub/NLWeb/.env')
    
    # Get configuration
    mongodb_uri = os.getenv('MONGODB_URI')
    db_name = os.getenv('MONGODB_DATABASE', 'nlweb')
    collection_name = os.getenv('MONGODB_COLLECTION', 'portfolio_vectors')
    ollama_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    embedding_model = os.getenv('OLLAMA_EMBEDDING_MODEL', 'nomic-embed-text')
    
    # Check MongoDB URI
    if not mongodb_uri or 'YOUR_USERNAME' in mongodb_uri:
        print(f"{Colors.RED}❌ Error: MongoDB URI not configured!{Colors.END}")
        print(f"\nPlease edit: C:\\Dev\\GitHub\\NLWeb\\.env")
        return False
    
    try:
        # Connect to MongoDB
        print(f"{Colors.YELLOW}Connecting to MongoDB Atlas...{Colors.END}")
        client = MongoClient(mongodb_uri)
        db = client[db_name]
        collection = db[collection_name]
        print(f"{Colors.GREEN}✓ Connected!{Colors.END}\n")
        
        # Connect to Ollama
        print(f"{Colors.YELLOW}Connecting to Ollama at {ollama_url}...{Colors.END}")
        ollama = OllamaClient(host=ollama_url)
        
        # Test Ollama connection
        try:
            models = ollama.list()
            print(f"{Colors.GREEN}✓ Ollama connected!{Colors.END}")
            print(f"{Colors.GRAY}Using embedding model: {embedding_model}{Colors.END}\n")
        except Exception as e:
            print(f"{Colors.RED}❌ Error: Cannot connect to Ollama!{Colors.END}")
            print(f"Make sure Ollama is running: {Colors.YELLOW}ollama serve{Colors.END}\n")
            return False
        
        # Load portfolio data
        data_file = 'C:/Dev/GitHub/harithkavish_github_io/portfolio_data.jsonl'
        print(f"{Colors.YELLOW}Loading portfolio data...{Colors.END}")
        
        if not os.path.exists(data_file):
            print(f"{Colors.RED}❌ Error: {data_file} not found!{Colors.END}")
            return False
        
        # Clear existing data (optional - comment out if you want to append)
        existing_count = collection.count_documents({})
        if existing_count > 0:
            print(f"{Colors.YELLOW}Found {existing_count} existing documents. Clearing...{Colors.END}")
            collection.delete_many({})
            print(f"{Colors.GREEN}✓ Cleared!{Colors.END}\n")
        
        # Process and ingest data
        print(f"{Colors.CYAN}Processing and ingesting data...{Colors.END}\n")
        
        ingested_count = 0
        with open(data_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    data = json.loads(line.strip())
                    
                    # Create searchable text from Schema.org data
                    text_parts = []
                    
                    # Add all relevant text fields
                    for field in ['name', 'description', 'jobTitle', 'alternateName', 
                                  'about', 'applicationCategory', 'applicationSubCategory']:
                        if field in data and data[field]:
                            text_parts.append(str(data[field]))
                    
                    # Add keywords if present
                    if 'keywords' in data:
                        if isinstance(data['keywords'], list):
                            text_parts.extend(data['keywords'])
                        else:
                            text_parts.append(str(data['keywords']))
                    
                    # Add knowsAbout if present
                    if 'knowsAbout' in data and isinstance(data['knowsAbout'], list):
                        text_parts.extend(data['knowsAbout'])
                    
                    # Add features if present
                    if 'features' in data and isinstance(data['features'], list):
                        text_parts.extend(data['features'])
                    
                    text = ' '.join(text_parts)
                    
                    if not text.strip():
                        print(f"{Colors.YELLOW}⚠ Line {line_num}: No text to embed, skipping{Colors.END}")
                        continue
                    
                    # Display progress
                    item_name = data.get('name', data.get('@type', f'Item {line_num}'))
                    print(f"{Colors.YELLOW}[{line_num}] Processing: {item_name}{Colors.END}")
                    print(f"{Colors.GRAY}    Text length: {len(text)} characters{Colors.END}")
                    
                    # Generate embedding
                    print(f"{Colors.GRAY}    Generating embedding...{Colors.END}", end='', flush=True)
                    start_time = time.time()
                    embedding = get_embedding(ollama, embedding_model, text)
                    elapsed = time.time() - start_time
                    
                    if embedding is None:
                        print(f"{Colors.RED} ✗ Failed{Colors.END}")
                        continue
                    
                    print(f"{Colors.GREEN} ✓ ({elapsed:.2f}s){Colors.END}")
                    print(f"{Colors.GRAY}    Embedding dimensions: {len(embedding)}{Colors.END}")
                    
                    # Prepare document
                    document = {
                        'text': text,
                        'embedding': embedding,
                        'metadata': data,
                        '@type': data.get('@type', 'Thing'),
                        'name': item_name
                    }
                    
                    # Insert into MongoDB
                    print(f"{Colors.GRAY}    Inserting into MongoDB...{Colors.END}", end='', flush=True)
                    collection.insert_one(document)
                    print(f"{Colors.GREEN} ✓{Colors.END}")
                    
                    ingested_count += 1
                    print(f"{Colors.GREEN}✓ [{line_num}] Success: {item_name}{Colors.END}\n")
                    
                except json.JSONDecodeError as e:
                    print(f"{Colors.RED}✗ Line {line_num}: Invalid JSON - {str(e)}{Colors.END}\n")
                except Exception as e:
                    print(f"{Colors.RED}✗ Line {line_num}: Error - {str(e)}{Colors.END}\n")
        
        # Summary
        print(f"\n{Colors.CYAN}{'='*60}{Colors.END}")
        print(f"{Colors.GREEN}✅ Ingestion Complete!{Colors.END}")
        print(f"{Colors.CYAN}{'='*60}{Colors.END}")
        print(f"Documents ingested: {Colors.YELLOW}{ingested_count}{Colors.END}")
        print(f"Database: {Colors.YELLOW}{db_name}{Colors.END}")
        print(f"Collection: {Colors.YELLOW}{collection_name}{Colors.END}")
        print(f"Total documents in collection: {Colors.YELLOW}{collection.count_documents({})}{Colors.END}\n")
        
        print(f"{Colors.CYAN}Next step:{Colors.END}")
        print(f"1. Make sure Vector Search Index is created in MongoDB Atlas")
        print(f"2. Run: {Colors.YELLOW}cd C:\\Dev\\GitHub\\NLWeb{Colors.END}")
        print(f"3. Run: {Colors.YELLOW}python start_server_debug.py{Colors.END}\n")
        
        return True
        
    except Exception as e:
        print(f"{Colors.RED}❌ Error: {str(e)}{Colors.END}\n")
        return False

if __name__ == '__main__':
    ingest_portfolio_data()

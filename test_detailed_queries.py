"""
Test specific project queries to see detailed portfolio responses
"""
import requests
import json

API_URL = "https://harithkavish-nlweb-portfolio-chat.hf.space/chat"

def test_detailed_query(query):
    print(f"🔍 Query: '{query}'")
    print("-" * 60)
    
    try:
        response = requests.post(
            API_URL,
            json={"query": query},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            answer = data.get('response', data.get('answer', 'No response'))
            print(f"📝 Full Response:\n{answer}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    print("\n" + "=" * 80 + "\n")

if __name__ == "__main__":
    print("🧪 Testing Detailed Portfolio Queries")
    print("=" * 80)
    
    # Test specific project queries
    queries = [
        "Tell me about SkinNet Analyzer project",
        "What is the Object Detector application?",
        "What programming languages and technologies does Harith use?",
        "Describe Harith's AI and machine learning projects",
        "What are the key features of Harith's applications?"
    ]
    
    for query in queries:
        test_detailed_query(query)
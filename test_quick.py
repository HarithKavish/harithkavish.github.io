"""
Quick test of orchestrator with GitHub projects
"""

import httpx
import json

ORCHESTRATOR_URL = "https://harithkavish-harithkavish-nlweb-orchestrator.hf.space"

def test_query(query):
    print(f"\n{'='*60}")
    print(f"Query: {query}")
    print('='*60)
    
    response = httpx.post(
        f"{ORCHESTRATOR_URL}/chat",
        json={"query": query},
        timeout=30.0
    )
    
    result = response.json()
    
    # Debug: print full response
    print(f"\n📦 Full response:\n{json.dumps(result, indent=2)}\n")
    
    # Get response text (handle different formats)
    response_text = result.get('response') or result.get('answer') or str(result)
    print(f"\n🤖 Response:\n{response_text}\n")
    
    # Check third-person
    if "Harith" in response_text or "he " in response_text.lower():
        print("✅ Third-person perspective detected!")
    
    # Check project info
    if any(keyword in response_text.lower() for keyword in ['project', 'repository', 'github', 'developed']):
        print("✅ Project information detected!")
    
    print(f"\n📊 Metadata:")
    print(f"  Intent: {result.get('intent', 'unknown')}")
    print(f"  Confidence: {result.get('confidence', 0):.2f}")

# Test queries
queries = [
    "Tell me about Harith's SkinNet Analyzer project",
    "What machine learning projects has Harith worked on?",
    "What is Harith's background?"
]

for query in queries:
    test_query(query)

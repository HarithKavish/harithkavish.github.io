#!/usr/bin/env python3
"""
Debug script to check MongoDB portfolio data and vector search
"""

import asyncio
import aiohttp
import json
from datetime import datetime

API_URL = "https://harithkavish-nlweb-portfolio-chat.hf.space"

async def test_portfolio_data_retrieval():
    """Test what data is actually being retrieved from portfolio"""
    print(f"🔍 Debugging Portfolio Data Retrieval")
    print(f"API: {API_URL}")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        
        # Test specific portfolio-related queries
        test_queries = [
            "What are Harith's programming skills?",
            "Tell me about Harith's projects",
            "What technologies does Harith know?",
            "What is Harith's educational background?",
            "Describe Harith's experience with machine learning"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{i}. 🤖 Testing Query: '{query}'")
            print("-" * 50)
            
            try:
                chat_payload = {
                    "query": query,
                    "top_k": 5
                }
                
                async with session.post(
                    f"{API_URL}/chat",
                    json=chat_payload,
                    timeout=30
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        response_text = data.get('response', 'No response')
                        sources = data.get('sources', [])
                        
                        print(f"   📝 Response: {response_text[:200]}...")
                        print(f"   📚 Sources Found: {len(sources)}")
                        
                        if sources:
                            print(f"   📋 Source Details:")
                            for j, source in enumerate(sources):
                                name = source.get('name', 'Unknown')
                                score = source.get('score', 0)
                                source_type = source.get('type', 'Unknown')
                                print(f"      {j+1}. {name} (Type: {source_type}, Score: {score:.4f})")
                        else:
                            print(f"   ⚠️  No sources found - this suggests:")
                            print(f"      - MongoDB collection might be empty")
                            print(f"      - Vector search not finding matches")
                            print(f"      - Embedding mismatch still exists")
                            
                    else:
                        error_text = await response.text()
                        print(f"   ❌ Request failed: {response.status}")
                        print(f"   📄 Error: {error_text}")
                        
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 DIAGNOSIS:")
    print("If no sources are found, the issue is likely:")
    print("   1. MongoDB collection is empty (no portfolio data ingested)")
    print("   2. Vector index doesn't exist or is misconfigured") 
    print("   3. Embedding model still doesn't match existing data")
    print("   4. Vector search threshold is too high")
    
    print(f"\n💡 NEXT STEPS:")
    print("   1. Check if portfolio data was actually ingested into MongoDB")
    print("   2. Verify vector index exists and has correct dimensions")
    print("   3. Consider re-ingesting data with the new embedding model")

if __name__ == "__main__":
    asyncio.run(test_portfolio_data_retrieval())
#!/usr/bin/env python3
"""
Health check script for NLWeb Portfolio Chat deployment
Tests the HF Space API endpoints to verify everything is working
"""

import asyncio
import aiohttp
import json
from datetime import datetime

API_BASE = "https://harithkavish-nlweb-portfolio-chat.hf.space"

async def test_health_endpoint():
    """Test basic health endpoint"""
    try:
        async with aiohttp.ClientSession() as session:
            print(f"🔍 Testing health endpoint: {API_BASE}/")
            async with session.get(f"{API_BASE}/", timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Health check passed: {data}")
                    return True
                else:
                    print(f"❌ Health check failed: {response.status}")
                    return False
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")
        return False

async def test_detailed_health():
    """Test detailed health endpoint"""
    try:
        async with aiohttp.ClientSession() as session:
            print(f"🔍 Testing detailed health: {API_BASE}/health")
            async with session.get(f"{API_BASE}/health", timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Detailed health: {json.dumps(data, indent=2)}")
                    return True
                else:
                    print(f"❌ Detailed health failed: {response.status}")
                    return False
    except Exception as e:
        print(f"❌ Detailed health error: {str(e)}")
        return False

async def test_chat_endpoint():
    """Test chat endpoint with sample query"""
    try:
        async with aiohttp.ClientSession() as session:
            print(f"🔍 Testing chat endpoint: {API_BASE}/chat")
            
            test_query = {
                "query": "Hello, tell me about Harith's skills",
                "top_k": 5
            }
            
            async with session.post(
                f"{API_BASE}/chat", 
                json=test_query,
                timeout=60
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Chat test passed!")
                    print(f"   Query: {test_query['query']}")
                    print(f"   Response: {data.get('response', 'No response field')[:100]}...")
                    if 'error' in data:
                        print(f"   Note: {data['error']}")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Chat test failed: {response.status}")
                    print(f"   Error: {error_text}")
                    return False
    except Exception as e:
        print(f"❌ Chat test error: {str(e)}")
        return False

async def run_all_tests():
    """Run all health checks"""
    print(f"🚀 NLWeb Portfolio Chat - Health Check")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target: {API_BASE}")
    print("=" * 50)
    
    results = []
    
    # Test basic health
    print("\n1. Basic Health Check:")
    results.append(await test_health_endpoint())
    
    # Wait a moment between tests
    await asyncio.sleep(2)
    
    # Test detailed health
    print("\n2. Detailed Health Check:")
    results.append(await test_detailed_health())
    
    # Wait a moment between tests
    await asyncio.sleep(2)
    
    # Test chat functionality
    print("\n3. Chat Functionality Test:")
    results.append(await test_chat_endpoint())
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 HEALTH CHECK SUMMARY:")
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ ALL TESTS PASSED ({passed}/{total})")
        print("🎉 NLWeb Portfolio Chat is fully operational!")
    else:
        print(f"⚠️  SOME TESTS FAILED ({passed}/{total})")
        print("💡 Check the logs above for details")
        
        if passed == 0:
            print("🔄 Space might still be building. Wait 2-3 minutes and try again.")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)
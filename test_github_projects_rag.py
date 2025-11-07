"""
Test enhanced RAG with GitHub projects data
"""

import asyncio
from playwright.async_api import async_playwright

async def test_github_projects():
    print("🧪 Testing Enhanced RAG with GitHub Projects\n")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Go to portfolio
        print("📍 Navigating to https://harithkavish.github.io...")
        await page.goto('https://harithkavish.github.io')
        await page.wait_for_load_state('networkidle')
        
        # Wait for chatbot widget
        print("⏳ Waiting for chatbot widget...")
        await page.wait_for_selector('#nlweb-chat-widget', timeout=10000)
        
        # Click chat button
        print("💬 Opening chat...")
        await page.click('#nlweb-chat-toggle')
        await page.wait_for_timeout(1000)
        
        # Test queries about projects
        test_queries = [
            "Tell me about Harith's SkinNet Analyzer project",
            "What projects has Harith worked on?",
            "Does Harith have any machine learning projects?",
            "What is the AgroCloud Finance Pro project about?"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{'='*60}")
            print(f"Query {i}: {query}")
            print('='*60)
            
            # Type message
            input_selector = '#nlweb-chat-widget input[type="text"]'
            await page.fill(input_selector, query)
            
            # Send message
            send_button = '#nlweb-chat-widget button[type="submit"]'
            await page.click(send_button)
            
            # Wait for response
            print("⏳ Waiting for response...")
            await page.wait_for_timeout(6000)  # Multi-agent takes ~4-5 seconds
            
            # Get latest response
            messages = await page.query_selector_all('#nlweb-chat-widget .message.bot')
            if messages:
                latest = messages[-1]
                response_text = await latest.inner_text()
                print(f"\n🤖 Response:\n{response_text}\n")
                
                # Check if response mentions third-person
                if "Harith" in response_text or "he " in response_text.lower() or "his " in response_text.lower():
                    print("✅ Third-person perspective detected!")
                else:
                    print("⚠️  No third-person indicators found")
                
                # Check if response has project details
                if any(keyword in response_text.lower() for keyword in ['project', 'github', 'repository', 'developed', 'created']):
                    print("✅ Project information detected!")
            else:
                print("❌ No response received")
        
        print("\n\n✅ Test complete! Browser will stay open for manual inspection...")
        await page.wait_for_timeout(30000)  # Keep browser open 30 seconds
        
        await browser.close()

if __name__ == '__main__':
    asyncio.run(test_github_projects())

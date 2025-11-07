"""
Test the new natural conversation style responses
"""
import requests
import time

API_URL = "https://harithkavish-nlweb-portfolio-chat.hf.space/chat"

def test_natural_response(query):
    print(f"🗣️  Query: '{query}'")
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
            
            print(f"🤖 Natural Response:\n{answer}")
            
            # Check for natural conversation indicators
            natural_indicators = {
                "Uses conversational language": any(phrase in answer.lower() for phrase in [
                    "really", "quite", "pretty", "seems like", "what's", "i find", "feel free"
                ]),
                "Personal/engaging tone": any(phrase in answer.lower() for phrase in [
                    "impressive", "fascinating", "interesting", "cool", "valuable", "talented"
                ]),
                "Natural transitions": any(phrase in answer for phrase in [
                    "What's", "From what I can see", "His work shows", "What I find"
                ]),
                "Conversational flow": not answer.startswith("Based on") and not answer.startswith("Here's"),
                "Avoids robotic formatting": "From " not in answer[:50]  # Check if it doesn't start with technical formatting
            }
            
            print(f"\n📊 Natural Language Indicators:")
            for indicator, present in natural_indicators.items():
                status = "✅" if present else "❌"
                print(f"   {status} {indicator}")
                
            natural_score = sum(natural_indicators.values())
            print(f"\n🎯 Naturalness Score: {natural_score}/5")
            
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    print("\n" + "=" * 80 + "\n")

if __name__ == "__main__":
    print("🗣️  TESTING NATURAL CONVERSATION STYLE")
    print("=" * 80)
    
    # Wait a moment for deployment
    print("⏳ Waiting for HuggingFace Space to update...")
    time.sleep(20)
    
    # Test various query types for natural responses
    queries = [
        "What projects has Harith built?",
        "Tell me about his AI skills",
        "What technologies does he know?", 
        "Show me his health applications",
        "Describe his machine learning experience",
        "What's his background?"
    ]
    
    for query in queries:
        test_natural_response(query)
import requests

services = {
    'perception': 'harithkavish-harithkavish-nlweb-perception',
    'memory': 'harithkavish-harithkavish-nlweb-memory',
    'reasoning': 'harithkavish-harithkavish-nlweb-reasoning',
    'execution': 'harithkavish-harithkavish-nlweb-execution',
    'monitoring': 'harithkavish-harithkavish-nlweb-monitoring',
    'orchestrator': 'harithkavish-harithkavish-nlweb-orchestrator'
}

print("🧪 Testing all microservices...\n")

for name, url in services.items():
    try:
        r = requests.get(f"https://{url}.hf.space/health", timeout=10)
        status = "✅" if r.status_code == 200 else "❌"
        print(f"{status} {name.capitalize()}: {r.status_code}")
        if r.status_code == 200:
            print(f"   URL: https://{url}.hf.space")
    except Exception as e:
        print(f"❌ {name.capitalize()}: Error - {str(e)[:50]}")

print("\n📝 Correct API URLs for orchestrator configuration:")
print(f"PERCEPTION_API=https://harithkavish-harithkavish-nlweb-perception.hf.space")
print(f"MEMORY_API=https://harithkavish-harithkavish-nlweb-memory.hf.space")
print(f"REASONING_API=https://harithkavish-harithkavish-nlweb-reasoning.hf.space")
print(f"EXECUTION_API=https://harithkavish-harithkavish-nlweb-execution.hf.space")
print(f"MONITORING_API=https://harithkavish-harithkavish-nlweb-monitoring.hf.space")

"""Fix retriever.py to add proper MongoDB support."""
import re

# Read the file
with open(r"C:\Dev\GitHub\NLWeb\code\python\core\retriever.py", "r", encoding="utf-8") as f:
    content = f.read()

# Fix the mangled elif block
old_pattern = r'_preloaded_modules\[db_type\] = BingSearchClient`n\s*elif db_type == "mongodb":`n\s*from retrieval_providers\.mongodb_client import\s*MongoDBVectorClient`n\s*_preloaded_modules\[db_type\] = MongoDBVectorClient'

new_block = '''_preloaded_modules[db_type] = BingSearchClient
                elif db_type == "mongodb":
                    from retrieval_providers.mongodb_client import MongoDBVectorClient
                    _preloaded_modules[db_type] = MongoDBVectorClient'''

content = re.sub(old_pattern, new_block, content)

# Fix the mangled package dict entry  
old_pkg_pattern = r'"bing_search": \["httpx>=0\.28\.1"\],.*?`n\s*"mongodb": \["pymongo>=4\.0\.0", "motor>=3\.0\.0"\],'

new_pkg = '''    "bing_search": ["httpx>=0.28.1"],  # Bing search uses httpx for API calls
    "mongodb": ["pymongo>=4.0.0", "motor>=3.0.0"],'''

content = re.sub(old_pkg_pattern, new_pkg, content, flags=re.DOTALL)

# Write back
with open(r"C:\Dev\GitHub\NLWeb\code\python\core\retriever.py", "w", encoding="utf-8") as f:
    f.write(content)

print("✓ Fixed retriever.py")

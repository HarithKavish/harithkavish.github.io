import re

# Read the old app.py
with open('nlweb-hf-deployment/app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract widget JS code
match = re.search(r'@app\.get\("/widget\.js"\).*?js_content = """(.+?)"""', content, re.DOTALL)
if match:
    widget_code = match.group(1)
    # Replace old API URL with dynamic origin
    widget_code = widget_code.replace(
        "'https://harithkavish-nlweb-portfolio-chat.hf.space'",
        "window.location.origin"
    )
    widget_code = widget_code.replace(
        "https://harithkavish-nlweb-portfolio-chat.hf.space",
        "' + window.location.origin + '"
    )
    
    # Save to temp file for inspection
    with open('widget_extracted.js', 'w', encoding='utf-8') as f:
        f.write(widget_code)
    
    print(f"✅ Extracted {len(widget_code)} characters")
    print(f"✅ Saved to widget_extracted.js")
else:
    print("❌ Could not find widget code")

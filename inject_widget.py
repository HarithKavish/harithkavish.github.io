import re

# Read extracted widget
with open('widget_extracted.js', 'r', encoding='utf-8') as f:
    widget_code = f.read()

# Read orchestrator app.py  
with open('spaces/orchestrator/app.py', 'r', encoding='utf-8') as f:
    app_content = f.read()

# Find and replace the widget endpoint function
pattern = r'@app\.get\("/widget\.js"\).*?return Response\([^)]+\)'
replacement = f'''@app.get("/widget.js")
async def widget_javascript():
    """Serve the embeddable JavaScript widget."""
    js_content = """{widget_code}"""
    return Response(content=js_content, media_type="application/javascript; charset=utf-8")'''

new_content = re.sub(pattern, replacement, app_content, flags=re.DOTALL)

# Write back
with open('spaces/orchestrator/app.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✅ Widget code injected into orchestrator/app.py")
print(f"✅ Widget size: {len(widget_code)} characters")

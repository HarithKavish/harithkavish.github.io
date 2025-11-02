# Neo AI Widget - Auto-Loading System

## 🎯 Overview
The **Neo AI - Harith Kavish's Assistant** chatbot widget now automatically loads on **ALL pages** across `harithkavish.github.io` and its subpages without requiring manual embedding.

## ✨ How It Works

### Automatic Loading
The widget is automatically injected via `script.js`, which is already included on all your pages:

```javascript
// Auto-load Neo AI Chatbot Widget
// Located in script.js (lines 169-189)
(function() {
    if (window.NeoAIWidgetLoaded) return;
    window.NeoAIWidgetLoaded = true;

    const widgetScript = document.createElement('script');
    widgetScript.src = 'https://harithkavish-nlweb-portfolio-chat.hf.space/widget.js';
    widgetScript.async = true;
    widgetScript.defer = true;
    
    widgetScript.onerror = function() {
        console.warn('Neo AI widget failed to load - continuing without chatbot');
    };
    
    document.head.appendChild(widgetScript);
    console.log('✅ Neo AI widget auto-loader initialized');
})();
```

### Pages That Get the Widget
✅ **Main page**: https://harithkavish.github.io/  
✅ **HarithKavish**: https://harithkavish.github.io/HarithKavish/  
✅ **SkinNet-Analyzer**: https://harithkavish.github.io/SkinNet-Analyzer/  
✅ **Object Detection**: https://harithkavish.github.io/Multi-Object-Detection-using-YOLO/  
✅ **Any future pages** that include `script.js`

## 🎨 Features

### 1. **Automatic Dark Theme Detection**
- Reads `localStorage.getItem('theme')`
- Automatically switches between light/dark modes
- Syncs with your page theme in real-time

### 2. **Zero Manual Setup**
- No need to add `<script>` tags to individual pages
- Widget appears automatically on page load
- Works across all subdomains and paths

### 3. **Graceful Degradation**
- If widget fails to load, page continues normally
- Error is logged to console, not shown to users
- No impact on page performance or functionality

### 4. **Global API Access**
Every page with the widget gets access to:
```javascript
window.PortfolioChatbot.open()      // Open chat window
window.PortfolioChatbot.close()     // Close chat window
window.PortfolioChatbot.toggle()    // Toggle chat window
window.PortfolioChatbot.sendMessage("Your question")  // Send programmatic message
```

## 🛠️ Configuration

### To Add Widget to New Pages
Simply include `script.js` in your HTML:
```html
<script src="script.js"></script>
```

That's it! The widget will automatically load.

### To Disable Widget on Specific Pages
Add this **before** loading `script.js`:
```html
<script>
    window.NeoAIWidgetLoaded = true; // Prevents auto-loading
</script>
<script src="script.js"></script>
```

### To Customize Widget Position (Future)
Currently positioned at `bottom: 20px; right: 20px;`  
To customize, modify the CSS in `nlweb-hf-deployment/app.py` lines 423-434.

## 📋 Maintenance

### Files Involved
1. **script.js** (Lines 169-189)  
   - Contains auto-loader logic
   - Loads on every page that includes this file

2. **nlweb-hf-deployment/app.py** (Widget source)  
   - Contains widget JavaScript and CSS
   - Hosted on HuggingFace Space
   - Auto-updates when pushed to HF Space

3. **index.html** (and other pages)  
   - No longer needs manual `<script>` tag for widget
   - Widget loads automatically via `script.js`

### How to Update Widget
1. Edit `nlweb-hf-deployment/app.py`
2. Commit and push to HuggingFace Space
3. Widget updates globally within 1-2 minutes
4. No changes needed on individual pages

## 🚀 Benefits

| Aspect | Before | After |
|--------|--------|-------|
| **Setup** | Manual `<script>` tag on each page | Automatic on all pages |
| **Maintenance** | Update multiple pages | Update once in script.js |
| **New Pages** | Remember to add widget | Widget appears automatically |
| **Consistency** | Risk of missing pages | Guaranteed on all pages |
| **Updates** | May miss pages during updates | All pages update together |

## 🎉 Result
**Neo AI - Harith Kavish's Assistant** is now a **universal chatbot** that appears on every page of your portfolio, providing consistent AI-powered assistance across your entire site!

---

**Last Updated**: November 2, 2025  
**Auto-Loader Version**: 1.0  
**Widget Source**: https://harithkavish-nlweb-portfolio-chat.hf.space/widget.js

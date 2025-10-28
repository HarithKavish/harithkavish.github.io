# Theme Persistence Across GitHub Pages Subpaths

This guide explains how to maintain dark/light theme preferences across different pages and subpaths in your GitHub Pages site (e.g., `/` and `/Multi-Object-Detection-using-YOLO/`).

## 🎯 Problem

GitHub Pages doesn't automatically share state between different subpaths. When you toggle dark mode on your main portfolio (`harithkavish.github.io/`), the preference doesn't carry over to your Object Detection page (`harithkavish.github.io/Multi-Object-Detection-using-YOLO/`).

## ✅ Solution: localStorage Bridge

Both pages read/write from the same `localStorage` key (`'theme'`), which is shared across all pages under the same domain.

---

## 📋 Implementation Steps

### Step 1: Update Main Portfolio (Already Done!)

Your main portfolio now uses:
- **localStorage key**: `'theme'` (stores `'dark'` or `'light'`)
- **Theme detector**: Loads before CSS to prevent flash
- **CSS class**: `.dark-mode` applied to `<body>`

### Step 2: Add Theme Detection to Other Pages

For **any other page** (like Object Detection), add this script in the `<head>` **BEFORE** your CSS:

```html
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Your Page Title</title>
    
    <!-- Theme detector - MUST load before CSS -->
    <script>
        (function() {
            const savedTheme = localStorage.getItem('theme');
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            
            if (savedTheme === 'dark' || (prefersDark && !savedTheme)) {
                document.documentElement.classList.add('dark-mode');
            }
        })();
    </script>
    
    <!-- Now load your CSS -->
    <link rel="stylesheet" href="style.css">
</head>
```

### Step 3: Add Dark Mode Styles

Use CSS variables for easy theme switching:

```css
/* Light mode (default) */
:root {
    --bg-color: white;
    --text-color: black;
    --card-bg: #f5f5f5;
}

/* Dark mode */
.dark-mode {
    --bg-color: #121212;
    --text-color: #e0e0e0;
    --card-bg: #1e1e1e;
}

body {
    background-color: var(--bg-color);
    color: var(--text-color);
    transition: background-color 0.3s ease, color 0.3s ease;
}
```

### Step 4: Add Theme Toggle (Optional)

If you want a toggle button on the subpage:

```html
<button id="themeToggle">🌙</button>

<script>
document.addEventListener('DOMContentLoaded', () => {
    const toggle = document.getElementById('themeToggle');
    
    // Update button icon
    function updateButton() {
        const isDark = document.documentElement.classList.contains('dark-mode');
        toggle.textContent = isDark ? '☀️' : '🌙';
    }
    
    updateButton();
    
    // Toggle theme
    toggle.addEventListener('click', () => {
        const isDark = document.documentElement.classList.contains('dark-mode');
        
        if (isDark) {
            document.documentElement.classList.remove('dark-mode');
            localStorage.setItem('theme', 'light');
        } else {
            document.documentElement.classList.add('dark-mode');
            localStorage.setItem('theme', 'dark');
        }
        
        updateButton();
    });
});
</script>
```

---

## 🔧 Technical Details

### Why This Works

1. **Shared localStorage**: All pages under `harithkavish.github.io` share the same localStorage
2. **Immediate execution**: Script runs before CSS loads, preventing flash
3. **System preference fallback**: If no saved theme, respects `prefers-color-scheme`
4. **CSS variables**: Makes theme switching smooth and maintainable

### localStorage Key

- **Key name**: `'theme'`
- **Values**: `'dark'` or `'light'`
- **Scope**: All pages under `harithkavish.github.io/*`

### CSS Class

- **Class name**: `.dark-mode`
- **Applied to**: `document.documentElement` (the `<html>` tag)
- **Why**: Allows styling from root, works even before `<body>` loads

---

## 📁 Files in This Project

| File | Purpose |
|------|---------|
| `theme-detector.js` | Reusable theme detection script for any page |
| `theme-persistence-example.html` | Example implementation showing theme sync |
| `THEME_PERSISTENCE_GUIDE.md` | This guide |

---

## 🧪 Testing

1. Open your main portfolio: `harithkavish.github.io/`
2. Toggle dark mode (🌙 button)
3. Navigate to Object Detection page: `harithkavish.github.io/Multi-Object-Detection-using-YOLO/`
4. **Expected result**: Dark mode is still active!
5. Toggle theme on Object Detection page
6. Go back to main portfolio
7. **Expected result**: Theme change persists!

---

## 🎨 Customization

### Different CSS Class Names

If your subpage uses a different class name (e.g., `.dark-theme` instead of `.dark-mode`):

```javascript
// In theme detector script, change this:
document.documentElement.classList.add('dark-mode');
// To:
document.documentElement.classList.add('dark-theme');
```

### Different Storage Key

To use a different localStorage key:

```javascript
// Change 'theme' to your preferred key:
const savedTheme = localStorage.getItem('my-custom-theme-key');
localStorage.setItem('my-custom-theme-key', 'dark');
```

### Per-Page Theme Override

To allow a page to have its own theme that doesn't sync:

```javascript
// Use a page-specific key:
const pageTheme = localStorage.getItem('page-object-detection-theme');
const globalTheme = localStorage.getItem('theme');
const theme = pageTheme || globalTheme; // Page preference overrides global
```

---

## 🚀 Quick Start for New Pages

**Copy this template for any new page:**

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <script>
        (function() {
            const t = localStorage.getItem('theme');
            const d = window.matchMedia('(prefers-color-scheme: dark)').matches;
            if (t === 'dark' || (d && !t)) document.documentElement.classList.add('dark-mode');
        })();
    </script>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <!-- Your content -->
</body>
</html>
```

**Add to your CSS:**

```css
:root { --bg: white; --text: black; }
.dark-mode { --bg: #121212; --text: #e0e0e0; }
body { background: var(--bg); color: var(--text); }
```

Done! 🎉

---

## 💡 Best Practices

1. ✅ **Load theme detector BEFORE CSS** - Prevents flash of unstyled content
2. ✅ **Use inline `<script>`** - Don't rely on external file that might load late
3. ✅ **Apply to `documentElement`** - More reliable than waiting for `<body>`
4. ✅ **Use CSS variables** - Makes theme values consistent and easy to change
5. ✅ **Respect system preference** - Fallback to `prefers-color-scheme` if no saved theme
6. ✅ **Keep key name consistent** - All pages must use the same localStorage key

---

## 🐛 Troubleshooting

### Theme doesn't persist between pages

- **Check**: Are both pages using the same localStorage key (`'theme'`)?
- **Check**: Is the theme detector script loading before CSS?
- **Check**: Are you testing on the same domain (not `file://` protocol)?

### Flash of light content on dark mode

- **Fix**: Move the `<script>` tag higher in `<head>`, before CSS
- **Fix**: Use inline script, not external file
- **Fix**: Ensure script is synchronous (no `async` or `defer`)

### System dark mode not working

- **Check**: Is your OS/browser set to dark mode?
- **Check**: Script should check `window.matchMedia('(prefers-color-scheme: dark)')`
- **Check**: Fallback logic: `savedTheme === 'dark' || (prefersDark && !savedTheme)`

### localStorage not working

- **Check**: Browser privacy settings might block localStorage
- **Check**: Incognito/private mode might clear localStorage between sessions
- **Test**: `localStorage.setItem('test', 'value')` in console

---

## 📚 References

- [MDN: localStorage](https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage)
- [MDN: prefers-color-scheme](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-color-scheme)
- [CSS Variables (Custom Properties)](https://developer.mozilla.org/en-US/docs/Web/CSS/Using_CSS_custom_properties)

---

**Made with 🌙 by Harith Kavish**

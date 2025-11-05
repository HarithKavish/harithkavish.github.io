/**
 * Universal Theme Detector
 * Immediately checks for theme preference and applies dark mode class
 * to prevent flash of unstyled content.
 * Works across all GitHub Pages subpaths by using shared localStorage.
 */
(function () {
    // Immediately check for theme preference
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

    // Apply dark mode class if needed
    if (savedTheme === 'dark' || (prefersDark && !savedTheme)) {
        document.documentElement.classList.add('dark-mode');
        // Also add to body for compatibility with existing styles
        if (document.body) {
            document.body.classList.add('dark-mode');
        } else {
            // If body doesn't exist yet, add it when DOM is ready
            document.addEventListener('DOMContentLoaded', () => {
                document.body.classList.add('dark-mode');
            });
        }
    }
})();

// Toggle the visibility of a section by its id (used for both My Websites and Connect with me)
function toggleSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.classList.toggle('section-hidden');
    }
}

function toggleConnect(event) {
    event.preventDefault();
    const btn = event.currentTarget;
    const section = document.getElementById('connectSection');
    if (section && btn) {
        const isHidden = section.classList.toggle('connect-hidden');
        if (!section.classList.contains('connect-hidden')) {
            sortConnectButtons();
            btn.classList.add('expanded');
            btn.setAttribute('aria-expanded', 'true');
        } else {
            btn.classList.remove('expanded');
            btn.setAttribute('aria-expanded', 'false');
        }
    }
}

function toggleWebsites(event) {
    event.preventDefault();
    const btn = document.getElementById('websitesToggleBtn');
    const websitesSection = document.getElementById('websitesSection');
    const websitesSection2 = document.getElementById('websitesSection2');
    const websitesHeading = document.getElementById('websitesHeading');
    const websitesHeading2 = document.getElementById('websitesHeading2');
    let isHidden = true;
    if (websitesSection && btn && websitesSection2 && websitesHeading && websitesHeading2) {
        isHidden = websitesSection.classList.toggle('websites-hidden');
        websitesSection2.classList.toggle('websites-hidden');
        websitesHeading.classList.toggle('websites-hidden');
        websitesHeading2.classList.toggle('websites-hidden');
        showStatusInfo(!isHidden);
        if (!isHidden) {
            btn.classList.add('expanded');
            btn.setAttribute('aria-expanded', 'true');
        } else {
            btn.classList.remove('expanded');
            btn.setAttribute('aria-expanded', 'false');
        }
    }
}

function sortConnectButtons() {
    // Alphabetically sort the buttons in the Connect section on page load and when toggled
    const connectSection = document.getElementById('connectSection');
    if (!connectSection) return;
    const links = Array.from(connectSection.querySelectorAll('a.footer-btn'));
    links.sort((a, b) => a.textContent.localeCompare(b.textContent));
    links.forEach(link => connectSection.appendChild(link));
}

// Sort on page load
window.addEventListener('DOMContentLoaded', sortConnectButtons);

function updateSkinNetStatus() {
    // Check SkinNet Analyzer backend status and update dot
    const dot = document.getElementById('skinnet-status-dot');
    if (!dot) return;
    fetch('https://skinnet-analyzer-backend-latest.onrender.com/api/status', { method: 'GET', mode: 'cors' })
        .then(response => response.json())
        .then(data => {
            if (data && typeof data.status === 'string') {
                const status = data.status.trim().toLowerCase();
                dot.className = 'status-dot online';
                if (status === 'offline') {
                    dot.className = 'status-dot offline';
                }
            } else {
                dot.className = 'status-dot unknown';
            }
        })
        .catch(err => {
            dot.className = 'status-dot unknown';
            console.log('SkinNet Analyzer status: unknown (fetch error)', err);
        });
}

window.addEventListener('DOMContentLoaded', updateSkinNetStatus);

function showStatusInfo(show) {
    // Show/hide the status info legend above the websites section
    const info = document.getElementById('skinnet-status-info');
    if (!info) return;
    info.style.display = show ? 'block' : 'none';
}

// Initial call to show/hide status info based on current visibility of websites section
window.addEventListener('DOMContentLoaded', () => {
    const websitesSection = document.getElementById('websitesSection');
    const isHidden = websitesSection.classList.contains('websites-hidden');
    showStatusInfo(!isHidden);
});

function updateDetectObjectStatus() {
    // Object Detection is always available (client-side only, no backend needed)
    const dot = document.getElementById('detectobject-status-dot');
    if (!dot) return;
    // Set to always online since it runs entirely in the browser
    dot.className = 'status-dot online';
}

window.addEventListener('DOMContentLoaded', updateDetectObjectStatus);

// Dark Mode Toggle
window.addEventListener('DOMContentLoaded', () => {
    const darkModeToggle = document.getElementById('darkModeToggle');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

    // Check localStorage or system preference (using 'theme' key for cross-page compatibility)
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark' || (prefersDark && !savedTheme)) {
        document.body.classList.add('dark-mode');
        if (darkModeToggle) darkModeToggle.textContent = '☀️';
    }

    // Toggle dark mode on button click
    darkModeToggle?.addEventListener('click', () => {
        document.body.classList.toggle('dark-mode');
        const isDark = document.body.classList.contains('dark-mode');
        // Store theme preference using 'theme' key for cross-page compatibility
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
        darkModeToggle.textContent = isDark ? '☀️' : '🌙';

        // Notify chat iframe about theme change
        const chatFrame = document.getElementById('chatFrame');
        if (chatFrame && chatFrame.contentWindow) {
            chatFrame.contentWindow.postMessage({
                type: 'theme-change',
                theme: isDark ? 'dark' : 'light'
            }, '*');
        }
    });
});

/**
 * Auto-load Neo AI Chatbot Widget
 * Automatically injects the chatbot widget on all pages across harithkavish.github.io
 * No manual embedding required - widget appears on every page automatically
 */
(function () {
    // Only load widget once
    if (window.NeoAIWidgetLoaded) return;
    window.NeoAIWidgetLoaded = true;

    // Load widget script dynamically (NEW MULTI-AGENT ORCHESTRATOR)
    const widgetScript = document.createElement('script');
    widgetScript.src = 'https://harithkavish-harithkavish-nlweb-orchestrator.hf.space/widget.js';
    widgetScript.async = true;
    widgetScript.defer = true;

    // Add error handling
    widgetScript.onerror = function () {
        console.warn('Neo AI widget failed to load - continuing without chatbot');
    };

    // Inject script into page
    document.head.appendChild(widgetScript);

    console.log('✅ Neo AI widget auto-loader initialized');
})();

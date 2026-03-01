const HarithShell = (() => {
    const THEME_KEY = 'theme';
    const defaultNavLinks = [];
    const defaultFooterLinks = [];
    let currentTheme = 'light';

    function detectPreferredTheme() {
        const saved = localStorage.getItem(THEME_KEY);
        if (saved) return saved;
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }

    function updateBodyClass(isDark) {
        if (document.body) {
            document.body.classList.toggle('dark-mode', isDark);
        } else {
            document.addEventListener('DOMContentLoaded', () => {
                document.body.classList.toggle('dark-mode', isDark);
            }, { once: true });
        }
    }

    function updateToggleText(theme) {
        const toggle = document.getElementById('darkModeToggle');
        if (toggle) {
            toggle.textContent = theme === 'dark' ? '☀️' : '🌙';
        }
    }

    function notifyThemeChange(theme) {
        const chatFrame = document.getElementById('chatFrame');
        if (chatFrame && chatFrame.contentWindow) {
            chatFrame.contentWindow.postMessage({
                type: 'theme-change',
                theme
            }, '*');
        }
    }

    function applyTheme(theme, persist = true) {
        currentTheme = theme === 'dark' ? 'dark' : 'light';
        document.documentElement.classList.toggle('dark-mode', currentTheme === 'dark');
        updateBodyClass(currentTheme === 'dark');
        if (persist) {
            localStorage.setItem(THEME_KEY, currentTheme);
        }
        updateToggleText(currentTheme);
        notifyThemeChange(currentTheme);
    }

    function toggleTheme() {
        applyTheme(currentTheme === 'dark' ? 'light' : 'dark');
    }

    function resolveTarget(target) {
        if (!target) return null;
        if (typeof target === 'string') {
            return document.querySelector(target);
        }
        if (target instanceof HTMLElement) {
            return target;
        }
        return null;
    }

    function renderNavLinks(links) {
        return links.map(link => {
            if (link.action) {
                return `<button type="button" class="shared-nav-link" data-action="${link.action}">${link.label}</button>`;
            }
            return `<a class="shared-nav-link" href="${link.href}">${link.label}</a>`;
        }).join('');
    }

    function renderHeader({ target = '#sharedHeader', navLinks = defaultNavLinks, brand = {} } = {}) {
        const container = resolveTarget(target);
        if (!container) return null;
        const brandTitle = brand.title || 'Harith Kavish';
        const brandTagline = brand.tagline || 'AI-Driven Systems Architect & Creative Director';
        container.innerHTML = '';
        const header = document.createElement('header');
        header.className = 'shared-header';
        const navMarkup = renderNavLinks(navLinks);
        header.innerHTML = `
            <div class="shared-header__inner">
                <div class="shared-brand shared-brand--single-line">
                    <span class="shared-brand__name">${brandTitle}</span>
                </div>
                ${navMarkup ? `<nav class="shared-nav" aria-label="Primary">${navMarkup}</nav>` : ''}
                        <div class="shared-header__actions">
                            <button id="darkModeToggle" class="theme-toggle" aria-label="Toggle dark mode"></button>
                            <div class="google-button-wrapper" id="googleSignInButton" aria-label="Sign in with Google"></div>
                        </div>
            </div>
        `;
        container.appendChild(header);
        header.querySelectorAll('[data-action]').forEach(button => {
            button.addEventListener('click', event => {
                const action = button.getAttribute('data-action');
                if (action === 'toggle-websites') {
                    toggleWebsites(event);
                }
                if (action === 'toggle-connect') {
                    toggleConnect(event);
                }
            });
        });
        const toggleBtn = document.getElementById('darkModeToggle');
        toggleBtn?.addEventListener('click', () => toggleTheme());
        updateToggleText(currentTheme);
        return header;
    }

    function renderFooter({ target = '#sharedFooter', links = defaultFooterLinks, text = 'Harith Kavish' } = {}) {
        const container = resolveTarget(target);
        if (!container) return null;
        const year = new Date().getFullYear();
        container.innerHTML = '';
        const footer = document.createElement('footer');
        footer.className = 'shared-footer';
        footer.innerHTML = `
            <div class="shared-footer__inner">
                <span class="shared-footer__copy">© ${year} ${text}</span>
                ${links.length
                ? `<div class="shared-footer__links">
                            ${links.map(link => `<a href="${link.href}" target="_blank" rel="noreferrer noopener">${link.label}</a>`).join('')}
                        </div>`
                : ''}
            </div>
        `;
        container.appendChild(footer);
        return footer;
    }

    function initTheme() {
        applyTheme(detectPreferredTheme(), false);
    }

    return {
        renderHeader,
        renderFooter,
        initTheme,
        toggleTheme,
        getTheme: () => currentTheme
    };
})();

window.HarithShell = HarithShell;
HarithShell.initTheme();

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
    const websitesSectionFrontend = document.getElementById('websitesSectionFrontend');
    const websitesHeading = document.getElementById('websitesHeading');
    const websitesHeading2 = document.getElementById('websitesHeading2');
    const websitesHeadingFrontend = document.getElementById('websitesHeadingFrontend');
    let isHidden = true;
    if (websitesSection && btn && websitesSection2 && websitesHeading && websitesHeading2) {
        isHidden = websitesSection.classList.toggle('websites-hidden');
        websitesSection2.classList.toggle('websites-hidden');
        websitesHeading.classList.toggle('websites-hidden');
        websitesHeading2.classList.toggle('websites-hidden');
        if (websitesSectionFrontend && websitesHeadingFrontend) {
            websitesSectionFrontend.classList.toggle('websites-hidden');
            websitesHeadingFrontend.classList.toggle('websites-hidden');
        }
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
    const connectSection = document.getElementById('connectSection');
    if (!connectSection) return;
    const links = Array.from(connectSection.querySelectorAll('a.footer-btn'));
    links.sort((a, b) => a.textContent.localeCompare(b.textContent));
    links.forEach(link => connectSection.appendChild(link));
}

window.addEventListener('DOMContentLoaded', sortConnectButtons);

function updateSkinNetStatus() {
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
    const info = document.getElementById('skinnet-status-info');
    if (!info) return;
    info.style.display = show ? 'block' : 'none';
}

window.addEventListener('DOMContentLoaded', () => {
    const websitesSection = document.getElementById('websitesSection');
    const websitesSectionFrontend = document.getElementById('websitesSectionFrontend');
    const websitesSection2 = document.getElementById('websitesSection2');
    const anyVisible = [websitesSection, websitesSectionFrontend, websitesSection2]
        .filter(Boolean)
        .some(sec => !sec.classList.contains('websites-hidden'));
    showStatusInfo(anyVisible);
});

function updateDetectObjectStatus() {
    const dot = document.getElementById('detectobject-status-dot');
    if (!dot) return;
    dot.className = 'status-dot online';
}

window.addEventListener('DOMContentLoaded', updateDetectObjectStatus);/**
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
    const websitesSectionFrontend = document.getElementById('websitesSectionFrontend');
    const websitesHeading = document.getElementById('websitesHeading');
    const websitesHeading2 = document.getElementById('websitesHeading2');
    const websitesHeadingFrontend = document.getElementById('websitesHeadingFrontend');
    let isHidden = true;
    if (websitesSection && btn && websitesSection2 && websitesHeading && websitesHeading2) {
        isHidden = websitesSection.classList.toggle('websites-hidden');
        websitesSection2.classList.toggle('websites-hidden');
        websitesHeading.classList.toggle('websites-hidden');
        websitesHeading2.classList.toggle('websites-hidden');
        if (websitesSectionFrontend && websitesHeadingFrontend) {
            websitesSectionFrontend.classList.toggle('websites-hidden');
            websitesHeadingFrontend.classList.toggle('websites-hidden');
        }
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
    const websitesSectionFrontend = document.getElementById('websitesSectionFrontend');
    const websitesSection2 = document.getElementById('websitesSection2');
    const anyVisible = [websitesSection, websitesSectionFrontend, websitesSection2]
        .filter(Boolean)
        .some(sec => !sec.classList.contains('websites-hidden'));
    showStatusInfo(anyVisible);
});

function updateDetectObjectStatus() {
    // Object Detection is always available (client-side only, no backend needed)
    const dot = document.getElementById('detectobject-status-dot');
    if (!dot) return;
    // Set to always online since it runs entirely in the browser
    dot.className = 'status-dot online';
}

window.addEventListener('DOMContentLoaded', updateDetectObjectStatus);

// Auto-load Neo AI chatbot widget on every page using the shared shell script
(function () {
    if (window.NeoAIWidgetLoaded) return;
    window.NeoAIWidgetLoaded = true;
    const widgetScript = document.createElement('script');
    widgetScript.src = 'https://harithkavish-nlweb-portfolio-chat.hf.space/widget.js?v=' + Date.now();
    widgetScript.async = true;
    widgetScript.defer = true;
    widgetScript.onerror = function () {
        console.warn('Neo AI widget failed to load - continuing without chatbot');
    };
    document.head.appendChild(widgetScript);
    console.log('✅ Neo AI widget auto-loader initialized');
})();

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
    // Add cache buster to ensure latest version
    const widgetScript = document.createElement('script');
    widgetScript.src = 'https://harithkavish-nlweb-portfolio-chat.hf.space/widget.js?v=' + Date.now();
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

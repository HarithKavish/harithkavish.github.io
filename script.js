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
            document.body.classList.add('sky-blue-theme', isDark ? 'dark-mode' : '');
        } else {
            document.addEventListener('DOMContentLoaded', () => {
                document.body.classList.toggle('dark-mode', isDark);
                document.body.classList.add('sky-blue-theme', isDark ? 'dark-mode' : '');
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
        header.className = 'shared-header sky-blue-theme';
        const navMarkup = renderNavLinks(navLinks);
        header.innerHTML = `
            <div class="shared-header__inner">
                <div class="shared-brand shared-brand--single-line">
                    <span class="shared-brand__name">${brandTitle}</span>
                </div>
                ${navMarkup ? `<nav class="shared-nav" aria-label="Primary">${navMarkup}</nav>` : ''}
                <div class="shared-header__actions">
                    <button id="darkModeToggle" class="theme-toggle sky-blue-theme" aria-label="Toggle dark mode"></button>
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
        footer.className = 'shared-footer sky-blue-theme';
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

// CSS Theme Overrides
document.addEventListener('DOMContentLoaded', () => {
    const body = document.body;
    const root = document.documentElement;

    // Sky Blue Theme Overrides
    if (currentTheme === 'light') {
        root.classList.add('sky-blue-theme');
        body.classList.add('sky-blue-light');

        // Override default styles with sky blue
        root.style.setProperty('--primary-color', '#4A90E2');
        root.style.setProperty('--secondary-color', '#E6F2FF');
        root.style.setProperty('--accent-color', '#1E90FF');
        root.style.setProperty('--text-primary', '#2C3E50');
        root.style.setProperty('--text-secondary', '#7F8C8D');
        root.style.setProperty('--background', '#FFFFFF');
        root.style.setProperty('--card-bg', '#F8F9FA');
        root.style.setProperty('--border-color', '#E9ecef');
    } else {
        root.classList.add('dark-mode sky-blue-theme');
        body.classList.add('dark-mode');

        // Dark mode overrides with sky blue
        root.style.setProperty('--primary-color', '#4A90E2');
        root.style.setProperty('--secondary-color', '#2C3E50');
        root.style.setProperty('--accent-color', '#1E90FF');
        root.style.setProperty('--text-primary', '#FFFFFF');
        root.style.setProperty('--text-secondary', '#E0E0E0');
        root.style.setProperty('--background', '#121212');
        root.style.setProperty('--card-bg', '#1E1E1E');
        root.style.setProperty('--border-color', '#333333');
    }
});

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
    event
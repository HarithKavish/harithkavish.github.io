/**
 * Page-specific logic for harithkavish.github.io index
 * Handles toggle buttons, Google Sign-In, status checks, and Neo AI widget
 * Design system (theme, shell components) loaded via CDN
 */

// Google Sign-In Configuration
const GOOGLE_USER_STORAGE_KEY = 'harith_google_user';
let googleButtonRetries = 0;

function handleGoogleCredentialResponse(credentialResponse) {
    console.log('Google OAuth credential response', credentialResponse);
    const profile = extractProfileFromCredential(credentialResponse?.credential);
    const user = {
        name: profile?.name || 'Signed in',
        picture: profile?.picture || '',
        email: profile?.email || ''
    };
    storeGoogleUser(user);
    renderSignedInButton(user);
}

function extractProfileFromCredential(credential) {
    if (!credential) return null;
    try {
        const payload = credential.split('.')[1];
        const base64 = payload.replace(/-/g, '+').replace(/_/g, '/');
        const decoded = decodeURIComponent(atob(base64)
            .split('')
            .map(char => `%${('00' + char.charCodeAt(0).toString(16)).slice(-2)}`)
            .join(''));
        return JSON.parse(decoded);
    } catch (err) {
        console.warn('Failed to decode Google credential', err);
        return null;
    }
}

function storeGoogleUser(user) {
    if (!user) return;
    localStorage.setItem(GOOGLE_USER_STORAGE_KEY, JSON.stringify(user));
}

function getStoredGoogleUser() {
    try {
        const raw = localStorage.getItem(GOOGLE_USER_STORAGE_KEY);
        return raw ? JSON.parse(raw) : null;
    } catch (err) {
        console.warn('Failed to parse stored Google user', err);
        return null;
    }
}

function clearStoredGoogleUser() {
    localStorage.removeItem(GOOGLE_USER_STORAGE_KEY);
}

function renderSignedInButton(user) {
    const googleButtonTarget = document.getElementById('googleSignInButton');
    if (!googleButtonTarget) return;
    googleButtonTarget.innerHTML = `
        <button type="button" class="signed-in-button" aria-label="Signed in as ${user.name}">
            <img src="${user.picture || 'https://www.gravatar.com/avatar/?d=mp'}" alt="${user.name} avatar"
                class="signed-in-button__avatar" loading="lazy" />
            <span class="signed-in-button__name">${user.name}</span>
        </button>`;
    const signInBtn = googleButtonTarget.querySelector('button');
    signInBtn?.addEventListener('click', () => {
        clearStoredGoogleUser();
        initGoogleSignInButton();
    });
}

function initGoogleSignInButton() {
    const googleButtonTarget = document.getElementById('googleSignInButton');
    if (!googleButtonTarget) {
        return;
    }
    const storedProfile = getStoredGoogleUser();
    if (storedProfile) {
        renderSignedInButton(storedProfile);
        return;
    }
    if (!window.google?.accounts?.id) {
        if (googleButtonRetries < 6) {
            googleButtonRetries += 1;
            window.setTimeout(initGoogleSignInButton, 250);
        }
        return;
    }
    googleButtonTarget.innerHTML = '';
    google.accounts.id.initialize({
        client_id: '59648450302-sqkk4pdujkt4hrm0uuhq95pq55b4jg2k.apps.googleusercontent.com',
        callback: handleGoogleCredentialResponse
    });
    google.accounts.id.renderButton(
        googleButtonTarget,
        {
            theme: 'outline',
            size: 'medium',
            type: 'standard',
            shape: 'pill'
        }
    );
    googleButtonTarget.dataset.initialized = 'true';
}

// Section Toggle Functions
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

// Status Updates
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

function updateDetectObjectStatus() {
    const dot = document.getElementById('detectobject-status-dot');
    if (!dot) return;
    dot.className = 'status-dot online';
}

function showStatusInfo(show) {
    const info = document.getElementById('skinnet-status-info');
    if (!info) return;
    info.style.display = show ? 'block' : 'none';
}

// Auto-load Neo AI Chatbot Widget
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

// Dark Mode Toggle Handler
function setupDarkModeToggle() {
    const darkModeToggle = document.getElementById('darkModeToggle');
    if (!darkModeToggle) return;

    // Initialize icon based on current state
    const isDark = document.body.classList.contains('dark-mode') || localStorage.getItem('theme') === 'dark';
    if (isDark) {
        document.body.classList.add('dark-mode');
        document.documentElement.classList.add('dark-mode');
    }
    darkModeToggle.textContent = isDark ? '☀️' : '🌙';

    darkModeToggle.addEventListener('click', () => {
        const isDarkNow = document.body.classList.toggle('dark-mode');
        document.documentElement.classList.toggle('dark-mode', isDarkNow);
        localStorage.setItem('theme', isDarkNow ? 'dark' : 'light');
        darkModeToggle.textContent = isDarkNow ? '☀️' : '🌙';
    });
}

// DOMContentLoaded Initialization
document.addEventListener('DOMContentLoaded', () => {
    if (window.HarithShell) {
        HarithShell.renderHeader({
            target: '#sharedHeader',
            brand: {
                title: 'Harith Kavish',
                tagline: 'AI-Driven Systems Architect & Creative Director'
            }
        });
        HarithShell.renderFooter({
            target: '#sharedFooter',
            text: 'Harith Kavish',
            links: [
                { href: '/privacy-policy.html', label: 'Privacy Policy' },
                { href: '/terms-of-service.html', label: 'Terms of Service' }
            ]
        });
    }
    initGoogleSignInButton();
    setupDarkModeToggle();
    sortConnectButtons();
    updateSkinNetStatus();
    updateDetectObjectStatus();
    const websitesSection = document.getElementById('websitesSection');
    const websitesSectionFrontend = document.getElementById('websitesSectionFrontend');
    const websitesSection2 = document.getElementById('websitesSection2');
    const anyVisible = [websitesSection, websitesSectionFrontend, websitesSection2]
        .filter(Boolean)
        .some(sec => !sec.classList.contains('websites-hidden'));
    showStatusInfo(anyVisible);
});

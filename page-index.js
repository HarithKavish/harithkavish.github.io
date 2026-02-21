/**
 * Page-specific logic for harithkavish.github.io index
 * Handles toggle buttons, status checks, and Neo AI widget
 */

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

// DOMContentLoaded Initialization
document.addEventListener('DOMContentLoaded', () => {
    // Note: Header/Footer are now Web Components (<harith-header> and <harith-footer>)    
    // Auth and Theme logic are handled internally by the components.

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

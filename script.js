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
    // Check Detect Object backend status and update dot
    const dot = document.getElementById('detectobject-status-dot');
    if (!dot) return;
    fetch('https://harithkavish-multi-object-detection-using-yolo.hf.space/health', { method: 'GET', mode: 'cors' })
        .then(response => response.json())
        .then(data => {
            if (data && typeof data.status === 'string') {
                const status = data.status.trim().toLowerCase();
                if (status === 'ok') {
                    dot.className = 'status-dot online';
                } else if (status === 'offline') {
                    dot.className = 'status-dot offline';
                } else {
                    dot.className = 'status-dot unknown';
                }
            } else {
                dot.className = 'status-dot unknown';
            }
        })
        .catch(err => {
            dot.className = 'status-dot unknown';
            console.log('Detect Object status: unknown (fetch error)', err);
        });
}

window.addEventListener('DOMContentLoaded', updateDetectObjectStatus);

// Dark Mode Toggle
window.addEventListener('DOMContentLoaded', () => {
    const darkModeToggle = document.getElementById('darkModeToggle');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

    // Check localStorage or system preference
    if (localStorage.getItem('darkMode') === 'true' || (prefersDark && !localStorage.getItem('darkMode'))) {
        document.body.classList.add('dark-mode');
        if (darkModeToggle) darkModeToggle.textContent = '☀️';
    }

    // Toggle dark mode on button click
    darkModeToggle?.addEventListener('click', () => {
        document.body.classList.toggle('dark-mode');
        const isDark = document.body.classList.contains('dark-mode');
        localStorage.setItem('darkMode', isDark);
        darkModeToggle.textContent = isDark ? '☀️' : '🌙';
    });
});

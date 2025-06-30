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
        section.classList.toggle('connect-hidden');
        if (!section.classList.contains('connect-hidden')) {
            sortConnectButtons();
            btn.classList.add('expanded');
        } else {
            btn.classList.remove('expanded');
        }
    }
}

function toggleWebsites(event) {
    event.preventDefault();
    const btn = document.getElementById('websitesToggleBtn');
    const websitesSection = document.getElementById('websitesSection');
    if (websitesSection && btn) {
        const isHidden = websitesSection.classList.toggle('websites-hidden');
        showStatusInfo(!isHidden);
        if (!isHidden) {
            btn.classList.add('expanded');
        } else {
            btn.classList.remove('expanded');
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

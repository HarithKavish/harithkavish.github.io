// Toggle the visibility of a section by its id (used for both My Websites and Connect with me)
function toggleSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.classList.toggle('section-hidden');
    }
}

function toggleConnect(event) {
    event.preventDefault();
    const connectSection = document.getElementById('connectSection');
    if (connectSection) {
        connectSection.classList.toggle('connect-hidden');
    }
}

function toggleWebsites(event) {
    event.preventDefault();
    const websitesSection = document.getElementById('websitesSection');
    if (websitesSection) {
        websitesSection.classList.toggle('websites-hidden');
    }
}

// Alphabetically sort the buttons in the Connect section on page load and when toggled
function sortConnectButtons() {
    const connectSection = document.getElementById('connectSection');
    if (!connectSection) return;
    const links = Array.from(connectSection.querySelectorAll('a.footer-btn'));
    links.sort((a, b) => a.textContent.localeCompare(b.textContent));
    links.forEach(link => connectSection.appendChild(link));
}

// Sort on page load
window.addEventListener('DOMContentLoaded', sortConnectButtons);
// Also sort every time the section is toggled (in case new buttons are added dynamically)
function toggleConnect(event) {
    const section = document.getElementById('connectSection');
    if (section) {
        section.classList.toggle('connect-hidden');
        if (!section.classList.contains('connect-hidden')) {
            sortConnectButtons();
        }
    }
}

// Check SkinNet Analyzer backend status and update dot
function updateSkinNetStatus() {
    const dot = document.getElementById('skinnet-status-dot');
    if (!dot) return;
    dot.className = 'status-dot unknown';
    fetch('https://skinnet-analyzer-backend-latest.onrender.com/api/status', { method: 'GET', mode: 'cors' })
        .then(r => {
            if (!r.ok) throw new Error('Network response was not ok');
            return r.json();
        })
        .then(data => {
            if (data && typeof data.status === 'string') {
                const status = data.status.trim().toLowerCase();
                console.log('SkinNet Analyzer status:', status); // Log status for debugging
                if (status === 'online') {
                    dot.className = 'status-dot online';
                } else if (status === 'offline') {
                    dot.className = 'status-dot offline';
                } else {
                    dot.className = 'status-dot unknown';
                }
            } else {
                console.log('SkinNet Analyzer status: unknown (invalid response)', data);
                dot.className = 'status-dot unknown';
            }
        })
        .catch((err) => {
            console.log('SkinNet Analyzer status: unknown (fetch error)', err);
            dot.className = 'status-dot unknown';
        });
}
window.addEventListener('DOMContentLoaded', updateSkinNetStatus);

/**
 * Universal Theme Detector
 * This script should be included in the <head> of all pages to ensure
 * dark mode is applied immediately, preventing flash of unstyled content.
 * 
 * Usage: Include this script early in <head> before any CSS:
 * <script src="theme-detector.js"></script>
 * 
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

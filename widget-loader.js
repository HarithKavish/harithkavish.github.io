/**
 * Neo AI Widget Auto-Loader
 * Universal script to load Neo AI chatbot on any harithkavish.github.io page
 * 
 * Usage: Add this to any page:
 * <script src="https://harithkavish.github.io/widget-loader.js"></script>
 */
(function () {
    // Prevent duplicate loading
    if (window.NeoAIWidgetLoaded) {
        console.log('Neo AI widget already loaded, skipping...');
        return;
    }
    window.NeoAIWidgetLoaded = true;

    // Load the widget from HuggingFace Space (Multi-Agent Orchestrator)
    // Add cache buster to ensure latest version
    const widgetScript = document.createElement('script');
    widgetScript.src = 'https://harithkavish-nlweb-portfolio-chat.hf.space/widget.js?v=' + Date.now();
    widgetScript.async = true;
    widgetScript.defer = true;

    // Error handling
    widgetScript.onerror = function () {
        console.warn('Neo AI widget failed to load from HuggingFace Space');
        window.NeoAIWidgetLoaded = false; // Allow retry
    };

    widgetScript.onload = function () {
        console.log('✅ Neo AI - Harith Kavish\'s Assistant loaded successfully!');
    };

    // Inject into page
    document.head.appendChild(widgetScript);

    console.log('🔄 Loading Neo AI widget...');
})();

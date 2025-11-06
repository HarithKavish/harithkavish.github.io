/**
 * Universal Neo AI Chatbot Widget Loader
 * 
 * Add this ONE line to any HTML page across all your GitHub projects:
 * <script src="https://harithkavish.github.io/universal-widget.js"></script>
 * 
 * This will automatically inject the chatbot on ANY page!
 */

(function () {
    'use strict';

    // Prevent multiple loads
    if (window.NeoAIWidgetLoaded) {
        console.log('Neo AI widget already loaded');
        return;
    }
    window.NeoAIWidgetLoaded = true;

    console.log('🚀 Loading Neo AI Chatbot Widget...');

    // Load the widget from orchestrator
    const widgetScript = document.createElement('script');
    widgetScript.src = 'https://harithkavish-harithkavish-nlweb-orchestrator.hf.space/widget.js';
    widgetScript.async = true;
    widgetScript.defer = true;

    // Success handler
    widgetScript.onload = function () {
        console.log('✅ Neo AI Chatbot Widget loaded successfully!');
    };

    // Error handler
    widgetScript.onerror = function () {
        console.warn('⚠️ Neo AI widget failed to load - continuing without chatbot');
    };

    // Inject into page
    document.head.appendChild(widgetScript);

})();

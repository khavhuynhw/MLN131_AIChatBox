/**
 * Configuration file for HCM Chatbot Frontend
 * Manages API endpoints for different environments
 */

// Auto-detect environment and set API URLs
const isDevelopment = window.location.hostname === 'localhost' || 
                     window.location.hostname === '127.0.0.1' ||
                     window.location.hostname === '0.0.0.0';

const API_CONFIG = {
    // Development URLs (local)
    development: {
        PYTHON_AI_API: 'http://localhost:8000',
        DOTNET_API: 'http://localhost:9000/api',
        NODEJS_API: 'http://localhost:9000/api' // legacy alias points to Dotnet backend
    },
    
    // Production URLs  
    production: {
        PYTHON_AI_API: 'https://hcm-chat-2.onrender.com',
        DOTNET_API: 'https://hcm-chatbot-nodejs-api.fly.dev/api',
        NODEJS_API: 'https://hcm-chatbot-nodejs-api.fly.dev/api'
    }
};

// Export current config based on environment
const CURRENT_CONFIG = isDevelopment ? API_CONFIG.development : API_CONFIG.production;

// Export individual APIs
window.PYTHON_AI_API = CURRENT_CONFIG.PYTHON_AI_API;
window.DOTNET_API = CURRENT_CONFIG.DOTNET_API;
// Legacy support - keep old variable names for compatibility
window.NODEJS_API = CURRENT_CONFIG.NODEJS_API || window.DOTNET_API;
window.API_BASE_URL = window.DOTNET_API;

console.log('[config] Current hostname:', window.location.hostname);
console.log('[config] Current URL:', window.location.href);
console.log('[config] Environment:', isDevelopment ? 'Development' : 'Production');
console.log('[config] isDevelopment flag:', isDevelopment);
console.log('[config] Python AI API:', window.PYTHON_AI_API);
console.log('[config] Dotnet API:', window.DOTNET_API);
console.log('[config] Node.js API (alias):', window.NODEJS_API);
console.log('[config] API Base URL:', window.API_BASE_URL);
console.log('[config] Full config:', CURRENT_CONFIG);
console.warn('[config] WARNING: Check Network tab - ensure the expected ports are used');

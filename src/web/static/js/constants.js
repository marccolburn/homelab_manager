// API endpoints and configuration constants

const API_BASE_URL = window.location.origin;

const API_ENDPOINTS = {
    // Repository management
    repos: '/api/repos',
    repo: (labId) => `/api/repos/${labId}`,
    
    // Lab deployment
    deployments: '/api/deployments',
    deploy: (labId) => `/api/labs/${labId}/deploy`,
    destroy: (labId) => `/api/labs/${labId}/destroy`,
    
    // Configuration scenarios
    scenarios: (labId) => `/api/labs/${labId}/scenarios`,
    applyScenario: (labId, scenario) => `/api/labs/${labId}/scenarios/${scenario}`,
    
    // Logs and tasks
    logs: (labId) => `/api/logs/${labId}`,
    tasks: (taskId) => `/api/tasks/${taskId}`,
    
    // System
    health: '/api/health',
    netbox: '/api/netbox/validate'
};

// Refresh intervals (in milliseconds)
const REFRESH_INTERVALS = {
    deployments: 5000,  // 5 seconds (updated from 30)
    tasks: 2000,        // 2 seconds for task updates
    logs: 1000          // 1 second for log streaming
};

// UI Constants
const NOTIFICATION_DURATION = 5000;  // 5 seconds
const ANIMATION_DURATION = 300;      // 300ms for transitions
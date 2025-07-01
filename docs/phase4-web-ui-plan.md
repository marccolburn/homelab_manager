# Phase 4: Web UI Implementation Plan

## Overview

This document provides a comprehensive implementation plan for Phase 4 of the Homelab Manager project - Web UI Development. The plan emphasizes simplicity, ease of setup, comprehensive testing, and good documentation while building on the existing foundation.

## Current State Analysis

### Existing Assets
- **Working Prototype**: `src/web/static/index.html` with basic functionality
- **Flask Static Serving**: Backend already configured to serve web files
- **API Endpoints**: Complete REST API available from Phase 1-3
- **Design Foundation**: Modern UI with gradient backgrounds and card-based layout

### Identified Gaps
1. **API Integration Issues**: JavaScript uses incorrect endpoint paths
2. **Code Organization**: All CSS/JS inline in HTML file
3. **Missing Features**:
   - Repository management UI
   - Configuration scenario selection
   - Deployment logs viewer
   - Real-time status updates
   - NetBox integration controls
4. **No Build Process**: Pure static files (which is good for simplicity!)
5. **Limited Error Handling**: Basic error notifications only

## Implementation Strategy

### Core Principles
1. **Keep It Simple**: No build tools, transpilers, or complex frameworks
2. **Progressive Enhancement**: Start with basic functionality, add features incrementally
3. **API-First**: All operations through existing REST API
4. **Responsive Design**: Work well on desktop, tablet, and mobile
5. **Minimal Dependencies**: Use vanilla JavaScript where possible

## Detailed Implementation Plan

### Phase 4.1: Foundation and Refactoring (Week 1, Days 1-2)

#### Task 1: Code Organization
**File Structure:**
```
src/web/
├── static/
│   ├── index.html          # Main application page
│   ├── css/
│   │   ├── main.css       # Core styles
│   │   ├── components.css # Component-specific styles
│   │   └── responsive.css # Mobile/tablet styles
│   ├── js/
│   │   ├── app.js        # Main application logic
│   │   ├── api.js        # API client module
│   │   ├── ui.js         # UI update functions
│   │   ├── utils.js      # Utility functions
│   │   └── constants.js  # Configuration constants
│   └── img/
│       └── favicon.ico    # Application icon
└── templates/
    └── (empty - for future server-side rendering if needed)
```

**Implementation Steps:**
1. Extract all CSS from index.html to separate files
2. Extract all JavaScript to modular files
3. Implement simple module pattern for JS organization
4. Add proper error handling and logging
5. Create constants file for API endpoints

#### Task 2: Fix API Integration
**Updates Required:**
```javascript
// constants.js
const API_BASE_URL = window.location.origin;
const API_ENDPOINTS = {
    repos: '/api/repos',
    deployments: '/api/deployments',
    deploy: (labId) => `/api/labs/${labId}/deploy`,
    destroy: (labId) => `/api/labs/${labId}/destroy`,
    scenarios: (labId) => `/api/labs/${labId}/scenarios`,
    applyScenario: (labId, scenario) => `/api/labs/${labId}/scenarios/${scenario}`,
    logs: (labId) => `/api/logs/${labId}`,
    tasks: (taskId) => `/api/tasks/${taskId}`,
    health: '/api/health',
    netbox: '/api/netbox/validate'
};
```

### Phase 4.2: Core Features Implementation (Week 1, Days 3-5)

#### Task 3: Repository Management UI
**New Section in index.html:**
```html
<section id="repository-management" class="hidden">
    <h2>Repository Management</h2>
    <div class="repo-actions">
        <button onclick="showAddRepoModal()">Add Repository</button>
        <button onclick="refreshRepos()">Refresh</button>
    </div>
    <div id="repo-list" class="repo-grid">
        <!-- Repository cards will be inserted here -->
    </div>
</section>
```

**Features:**
- Add new repository with Git URL
- Update existing repositories
- Remove repositories
- Show sync status
- Display last update time

#### Task 4: Enhanced Deployment UI
**Improvements:**
1. **Version Selection**: Dropdown to select lab version/tag
2. **NetBox Integration**: Checkbox for "--allocate-ips"
3. **Progress Tracking**: Real-time deployment progress
4. **Resource Check**: Show if resources are available

**Deployment Modal:**
```html
<div id="deploy-modal" class="modal">
    <div class="modal-content">
        <h3>Deploy Lab: <span id="deploy-lab-name"></span></h3>
        <form id="deploy-form">
            <label>Version:
                <select id="version-select">
                    <option value="latest">Latest</option>
                    <!-- Git tags populated here -->
                </select>
            </label>
            <label>
                <input type="checkbox" id="allocate-ips">
                Allocate IPs from NetBox
            </label>
            <div id="resource-check">
                <!-- Resource availability shown here -->
            </div>
            <button type="submit">Deploy</button>
            <button type="button" onclick="closeModal()">Cancel</button>
        </form>
    </div>
</div>
```

#### Task 5: Configuration Scenarios
**Scenario Management Panel:**
```javascript
// ui.js
async function showScenarioPanel(labId) {
    const scenarios = await api.getScenarios(labId);
    const panel = createScenarioPanel(scenarios);
    showModal(panel);
}

function createScenarioPanel(scenarios) {
    return `
        <div class="scenarios-panel">
            <h3>Configuration Scenarios</h3>
            <div class="scenario-list">
                ${scenarios.map(scenario => `
                    <div class="scenario-card">
                        <h4>${scenario.name}</h4>
                        <p>${scenario.description}</p>
                        <button onclick="applyScenario('${scenario.id}')">
                            Apply
                        </button>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}
```

### Phase 4.3: Real-time Updates (Week 2, Days 1-2)

#### Task 6: Server-Sent Events Implementation
**Backend Addition (if not exists):**
```python
# src/backend/api/events.py
from flask import Response, Blueprint
import json

events_bp = Blueprint('events', __name__)

@events_bp.route('/api/events')
def stream_events():
    def generate():
        # Subscribe to deployment events
        while True:
            event = get_next_event()  # From event queue
            yield f"data: {json.dumps(event)}\n\n"
    
    return Response(generate(), mimetype="text/event-stream")
```

**Frontend SSE Client:**
```javascript
// app.js
let eventSource;

function connectToEventStream() {
    eventSource = new EventSource('/api/events');
    
    eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleRealtimeUpdate(data);
    };
    
    eventSource.onerror = (error) => {
        console.error('SSE Error:', error);
        // Implement reconnection logic
        setTimeout(connectToEventStream, 5000);
    };
}

function handleRealtimeUpdate(data) {
    switch(data.type) {
        case 'deployment_progress':
            updateDeploymentProgress(data);
            break;
        case 'deployment_complete':
            onDeploymentComplete(data);
            break;
        case 'deployment_failed':
            onDeploymentFailed(data);
            break;
        case 'lab_destroyed':
            onLabDestroyed(data);
            break;
    }
}
```

#### Task 7: Deployment Logs Viewer
**Log Streaming UI:**
```html
<div id="logs-viewer" class="logs-panel hidden">
    <div class="logs-header">
        <h3>Deployment Logs: <span id="logs-lab-name"></span></h3>
        <button onclick="closeLogs()">×</button>
    </div>
    <div class="logs-controls">
        <button onclick="toggleAutoScroll()">Auto-scroll</button>
        <button onclick="downloadLogs()">Download</button>
        <button onclick="clearLogs()">Clear</button>
    </div>
    <pre id="logs-content" class="logs-content">
        <!-- Logs appear here -->
    </pre>
</div>
```

**Log Fetching:**
```javascript
// api.js
async function streamLogs(labId, onUpdate) {
    const response = await fetch(`${API_ENDPOINTS.logs(labId)}`);
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    
    while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value);
        onUpdate(chunk);
    }
}
```

### Phase 4.4: UI Enhancements (Week 2, Days 3-4)

#### Task 8: Navigation and Layout
**Tab-based Navigation:**
```html
<nav class="main-nav">
    <div class="nav-brand">
        <h1>Homelab Manager</h1>
        <span class="version">v1.0.0</span>
    </div>
    <ul class="nav-tabs">
        <li><a href="#labs" class="active">Labs</a></li>
        <li><a href="#deployments">Active Deployments</a></li>
        <li><a href="#repositories">Repositories</a></li>
        <li><a href="#system">System</a></li>
    </ul>
</nav>
```

#### Task 9: Status Dashboard
**System Health Panel:**
```javascript
// ui.js
async function updateSystemStatus() {
    const health = await api.getHealth();
    const netboxStatus = await api.getNetboxStatus();
    
    document.getElementById('system-status').innerHTML = `
        <div class="status-grid">
            <div class="status-card ${health.status}">
                <h4>API Status</h4>
                <p>${health.status}</p>
                <small>Version: ${health.version}</small>
            </div>
            <div class="status-card ${netboxStatus.enabled ? 'healthy' : 'disabled'}">
                <h4>NetBox Integration</h4>
                <p>${netboxStatus.enabled ? 'Connected' : 'Disabled'}</p>
                ${netboxStatus.enabled ? `<small>${netboxStatus.available_ips} IPs available</small>` : ''}
            </div>
            <div class="status-card">
                <h4>Active Labs</h4>
                <p>${health.active_labs}</p>
            </div>
        </div>
    `;
}
```

#### Task 10: Error Handling and Notifications
**Toast Notification System:**
```javascript
// ui.js
class NotificationManager {
    constructor() {
        this.container = document.getElementById('notifications');
    }
    
    show(message, type = 'info', duration = 5000) {
        const id = Date.now();
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <span>${message}</span>
            <button onclick="dismissNotification(${id})">×</button>
        `;
        notification.id = `notification-${id}`;
        
        this.container.appendChild(notification);
        
        if (duration > 0) {
            setTimeout(() => this.dismiss(id), duration);
        }
        
        return id;
    }
    
    dismiss(id) {
        const notification = document.getElementById(`notification-${id}`);
        if (notification) {
            notification.classList.add('fade-out');
            setTimeout(() => notification.remove(), 300);
        }
    }
}
```

### Phase 4.5: Testing Implementation (Week 2, Day 5)

#### Task 11: JavaScript Unit Tests
**Test Framework: Jest (via CDN for simplicity)**
```html
<!-- test.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Homelab Manager - Tests</title>
    <script src="https://unpkg.com/jest-lite@1.0.0-alpha.4/dist/core.js"></script>
    <script src="js/api.js"></script>
    <script src="js/utils.js"></script>
    <script src="tests/api.test.js"></script>
    <script src="tests/utils.test.js"></script>
</head>
<body>
    <div id="test-results"></div>
    <script>
        // Run tests and display results
        runTests();
    </script>
</body>
</html>
```

**Example Test File:**
```javascript
// tests/api.test.js
describe('API Client', () => {
    beforeEach(() => {
        // Mock fetch
        global.fetch = jest.fn();
    });
    
    test('getLabs returns parsed JSON', async () => {
        const mockLabs = [{ id: 'lab1', name: 'Test Lab' }];
        fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => mockLabs
        });
        
        const labs = await api.getLabs();
        expect(labs).toEqual(mockLabs);
        expect(fetch).toHaveBeenCalledWith('/api/repos');
    });
    
    test('deployLab sends correct request', async () => {
        fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => ({ task_id: '123' })
        });
        
        await api.deployLab('lab1', 'v1.0.0', true);
        
        expect(fetch).toHaveBeenCalledWith('/api/labs/lab1/deploy', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                version: 'v1.0.0',
                allocate_ips: true
            })
        });
    });
});
```

#### Task 12: Integration Tests
**Selenium-based E2E Tests:**
```python
# tests/e2e/test_web_ui.py
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestWebUI(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.get("http://localhost:5000")
        
    def tearDown(self):
        self.driver.quit()
        
    def test_lab_list_loads(self):
        """Test that labs are displayed on page load"""
        # Wait for labs to load
        wait = WebDriverWait(self.driver, 10)
        labs_section = wait.until(
            EC.presence_of_element_located((By.ID, "labs"))
        )
        
        # Check that at least one lab card is displayed
        lab_cards = self.driver.find_elements(By.CLASS_NAME, "lab-card")
        self.assertGreater(len(lab_cards), 0)
        
    def test_deploy_lab(self):
        """Test deploying a lab through the UI"""
        # Find and click deploy button
        deploy_btn = self.driver.find_element(By.CSS_SELECTOR, ".lab-card button")
        deploy_btn.click()
        
        # Wait for deployment to start
        wait = WebDriverWait(self.driver, 10)
        notification = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "notification"))
        )
        
        self.assertIn("Deployment started", notification.text)
```

### Phase 4.6: Documentation (Week 3, Day 1)

#### Task 13: User Documentation
**docs/web-ui-guide.md:**
```markdown
# Web UI User Guide

## Overview
The Homelab Manager Web UI provides a browser-based interface for managing your lab deployments.

## Accessing the Web UI
1. Ensure the backend is running: `systemctl status labctl-backend`
2. Open your browser to: `http://your-server:5000`
3. The main dashboard will load automatically

## Features

### Lab Browser
- View all available labs with metadata
- Filter by category, vendor, or difficulty
- Search labs by name or tags
- One-click deployment with options

### Deployment Management
- Deploy labs with version selection
- Optional NetBox IP allocation
- Real-time deployment progress
- View deployment logs
- Destroy active deployments

### Repository Management
- Add new Git repositories
- Update repositories to pull latest changes
- Remove unused repositories
- View repository sync status

### Configuration Scenarios
- List available scenarios for deployed labs
- Apply configuration changes
- View scenario descriptions

## Troubleshooting
[Common issues and solutions...]
```

#### Task 14: Developer Documentation
**docs/web-ui-development.md:**
```markdown
# Web UI Development Guide

## Architecture
The web UI is a simple single-page application that uses vanilla JavaScript to interact with the Flask REST API.

## Project Structure
- `static/index.html` - Main HTML page
- `static/css/` - Stylesheets (extracted from inline styles)
- `static/js/` - JavaScript modules
  - `app.js` - Main application logic
  - `api.js` - API client functions
  - `ui.js` - UI update functions
  - `utils.js` - Utility functions
  - `constants.js` - Configuration

## Development Workflow
1. Start the backend: `./run-backend.sh`
2. Make changes to web files
3. Refresh browser (no build process!)
4. Run tests: Open `test.html` in browser

## Adding New Features
[Step-by-step guide for common tasks...]
```

### Phase 4.7: Deployment and Installation (Week 3, Day 2)

#### Task 15: Installation Scripts Update
**Update scripts/install-backend.sh:**
```bash
# After Flask installation, ensure web UI is accessible
echo "Setting up Web UI..."
if [ -d "src/web/static" ]; then
    echo "Web UI files found at src/web/static"
else
    echo "Warning: Web UI files not found!"
fi

# Add nginx configuration for production (optional)
if command -v nginx &> /dev/null; then
    echo "Configuring nginx for Web UI..."
    sudo cp config/nginx/labctl.conf /etc/nginx/conf.d/
    sudo nginx -s reload
fi
```

#### Task 16: Production Configuration
**config/nginx/labctl.conf:**
```nginx
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        
        # SSE support
        proxy_set_header Connection '';
        proxy_http_version 1.1;
        chunked_transfer_encoding off;
        proxy_buffering off;
        proxy_cache off;
    }
    
    # Larger timeouts for long-running operations
    proxy_read_timeout 300s;
    proxy_connect_timeout 300s;
}
```

## Testing Strategy

### Unit Tests
- JavaScript functions tested in isolation
- Mock API responses
- Test UI update logic
- Validate error handling

### Integration Tests
- Test API client with real backend
- Verify data flow
- Test event handling
- Validate state management

### E2E Tests
- Full user workflows
- Browser automation with Selenium
- Cross-browser testing
- Performance benchmarks

### Manual Testing Checklist
- [ ] Lab deployment workflow
- [ ] Repository management
- [ ] Configuration scenarios
- [ ] Error conditions
- [ ] Mobile responsiveness
- [ ] Browser compatibility

## Success Metrics

### Technical
- Page load time < 2 seconds
- API response time < 500ms
- Zero JavaScript errors in console
- Works in Chrome, Firefox, Safari, Edge
- Mobile responsive design

### User Experience
- Intuitive navigation
- Clear status indicators
- Helpful error messages
- Smooth animations
- Consistent design

### Code Quality
- Modular JavaScript structure
- Clear function names
- Comprehensive error handling
- JSDoc comments
- No global namespace pollution

## Risk Mitigation

### Potential Issues
1. **Browser Compatibility**: Test in multiple browsers
2. **API Changes**: Version API endpoints
3. **Large Lab Lists**: Implement pagination
4. **Slow Networks**: Add loading states
5. **Concurrent Updates**: Handle race conditions

### Mitigation Strategies
1. Use standard JavaScript features
2. Implement proper error boundaries
3. Add request debouncing
4. Cache static data
5. Implement optimistic updates

## Implementation Timeline

### Week 1
- Days 1-2: Foundation and refactoring
- Days 3-5: Core features implementation

### Week 2
- Days 1-2: Real-time updates
- Days 3-4: UI enhancements
- Day 5: Testing implementation

### Week 3
- Day 1: Documentation
- Day 2: Deployment and installation

## Deliverables

1. **Refactored Web UI** with modular code structure
2. **Complete Feature Set** including all missing functionality
3. **Test Suite** with unit and integration tests
4. **Documentation** for users and developers
5. **Installation Updates** for easy deployment

## Future Enhancements (Post-Phase 4)

1. **Authentication**: Basic auth or JWT tokens
2. **User Preferences**: Save UI settings
3. **Advanced Filtering**: Complex search queries
4. **Batch Operations**: Deploy multiple labs
5. **Export/Import**: Configuration backup
6. **Dark Mode**: Theme switching
7. **Keyboard Shortcuts**: Power user features
8. **WebSocket Updates**: Replace SSE with WebSockets
9. **Progressive Web App**: Offline capabilities
10. **Metrics Dashboard**: Grafana embedding

## Conclusion

This implementation plan provides a clear path to building a simple, functional, and well-tested web UI for the Homelab Manager. By following these steps, the project will have a professional web interface that complements the existing CLI while maintaining the project's core principle of simplicity.
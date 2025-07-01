# Phase 4 Web UI Implementation Tasks

## Overview
This is a simplified task list for implementing the Phase 4 Web UI. Each task is designed to be completed incrementally with clear deliverables.

## Prerequisites
- Backend API is working (Phase 1-3 complete)
- Flask is serving static files from `src/web/`
- Basic `index.html` exists with prototype functionality

## Implementation Tasks

### Stage 1: Code Refactoring (Priority: HIGH)

**Task 1.1: Extract CSS from index.html**
- Create `src/web/static/css/main.css`
- Move all `<style>` content to main.css
- Add `<link rel="stylesheet" href="/static/css/main.css">` to index.html
- Test that styles still work

**Task 1.2: Extract JavaScript from index.html**
- Create these files in `src/web/static/js/`:
  - `api.js` - All fetch() calls to backend
  - `ui.js` - All DOM manipulation functions
  - `app.js` - Main application logic
  - `constants.js` - API endpoints and config
- Move all `<script>` content to appropriate files
- Add script tags to load JS files in correct order
- Test all functionality still works

**Task 1.3: Fix API Endpoints**
- Update JavaScript to use correct API paths:
  - Change `/labs` to `/api/repos`
  - Change `/deployments` to `/api/deployments`
  - Add other missing endpoints
- Test lab listing and deployment

### Stage 2: Core Features (Priority: HIGH)

**Task 2.1: Repository Management UI**
- Add "Repositories" tab to navigation
- Create repository list view showing all repos
- Add "Add Repository" button and modal
- Implement add/update/delete repository functions
- Test full CRUD operations

**Task 2.2: Deployment Enhancements**
- Add version selection dropdown to deploy modal
- Add "Allocate IPs" checkbox for NetBox
- Show deployment progress with status messages
- Add "View Logs" button for active deployments
- Test deployment with options

**Task 2.3: Configuration Scenarios**
- Add "Scenarios" button to deployed lab cards
- Create modal to list available scenarios
- Implement scenario apply functionality
- Show success/error notifications
- Test scenario application

### Stage 3: Real-time Updates (Priority: MEDIUM)

**Task 3.1: Deployment Status Updates**
- Replace 30-second polling with 5-second polling
- Update deployment cards with current status
- Show progress percentage if available
- Auto-remove completed deployments after success
- Test status updates work smoothly

**Task 3.2: Logs Viewer**
- Create expandable logs panel
- Implement `/api/logs/<lab_id>` fetching
- Add auto-scroll option
- Add download logs button
- Test log viewing for deployments

### Stage 4: UI Polish (Priority: MEDIUM)

**Task 4.1: Navigation Improvements**
- Implement tab switching without page reload
- Add active tab highlighting
- Show count badges (e.g., active deployments)
- Add simple routing with hash fragments
- Test navigation flow

**Task 4.2: Error Handling**
- Create toast notification system
- Show user-friendly error messages
- Add retry buttons for failed operations
- Implement connection error detection
- Test various error scenarios

**Task 4.3: Loading States**
- Add loading spinners for all async operations
- Disable buttons during operations
- Show skeleton cards while loading
- Add progress bars where applicable
- Test loading states appear correctly

### Stage 5: Testing (Priority: HIGH)

**Task 5.1: JavaScript Unit Tests**
- Create `src/web/static/tests/` directory
- Write tests for api.js functions
- Write tests for ui.js functions
- Create simple test runner HTML page
- Ensure 80%+ code coverage

**Task 5.2: Manual Test Plan**
- Create `docs/web-ui-testing.md`
- Document all user workflows to test
- Create test data setup instructions
- List browser compatibility requirements
- Include mobile testing steps

**Task 5.3: Integration Tests**
- Write Python tests using Selenium
- Test critical user paths:
  - View labs → Deploy lab → Check status
  - Add repository → View in list
  - Apply scenario → Verify success
- Add to existing test suite

### Stage 6: Documentation (Priority: HIGH)

**Task 6.1: User Guide**
- Create `docs/web-ui-user-guide.md`
- Include screenshots of key features
- Document each major workflow
- Add troubleshooting section
- Keep it simple and visual

**Task 6.2: Development Guide**
- Update `docs/development.md` with web UI section
- Document file structure and architecture
- Explain how to add new features
- Include code style guidelines
- Add debugging tips

### Stage 7: Installation (Priority: MEDIUM)

**Task 7.1: Update Installation Scripts**
- Ensure web files are included in installation
- Add web UI URL to post-install message
- Test installation on clean system
- Update README with web UI access info

**Task 7.2: Production Readiness**
- Add cache headers for static files
- Ensure proper error pages (404, 500)
- Add basic security headers
- Test with nginx reverse proxy
- Document production deployment

## Implementation Order

1. **Week 1**: Complete Stages 1-2 (Refactoring and Core Features)
2. **Week 2**: Complete Stages 3-4 (Real-time Updates and UI Polish)
3. **Week 3**: Complete Stages 5-7 (Testing, Documentation, Installation)

## Definition of Done

Each task is complete when:
1. Code is implemented and working
2. Manually tested in Chrome and Firefox
3. No JavaScript errors in console
4. Code follows existing style
5. Basic error handling is in place

## Tips for Implementation

1. **Start Simple**: Get basic functionality working first
2. **Test Often**: Refresh browser after each change
3. **Use Browser DevTools**: Console and Network tabs are your friends
4. **Keep Compatibility**: Use standard JavaScript (ES6 is fine)
5. **Avoid Dependencies**: No need for jQuery, React, etc.

## Quick Wins

If time is limited, prioritize these high-impact tasks:
1. Fix API endpoints (Task 1.3)
2. Add repository management (Task 2.1)
3. Improve error handling (Task 4.2)
4. Create user guide (Task 6.1)

## Testing the Implementation

After each stage, verify:
```bash
# Backend is running
curl http://localhost:5000/api/health

# Web UI loads
curl http://localhost:5000/

# API endpoints work
curl http://localhost:5000/api/repos
```

Then open http://localhost:5000 in your browser and test the features.

## Success Criteria

The Phase 4 Web UI is successful when:
- All existing CLI features are accessible via web
- Code is organized into logical modules
- UI is responsive and provides good feedback
- Basic tests exist and pass
- Documentation helps new users get started
- Installation is still simple and reliable
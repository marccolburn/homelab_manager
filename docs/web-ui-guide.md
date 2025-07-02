# Web UI User Guide

The Homelab Manager provides a modern web interface for managing network topology labs. This guide covers all features and functionality available through the web UI.

## Accessing the Web UI

### Development Environment
- **URL**: `http://localhost:5001`
- **Requirements**: Backend server must be running (`./scripts/run-backend.sh`)

### Production Environment
- **URL**: `http://your-server:5001` (or configured port)
- **Requirements**: Backend installed and running as systemd service

## Main Dashboard

### Navigation
The main dashboard provides three primary tabs:

#### 1. Labs Tab
- **View**: Grid of available lab repositories
- **Features**:
  - Lab metadata display (name, description, vendor, difficulty)
  - Version/tag information
  - Resource requirements
  - Quick deployment with version selection
  - Deploy with NetBox IP allocation option

#### 2. Active Deployments Tab
- **View**: List of currently running lab deployments
- **Features**:
  - Deployment status and duration
  - Lab information and version
  - Quick destroy action
  - View deployment logs
  - Real-time status updates

#### 3. Repositories Tab
- **View**: List of registered lab repositories
- **Features**:
  - Repository information (URL, branch, last update)
  - Add new repositories via Git URL
  - Update existing repositories
  - Remove repositories
  - Repository validation status

### Quick Actions

#### Deploy a Lab
1. Navigate to **Labs** tab
2. Find desired lab in the grid
3. Select version from dropdown (latest/tags)
4. Optional: Check "Allocate IPs" for NetBox integration
5. Click **Deploy** button
6. Monitor progress in **Active Deployments** tab

#### Add Repository
1. Navigate to **Repositories** tab
2. Click **➕ Add Repository** button
3. Enter Git repository URL (SSH or HTTPS)
4. Click **Add Repository**
5. New lab appears in Labs tab after processing

#### View Deployment Logs
1. Go to **Active Deployments** tab
2. Find your deployment
3. Click **View Logs** button
4. Real-time log output displays deployment progress

## Settings Page

### Accessing Settings
- Click **⚙️ Settings** button in the top-right corner of main dashboard
- Or navigate directly to `http://localhost:5001/settings.html`

### Configuration Sections

#### 1. Remote Credentials
Configure passwords for remote lab host operations:

- **clab-tools Password**: Password for clab-tools operations
- **SSH Password**: SSH authentication to remote lab host
- **Sudo Password**: Sudo operations on remote lab host

**Security Features**:
- Passwords are masked in the interface
- Secure storage in backend configuration
- Never transmitted in plain text

#### 2. NetBox Integration
Configure NetBox for dynamic IP allocation:

- **Enable NetBox Integration**: Toggle NetBox functionality
- **NetBox URL**: NetBox instance URL
- **API Token**: NetBox API authentication token
- **Default Prefix**: IP prefix for lab management networks

#### 3. Monitoring
Configure monitoring system URLs:

- **Prometheus URL**: Prometheus metrics collection
- **Grafana URL**: Grafana dashboard access

### Settings Actions

#### Save Settings
1. Configure desired settings in each section
2. Click **💾 Save Settings** button
3. Success confirmation displays
4. Settings persist across backend restarts

#### Test Connection
1. Configure settings (especially NetBox)
2. Click **🔍 Test Connection** button
3. Connection test results display:
   - Backend API connectivity
   - NetBox connectivity (if configured)
   - Status and error messages

## Advanced Features

### Lab Deployment Options

#### Version Selection
- **Latest**: Deploy most recent commit from main branch
- **Tags**: Deploy specific version tags (v1.0.0, v1.1.0, etc.)
- Version dropdown shows available options

#### NetBox IP Allocation
- Enable "Allocate IPs" during deployment
- Requires NetBox configuration in Settings
- Automatically assigns management IPs to lab nodes
- IPs released when lab is destroyed

### Repository Management

#### Supported Repository Types
- **GitHub**: `git@github.com:user/repo.git` or `https://github.com/user/repo.git`
- **GitLab**: Similar SSH/HTTPS formats
- **Private Repositories**: SSH key authentication required

#### Repository Updates
- Manual: Click update button in Repositories tab
- Automatic: Backend periodically checks for updates
- Version tags automatically detected

### Real-time Updates

#### Status Monitoring
- Deployment status updates every 30 seconds
- Progress indicators for active operations
- Error notifications for failed operations

#### Log Streaming
- Real-time deployment log viewing
- Automatic scrolling to latest output
- Error highlighting and formatting

## Troubleshooting

### Common Issues

#### Web UI Not Loading
1. Verify backend is running: `./scripts/run-backend.sh`
2. Check URL and port: `http://localhost:5001`
3. Check browser console for JavaScript errors

#### Settings Not Saving
1. Verify form data is complete
2. Check network connectivity to backend
3. Review backend logs for error messages

#### Deployment Failures
1. Check Settings page for proper configuration
2. Verify remote host connectivity
3. Review deployment logs for specific errors
4. Ensure SSH keys are properly configured

#### Repository Add Failures
1. Verify Git URL format is correct
2. Check SSH key access for private repositories
3. Ensure repository contains required lab structure

### Browser Compatibility
- **Supported**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **Features**: Modern JavaScript (ES6+), CSS Grid, Flexbox
- **Requirements**: JavaScript enabled, local storage access

### Performance Tips
- **Lab Grid**: Large numbers of labs load efficiently
- **Log Viewing**: Logs are streamed efficiently for real-time viewing
- **Background Updates**: Minimal bandwidth usage for status polling

## Integration with CLI

### Consistency
- Web UI and CLI use identical backend API
- All operations available in both interfaces
- Configuration changes apply to both

### Workflow Examples

#### Web UI → CLI
1. Deploy lab via web UI
2. Manage lab via CLI: `labctl status`, `labctl logs lab-id`
3. Destroy via either interface

#### CLI → Web UI
1. Add repository via CLI: `labctl repo add git-url`
2. Deploy via web UI with visual interface
3. Monitor status in web UI dashboard

## Security Considerations

### Password Security
- Passwords never displayed in plain text
- Secure transmission via HTTPS (in production)
- Encrypted storage in backend configuration

### Access Control
- Web UI requires backend access
- No built-in authentication (use reverse proxy for production)
- Session management via browser localStorage

### Network Security
- Development: HTTP on localhost only
- Production: Use HTTPS with proper certificates
- Firewall: Restrict access to trusted networks

## Customization

### Styling
- CSS files in `src/web/static/css/`
- Modern design system with CSS variables
- Responsive layout for mobile/tablet

### Adding Features
- JavaScript modules in `src/web/static/js/`
- API client functions in `api.js`
- UI helpers in `ui.js`

### Configuration
- API endpoints in `constants.js`
- Polling intervals and timeouts configurable
- Color scheme and branding customizable via CSS
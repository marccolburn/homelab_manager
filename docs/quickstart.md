# Quick Start Guide

Get up and running with Homelab Manager in 5 minutes.

## Prerequisites

- Python 3.11+ installed
- `clab-tools` installed and working
- SSH access to a lab host (for remote deployments)

## Step 1: Install

```bash
git clone https://github.com/your-org/homelab-manager.git
cd homelab-manager
./scripts/install-labctl.sh
```

## Step 2: Start Backend

```bash
./scripts/run-backend.sh
```

The backend starts on `http://localhost:5001`

## Step 3: Configure Remote Access

### Option A: Web UI (Recommended)
1. Open `http://localhost:5001/settings.html`
2. Enter your remote host credentials:
   - SSH Password
   - Sudo Password (if needed)
3. Click "Save Settings"
4. Click "Test Connection" to verify

### Option B: Command Line
```bash
# Configure via environment variables
export CLAB_TOOLS_PASSWORD="your-password"
export CLAB_REMOTE_PASSWORD="ssh-password"
export CLAB_REMOTE_SUDO_PASSWORD="sudo-password"
```

## Step 4: Add a Lab Repository

### Web UI
1. Go to `http://localhost:5001`
2. Click "Repositories" tab
3. Click "➕ Add Repository"
4. Enter Git URL: `git@github.com:user/lab-repo.git`
5. Click "Add Repository"

### CLI
```bash
labctl repo add git@github.com:user/lab-repo.git
```

## Step 5: Deploy Your First Lab

### Web UI
1. Go to "Labs" tab
2. Find your lab
3. Select version (latest/specific tag)
4. Optional: Check "Allocate IPs" for NetBox integration
5. Click "Deploy"
6. Monitor progress in "Active Deployments" tab

### CLI
```bash
# List available labs
labctl repo list

# Deploy a lab
labctl deploy lab-name

# Check deployment status
labctl status

# View deployment logs
labctl logs lab-name
```

## Step 6: Manage Your Lab

### View Active Deployments
- **Web UI**: "Active Deployments" tab shows running labs
- **CLI**: `labctl status`

### Destroy a Lab
- **Web UI**: Click "Destroy" button in Active Deployments
- **CLI**: `labctl destroy lab-name`

### View Logs
- **Web UI**: Click "View Logs" in Active Deployments
- **CLI**: `labctl logs lab-name`

## Next Steps

- **[Web UI Guide](web-ui-guide.md)** - Detailed web interface usage
- **[CLI Reference](commands.md)** - Complete command documentation
- **[Configuration](configuration.md)** - Advanced settings and NetBox setup

## Troubleshooting

### Backend Won't Start
```bash
# Check if port 5001 is in use
lsof -i :5001

# Check logs
tail -f ~/.labctl/logs/backend.log
```

### Can't Connect to Remote Host
1. Verify SSH access: `ssh user@remote-host`
2. Check credentials in Settings page
3. Ensure `clab-tools` is installed on remote host

### Repository Add Fails
1. Verify Git URL format
2. Check SSH key access for private repos
3. Ensure repo has required lab structure

### Deployment Fails
1. Check deployment logs in Web UI or CLI
2. Verify remote host connectivity
3. Check Settings configuration
4. Ensure sufficient resources on remote host

For more help, see the complete documentation in the `docs/` directory.
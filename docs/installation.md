# Installation Guide

Complete installation guide for Homelab Manager. Choose the installation method that best fits your setup.

## Prerequisites

- **Python 3.11+** 
- **clab-tools** installed and configured
- **SSH access** to lab host (for remote deployments)
- **Git** for repository management

## Installation Methods

### Option 1: All-in-One (Recommended)

Install both backend and CLI on the same system:

```bash
git clone https://github.com/your-org/homelab-manager.git
cd homelab-manager
./scripts/install-labctl.sh
```

**What this installs:**
- Flask backend server
- CLI client (`labctl` command)
- Web UI (served by backend)
- All dependencies and configuration

**After installation:**
```bash
# Start backend
./scripts/run-backend.sh

# Access web UI
open http://localhost:5001

# Use CLI
labctl --help
```

### Option 2: Backend Only (Server Installation)

For dedicated lab server deployment:

```bash
git clone https://github.com/your-org/homelab-manager.git
cd homelab-manager
./scripts/install-backend.sh
```

**What this installs:**
- Flask backend server
- Web UI
- systemd service (production mode)

**Start as service:**
```bash
sudo systemctl enable labctl-backend
sudo systemctl start labctl-backend
```

### Option 3: CLI Only (Workstation)

For connecting to an existing backend:

```bash
git clone https://github.com/your-org/homelab-manager.git
cd homelab-manager
./scripts/install-frontend.sh
```

**Configuration:**
```bash
# Configure backend URL
export BACKEND_URL=http://lab-server:5001
labctl repo list
```

## Post-Installation Setup

### 1. Configure Remote Credentials

#### Via Web UI (Easiest)
1. Open `http://localhost:5001/settings.html`
2. Enter remote SSH credentials
3. Test connection

#### Via Configuration File
```bash
# Edit configuration
nano ~/.labctl/config.yaml

# Add credentials
clab_tools_password: "your-password"
remote_credentials:
  ssh_password: "ssh-password"
  sudo_password: "sudo-password"
```

### 2. Verify Installation

```bash
# Check system health
labctl doctor

# Test backend connectivity
curl http://localhost:5001/api/health

# Check web UI
open http://localhost:5001
```

## Network Configuration

### Development (Default)
- **Backend**: `http://localhost:5001`
- **Web UI**: `http://localhost:5001`
- **API**: `http://localhost:5001/api/*`

### Production
```bash
# Configure firewall (RHEL/Fedora)
sudo firewall-cmd --permanent --add-port=5001/tcp
sudo firewall-cmd --reload

# Run on all interfaces
FLASK_HOST=0.0.0.0 ./scripts/run-backend.sh
```

## Troubleshooting

### Installation Fails

**Check Python version:**
```bash
python3 --version  # Should be 3.11+
```

**Check permissions:**
```bash
chmod +x scripts/install-labctl.sh
```

**Manual installation:**
```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/backend.txt
```

### Backend Won't Start

**Check port availability:**
```bash
lsof -i :5001
```

**Use different port:**
```bash
PORT=5002 ./scripts/run-backend.sh
```

**Check logs:**
```bash
tail -f ~/.labctl/logs/backend.log
```

### CLI Command Not Found

**Add to PATH:**
```bash
export PATH="$HOME/.local/bin:$PATH"
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
```

**Use direct path:**
```bash
~/.local/bin/labctl --help
```

## Directory Structure

After installation:

```
~/.labctl/                          # User configuration
├── config.yaml                    # Main configuration
├── repos/                         # Lab repositories  
├── logs/                          # Deployment logs
└── state.json                     # Application state

homelab-manager/                    # Installation directory
├── src/backend/                   # Flask API server
├── src/cli/                       # CLI client
├── src/web/static/               # Web UI files
└── scripts/                      # Utility scripts
```

## Upgrading

### Update Installation

```bash
cd homelab-manager
git pull origin main
./scripts/install-labctl.sh  # Reinstall
```

### Backup Configuration

```bash
# Backup before upgrade
cp ~/.labctl/config.yaml ~/.labctl/config.yaml.backup

# Restore if needed
cp ~/.labctl/config.yaml.backup ~/.labctl/config.yaml
```

## Uninstallation

### Remove Installation

```bash
# Stop backend
pkill -f "src.backend.app"

# Remove CLI
rm ~/.local/bin/labctl

# Remove virtual environment
rm -rf homelab-manager/.venv

# Remove configuration (optional)
rm -rf ~/.labctl/
```

### Remove systemd Service

```bash
sudo systemctl stop labctl-backend
sudo systemctl disable labctl-backend
sudo rm /etc/systemd/system/labctl-backend.service
sudo systemctl daemon-reload
```
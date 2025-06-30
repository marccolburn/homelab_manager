# Installation Guide

This guide covers installing the Homelab Manager system on RHEL/Fedora systems. There are three installation scenarios:

1. **Split Deployment** (Recommended): Backend on lab server, CLI on workstation
2. **All-in-One**: Both backend and CLI on the same system  
3. **CLI-Only**: Just the CLI tools for connecting to an existing backend

## Prerequisites

### System Requirements

**Lab Server (Backend):**
- RHEL 9+, CentOS Stream 9+, or Fedora 40+
- Python 3.8+
- 4GB RAM minimum, 8GB+ recommended
- 50GB+ disk space for lab storage
- clab-tools installed and configured

**User Workstation (CLI):**
- Linux or macOS
- Python 3.8+
- Network access to lab server

### Network Requirements
- Port 5000/tcp open on lab server (for API)
- SSH access to lab server
- Internet access for Git repositories

## Installation Scenarios

### Scenario 1: Split Deployment (Recommended)

This is the typical production setup where you manage labs from your laptop/workstation but containerlab runs on a dedicated server.

#### Step 1: Install Backend on Lab Server

**On your RHEL/Fedora lab server:**

```bash
# Clone the repository
git clone <homelab-manager-repo-url>
cd homelab-manager

# Run automated backend installation
sudo ./install-backend.sh
```

**What the script does:**
- Installs system dependencies (Python, Git, firewalld)
- Creates dedicated service user (`labctl`)
- Sets up Python virtual environment with backend dependencies
- Configures firewalld (opens port 5000/tcp)
- Installs and starts systemd service
- Tests the installation

**Manual verification:**
```bash
# Check service status
systemctl status labctl-backend

# Test API endpoint
curl http://localhost:5000/api/health

# View logs
journalctl -u labctl-backend -f
```

#### Step 2: Install CLI on Your Workstation

**On your laptop/workstation (macOS or Linux):**

```bash
# Clone repository (you can clone just what you need)
git clone <homelab-manager-repo-url>
cd homelab-manager

# Run automated frontend installation
./install-frontend.sh
```

**What the script does:**
- Detects OS (macOS/Linux) and shell
- Sets up user-space Python virtual environment
- Installs only CLI dependencies
- Configures CLI command
- Prompts for backend server URL
- Tests connection

**Manual configuration (if needed):**
```bash
# Set backend URL
export LABCTL_API_URL="http://your-lab-server:5000"

# Add to shell profile permanently
echo 'export LABCTL_API_URL="http://your-lab-server:5000"' >> ~/.bashrc
# or for macOS zsh:
echo 'export LABCTL_API_URL="http://your-lab-server:5000"' >> ~/.zshrc
```

### Scenario 2: All-in-One Installation

Install both backend and CLI on the same system (good for development or single-user setups).

**On RHEL/Fedora system:**

```bash
# Clone repository
git clone <homelab-manager-repo-url>
cd homelab-manager

# Run all-in-one installation
sudo ./install-labctl.sh
```

**What the script does:**
- Installs system dependencies
- Sets up virtual environment with all dependencies
- Installs CLI command
- Optionally installs and starts backend service
- Configures firewalld if backend is installed
- Sets up local API connection

### Scenario 3: CLI-Only Installation

Install just the CLI to connect to an existing backend server.

**Minimal installation (any Linux/macOS):**

```bash
# Download CLI files
curl -O https://raw.githubusercontent.com/user/homelab-manager/main/labctl.py
curl -O https://raw.githubusercontent.com/user/homelab-manager/main/labctl.sh
curl -O https://raw.githubusercontent.com/user/homelab-manager/main/requirements-frontend.txt

# Set up environment
python3 -m venv ~/.labctl
~/.labctl/bin/pip install -r requirements-frontend.txt

# Configure CLI
cp labctl.py ~/.labctl/
chmod +x labctl.sh
sudo ln -sf "$(pwd)/labctl.sh" /usr/local/bin/labctl

# Set backend URL
export LABCTL_API_URL="http://your-backend-server:5000"
```

## RHEL/Fedora Specific Configuration

### Firewalld Configuration

**On backend server, the install script automatically configures:**
```bash
# Open API port
firewall-cmd --permanent --add-port=5000/tcp
firewall-cmd --reload
```

**For additional security, restrict access to specific IPs:**
```bash
# Remove general rule
firewall-cmd --permanent --remove-port=5000/tcp

# Add specific source IPs
firewall-cmd --permanent --add-rich-rule='rule family="ipv4" source address="192.168.1.100" port protocol="tcp" port="5000" accept'
firewall-cmd --reload
```

**For SSH tunnel access (most secure):**
```bash
# Don't open port 5000 publicly
# Instead, use SSH tunnel from workstation:
ssh -L 5000:localhost:5000 user@lab-server

# Then set: export LABCTL_API_URL="http://localhost:5000"
```

### SELinux Considerations

**If you encounter SELinux issues:**
```bash
# Check for denials
ausearch -m AVC -ts recent

# Generate policy if needed
ausearch -m AVC -ts recent | audit2allow -M labctl-backend
semodule -i labctl-backend.pp
```

**Or temporarily set permissive mode for testing:**
```bash
# Temporary (until reboot)
setenforce 0

# Check current mode
getenforce
```

### Systemd Service Management

**Backend service commands:**
```bash
# Start/stop service
systemctl start labctl-backend
systemctl stop labctl-backend

# Enable/disable autostart
systemctl enable labctl-backend
systemctl disable labctl-backend

# Check status
systemctl status labctl-backend

# View logs
journalctl -u labctl-backend -f
journalctl -u labctl-backend --since "1 hour ago"

# Restart after config changes
systemctl restart labctl-backend
```

## Verification and Testing

### Test Backend Installation

**On lab server:**
```bash
# Check service
systemctl status labctl-backend

# Test API
curl http://localhost:5000/api/health
curl http://localhost:5000/api/repos

# Check firewall
firewall-cmd --list-ports
ss -tlnp | grep :5000
```

### Test CLI Installation

**On workstation:**
```bash
# Check CLI command
which labctl
labctl --help

# Test connection to backend
labctl version

# List repositories (should be empty initially)
labctl repo list
```

### Test End-to-End Workflow

**From workstation:**
```bash
# Add a test repository
labctl repo add https://github.com/user/test-lab.git

# List labs
labctl repo list

# Deploy a lab (if available)
labctl deploy test-lab

# Check status
labctl status

# View logs
labctl logs test-lab

# Destroy lab
labctl destroy test-lab
```

## Troubleshooting

### Common Issues

#### 1. "Cannot connect to backend" Error

**Check network connectivity:**
```bash
# Test basic connectivity
curl -v http://lab-server:5000/api/health
telnet lab-server 5000

# Check if port is open
nmap -p 5000 lab-server
```

**Check firewall:**
```bash
# On lab server
firewall-cmd --list-all
ss -tlnp | grep :5000

# If needed, open port
firewall-cmd --permanent --add-port=5000/tcp
firewall-cmd --reload
```

#### 2. Backend Service Won't Start

**Check logs:**
```bash
journalctl -u labctl-backend -f
systemctl status labctl-backend
```

**Common fixes:**
```bash
# Check Python path
which python3
/opt/homelab-manager/.venv/bin/python --version

# Check permissions
ls -la /opt/homelab-manager
chown -R labctl:labctl /opt/homelab-manager

# Check for port conflicts
ss -tlnp | grep :5000
```

#### 3. clab-tools Not Found

**On lab server:**
```bash
# Check if clab-tools is installed
which clab-tools
clab-tools --help

# If not found, install clab-tools first
# (Follow clab-tools installation guide)

# Check service environment
systemctl edit labctl-backend
# Add if needed:
[Service]
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
```

#### 4. Git Authentication Issues

**Set up SSH keys for service user:**
```bash
# Switch to service user
sudo -u labctl -s

# Generate SSH key
ssh-keygen -t ed25519 -C "labctl@$(hostname)"

# Display public key
cat ~/.ssh/id_ed25519.pub
# Add this to your Git service (GitHub, GitLab, etc.)

# Test Git access
git clone git@github.com:user/test-repo.git
```

#### 5. Permission Denied on CLI Installation

**Alternative installation paths:**
```bash
# Install to user directory instead
mkdir -p ~/bin
ln -sf "$(pwd)/labctl.sh" ~/bin/labctl
export PATH="$HOME/bin:$PATH"

# Or use the full path
/path/to/homelab-manager/labctl.sh --help
```

## Security Hardening

### Production Security

**1. Use SSL/TLS:**
```bash
# Install nginx reverse proxy
dnf install -y nginx

# Configure SSL termination
# /etc/nginx/conf.d/labctl.conf
server {
    listen 443 ssl;
    server_name lab-api.example.com;
    
    ssl_certificate /etc/ssl/certs/labctl.crt;
    ssl_certificate_key /etc/ssl/private/labctl.key;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Update firewall
firewall-cmd --permanent --remove-port=5000/tcp
firewall-cmd --permanent --add-service=https
firewall-cmd --reload
```

**2. Restrict Network Access:**
```bash
# Allow only specific subnets
firewall-cmd --permanent --add-rich-rule='rule family="ipv4" source address="192.168.1.0/24" port protocol="tcp" port="5000" accept'
```

**3. Use SSH Tunnels:**
```bash
# On workstation, create tunnel
ssh -L 5000:localhost:5000 user@lab-server

# Set local API URL
export LABCTL_API_URL="http://localhost:5000"
```

## Next Steps

After successful installation:

1. **Add Lab Repositories**: `labctl repo add <git-url>`
2. **Configure Monitoring**: Set up Prometheus/Grafana stack
3. **Set up NetBox Integration**: Configure IP allocation
4. **Create Lab Templates**: Follow lab creation guide
5. **Set up Backups**: Backup configurations and state

## Support

For installation issues:
- Check system logs: `journalctl -u labctl-backend`
- Verify requirements are met
- Review firewall configuration
- Test network connectivity
- Create issue in project repository
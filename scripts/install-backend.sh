#!/bin/bash
# Backend Installation Script for RHEL/Fedora Lab Servers
# This installs the Flask API backend and configures it as a systemd service

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="/opt/homelab-manager"
SERVICE_USER="labctl"
SERVICE_GROUP="labctl"

echo "🚀 Installing Homelab Manager Backend on RHEL/Fedora..."
echo "This will install the Flask API backend for lab management."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run as root (use sudo)"
    exit 1
fi

# Check for RHEL/Fedora
if ! command -v dnf &> /dev/null && ! command -v yum &> /dev/null; then
    echo "❌ This script is designed for RHEL/Fedora systems with dnf/yum"
    exit 1
fi

# Install system dependencies
echo "📦 Installing system dependencies..."
if command -v dnf &> /dev/null; then
    dnf update -y
    dnf install -y python3 python3-pip python3-venv git firewalld
else
    yum update -y
    yum install -y python3 python3-pip python3-venv git firewalld
fi

# Enable and start firewalld
systemctl enable firewalld
systemctl start firewalld

# Check for clab-tools
if ! command -v clab-tools &> /dev/null; then
    echo "⚠️  Warning: clab-tools not found in PATH"
    echo "   The backend requires clab-tools to function properly"
    echo "   Please install clab-tools before proceeding"
    read -p "Continue anyway? (y/N): " -r
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create service user
echo "👤 Creating service user..."
if ! id "$SERVICE_USER" &>/dev/null; then
    useradd -r -s /bin/false -d /opt/homelab-manager "$SERVICE_USER"
fi

# Create installation directory
echo "📁 Setting up installation directory..."
mkdir -p "$INSTALL_DIR"

# Get the project root (parent of scripts directory)
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Copy necessary files and directories
cp -r "$PROJECT_ROOT/src" "$INSTALL_DIR/"
cp -r "$PROJECT_ROOT/requirements" "$INSTALL_DIR/"
cp "$PROJECT_ROOT/README.md" "$INSTALL_DIR/" 2>/dev/null || true

# Copy requirements files to expected location
cp "$PROJECT_ROOT/requirements/backend.txt" "$INSTALL_DIR/requirements-backend.txt" 2>/dev/null || \
  cp "$PROJECT_ROOT/requirements-backend.txt" "$INSTALL_DIR/requirements-backend.txt"

chown -R "$SERVICE_USER":"$SERVICE_GROUP" "$INSTALL_DIR"

# Set up virtual environment
echo "🐍 Setting up Python virtual environment..."
cd "$INSTALL_DIR"
sudo -u "$SERVICE_USER" python3 -m venv .venv
sudo -u "$SERVICE_USER" .venv/bin/pip install --upgrade pip
sudo -u "$SERVICE_USER" .venv/bin/pip install -r requirements-backend.txt

# Configure firewall
echo "🔥 Configuring firewall..."
firewall-cmd --permanent --add-port=5000/tcp
firewall-cmd --reload

# Create systemd service
echo "⚙️  Installing systemd service..."
cat > /etc/systemd/system/labctl-backend.service << EOF
[Unit]
Description=Labctl Backend API Service
After=network.target

[Service]
Type=simple
User=$SERVICE_USER
Group=$SERVICE_GROUP
WorkingDirectory=$INSTALL_DIR
Environment="PATH=$INSTALL_DIR/.venv/bin:/usr/local/bin:/usr/bin:/bin"
Environment="FLASK_ENV=production"
ExecStart=$INSTALL_DIR/.venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 4 src.backend.app:app
Restart=on-failure
RestartSec=10

# Security settings
NoNewPrivileges=true
PrivateTmp=true

# Logging
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable service
systemctl daemon-reload
systemctl enable labctl-backend

# Set up log rotation
echo "📝 Setting up log rotation..."
cat > /etc/logrotate.d/labctl-backend << EOF
/var/log/labctl-backend.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    sharedscripts
    postrotate
        systemctl reload labctl-backend
    endscript
}
EOF

# Start the service
echo "🚀 Starting labctl-backend service..."
systemctl start labctl-backend

# Wait a moment for service to start
sleep 3

# Verify installation
if systemctl is-active --quiet labctl-backend; then
    echo "✅ Backend service started successfully!"
    
    # Test API endpoint
    if curl -s http://localhost:5000/api/health > /dev/null; then
        echo "✅ API endpoint is responding"
        
        # Get the server's IP address
        SERVER_IP=$(ip route get 1.1.1.1 | awk '{print $7; exit}')
        
        echo ""
        echo "🎉 Installation complete!"
        echo ""
        echo "Backend is running at:"
        echo "  - Local: http://localhost:5000"
        echo "  - Network: http://$SERVER_IP:5000"
        echo ""
        echo "Service management:"
        echo "  - Status: systemctl status labctl-backend"
        echo "  - Logs: journalctl -u labctl-backend -f"
        echo "  - Restart: systemctl restart labctl-backend"
        echo ""
        echo "Next steps:"
        echo "  1. Install CLI on your workstation using install-frontend.sh"
        echo "  2. Set LABCTL_API_URL=http://$SERVER_IP:5000 on your workstation"
        echo "  3. Test with: labctl repo list"
        
    else
        echo "⚠️  Service started but API not responding"
        echo "Check logs: journalctl -u labctl-backend -f"
    fi
else
    echo "❌ Failed to start backend service"
    echo "Check logs: journalctl -u labctl-backend -f"
    echo "Check status: systemctl status labctl-backend"
    exit 1
fi
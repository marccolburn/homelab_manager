#!/bin/bash
# All-in-One Installation Script for RHEL/Fedora
# This installs both CLI and backend on the same system

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLI_SCRIPT="$SCRIPT_DIR/labctl"
INSTALL_PATH="/usr/local/bin/labctl"

echo "🚀 Installing Homelab Manager (All-in-One) on RHEL/Fedora..."
echo "This installs both CLI and backend on the same system."

# Detect if we're on RHEL/Fedora
if ! command -v dnf &> /dev/null && ! command -v yum &> /dev/null; then
    echo "⚠️  This script is optimized for RHEL/Fedora systems"
    echo "For other systems, use install-backend.sh and install-frontend.sh separately"
    read -p "Continue anyway? (y/N): " -r
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Get the project root
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Check if source code exists
if [ ! -d "$PROJECT_ROOT/src" ]; then
    echo "❌ Error: src directory not found in $PROJECT_ROOT"
    exit 1
fi

# Install system dependencies (if running as root)
if [ "$EUID" -eq 0 ]; then
    echo "📦 Installing system dependencies..."
    if command -v dnf &> /dev/null; then
        dnf install -y python3 python3-pip python3-venv git
    elif command -v yum &> /dev/null; then
        yum install -y python3 python3-pip python3-venv git
    fi
else
    echo "💡 Note: Run as root to install system dependencies automatically"
fi

# Make sure the CLI script is executable
chmod +x "$CLI_SCRIPT"

# Check if virtual environment exists
if [ ! -f "$PROJECT_ROOT/.venv/bin/python" ]; then
    echo "🐍 Setting up virtual environment..."
    
    # Create virtual environment
    python3 -m venv "$PROJECT_ROOT/.venv"
    
    # Install dependencies
    echo "Installing dependencies..."
    "$PROJECT_ROOT/.venv/bin/pip" install --upgrade pip
    
    # Install from the appropriate requirements file
    if [ -f "$PROJECT_ROOT/requirements/all.txt" ]; then
        "$PROJECT_ROOT/.venv/bin/pip" install -r "$PROJECT_ROOT/requirements/all.txt"
    elif [ -f "$PROJECT_ROOT/requirements.txt" ]; then
        "$PROJECT_ROOT/.venv/bin/pip" install -r "$PROJECT_ROOT/requirements.txt"
    else
        echo "❌ Could not find requirements.txt"
        exit 1
    fi
fi

# Use the pre-made CLI wrapper script
CLI_WRAPPER="$CLI_SCRIPT"

# Verify the wrapper exists
if [ ! -f "$CLI_WRAPPER" ]; then
    echo "❌ Error: CLI wrapper script not found at $CLI_WRAPPER"
    exit 1
fi

# Check if clab-tools is installed
if command -v clab-tools &> /dev/null; then
    echo "✅ Found clab-tools installation"
else
    echo "⚠️  Warning: clab-tools not found in PATH"
    echo "   labctl requires clab-tools to function properly"
    echo "   Please ensure clab-tools is installed and accessible"
fi

# Create CLI symlink
echo "🔗 Installing CLI command..."
if [ "$EUID" -eq 0 ]; then
    ln -sf "$CLI_WRAPPER" "$INSTALL_PATH"
    echo "✅ CLI installed to $INSTALL_PATH"
elif [ -w "/usr/local/bin" ]; then
    ln -sf "$CLI_WRAPPER" "$INSTALL_PATH"
    echo "✅ CLI installed to $INSTALL_PATH"
else
    echo "Creating CLI symlink (requires sudo)..."
    sudo ln -sf "$CLI_WRAPPER" "$INSTALL_PATH"
    if [ $? -eq 0 ]; then
        echo "✅ CLI installed to $INSTALL_PATH"
    else
        echo "❌ CLI installation failed. Please check permissions and try again."
        exit 1
    fi
fi

# Ask about backend service installation
echo ""
echo "🖥️  Backend Service Installation"
read -p "Install backend service? This enables the API and web UI (y/N): " -r

if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ "$EUID" -ne 0 ]; then
        echo "❌ Backend service installation requires root privileges"
        echo "Run with sudo or use install-backend.sh"
        exit 1
    fi
    
    echo "🔧 Installing backend service..."
    
    # Configure firewall
    if command -v firewall-cmd &> /dev/null; then
        echo "🔥 Configuring firewall..."
        systemctl enable firewalld
        systemctl start firewalld
        firewall-cmd --permanent --add-port=5000/tcp
        firewall-cmd --reload
        echo "✅ Firewall configured (port 5000 open)"
    fi
    
    # Create systemd service
    cat > /etc/systemd/system/labctl-backend.service << EOF
[Unit]
Description=Labctl Backend API Service
After=network.target

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=$SCRIPT_DIR
Environment="PATH=$SCRIPT_DIR/.venv/bin:/usr/local/bin:/usr/bin:/bin"
Environment="FLASK_ENV=production"
ExecStart=$SCRIPT_DIR/.venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 2 app:app
Restart=on-failure
RestartSec=10

# Logging
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

    # Enable and start service
    systemctl daemon-reload
    systemctl enable labctl-backend
    systemctl start labctl-backend
    
    # Wait for service to start
    sleep 3
    
    # Verify service
    if systemctl is-active --quiet labctl-backend; then
        echo "✅ Backend service started successfully!"
        
        # Test API
        if curl -s http://localhost:5000/api/health > /dev/null; then
            echo "✅ API endpoint is responding"
        else
            echo "⚠️  Service started but API not responding"
        fi
        
        # Set environment variable for CLI
        export LABCTL_API_URL="http://localhost:5000"
        
    else
        echo "❌ Failed to start backend service"
        echo "Check logs: journalctl -u labctl-backend -f"
    fi
else
    echo "⏭️  Skipping backend service installation"
    echo "To install later, run install-backend.sh or use systemctl"
fi

echo ""
echo "🎉 Installation complete!"
echo ""
echo "Available commands:"
echo "  - 'labctl' for lab repository management"
echo "  - 'clab-tools' for direct containerlab operations"
echo ""

if [[ $REPLY =~ ^[Yy]$ ]] && systemctl is-active --quiet labctl-backend; then
    echo "✅ All-in-One Mode: Both CLI and backend are running"
    echo ""
    echo "Usage:"
    echo "  labctl repo add <git-url>          # Add a new lab"
    echo "  labctl deploy <lab-id>             # Deploy a lab"
    echo "  labctl status                      # Show active deployments"
    echo ""
    echo "Web UI: http://localhost:5000 (future feature)"
    echo "API: http://localhost:5000/api/"
    echo ""
    echo "Service management:"
    echo "  systemctl status labctl-backend    # Check service status"
    echo "  journalctl -u labctl-backend -f   # View logs"
else
    echo "⚙️  CLI-Only Mode"
    echo ""
    echo "To use with remote backend:"
    echo "  export LABCTL_API_URL=\"http://your-backend-server:5000\""
    echo "  labctl repo list"
    echo ""
    echo "To start local backend manually:"
    echo "  python app.py"
fi

echo ""
echo "For help: labctl --help"
#!/bin/bash
# Frontend/CLI Installation Script for User Workstations
# This installs only the labctl CLI tool (macOS/Linux)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CLI_SCRIPT="$SCRIPT_DIR/labctl"
INSTALL_PATH="/usr/local/bin/labctl"

echo "💻 Installing Homelab Manager CLI..."
echo "This installs the labctl command-line interface."

# Detect OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macOS"
    SHELL_PROFILE="$HOME/.zshrc"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="Linux"
    if [[ -f "$HOME/.bashrc" ]]; then
        SHELL_PROFILE="$HOME/.bashrc"
    elif [[ -f "$HOME/.zshrc" ]]; then
        SHELL_PROFILE="$HOME/.zshrc"
    else
        SHELL_PROFILE="$HOME/.profile"
    fi
else
    echo "❌ Unsupported operating system: $OSTYPE"
    exit 1
fi

echo "📋 Detected OS: $OS"

# Check if the CLI script exists
if [ ! -f "$CLI_SCRIPT" ]; then
    echo "❌ Error: labctl wrapper not found in $SCRIPT_DIR"
    echo "Make sure you've cloned the complete repository"
    exit 1
fi

# Make sure it's executable
chmod +x "$CLI_SCRIPT"

# Install Python dependencies
echo "🐍 Installing Python dependencies..."

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    if [[ "$OS" == "macOS" ]]; then
        echo "Install Python 3 using Homebrew: brew install python"
        echo "Or download from: https://www.python.org/downloads/"
    else
        echo "Install Python 3 using your package manager"
    fi
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$PROJECT_ROOT/.venv" ]; then
    echo "🐍 Creating virtual environment..."
    python3 -m venv "$PROJECT_ROOT/.venv"
fi

# Install CLI dependencies
echo "📦 Installing dependencies..."
"$PROJECT_ROOT/.venv/bin/pip" install --quiet --upgrade pip

# Install from the appropriate requirements file
if [ -f "$PROJECT_ROOT/requirements/requirements-frontend.txt" ]; then
    "$PROJECT_ROOT/.venv/bin/pip" install --quiet -r "$PROJECT_ROOT/requirements/requirements-frontend.txt"
elif [ -f "$PROJECT_ROOT/requirements/frontend.txt" ]; then
    "$PROJECT_ROOT/.venv/bin/pip" install --quiet -r "$PROJECT_ROOT/requirements/frontend.txt"
elif [ -f "$PROJECT_ROOT/requirements.txt" ]; then
    "$PROJECT_ROOT/.venv/bin/pip" install --quiet -r "$PROJECT_ROOT/requirements.txt"
else
    echo "❌ Could not find requirements file"
    exit 1
fi

# Check if clab-tools is installed
if command -v clab-tools &> /dev/null; then
    echo "✅ Found clab-tools installation"
else
    echo "⚠️  Warning: clab-tools not found"
    echo "   labctl requires clab-tools for lab deployments"
    echo "   Please ensure clab-tools is installed and in your PATH"
fi

# Determine installation location
if [ -w "/usr/local/bin" ]; then
    INSTALL_PATH="/usr/local/bin/labctl"
    NEED_SUDO=false
elif [ -d "$HOME/.local/bin" ]; then
    INSTALL_PATH="$HOME/.local/bin/labctl"
    NEED_SUDO=false
    # Create directory if it doesn't exist
    mkdir -p "$HOME/.local/bin"
else
    INSTALL_PATH="/usr/local/bin/labctl"
    NEED_SUDO=true
fi

# Create symlink
echo "🔗 Installing CLI command..."
if [ "$NEED_SUDO" = true ]; then
    echo "📝 Note: sudo required to install to $INSTALL_PATH"
    sudo ln -sf "$CLI_SCRIPT" "$INSTALL_PATH"
else
    ln -sf "$CLI_SCRIPT" "$INSTALL_PATH"
fi

echo "✅ labctl installed to $INSTALL_PATH"

# Check if installation directory is in PATH
if ! echo "$PATH" | grep -q "$(dirname "$INSTALL_PATH")"; then
    echo ""
    echo "⚠️  Warning: $(dirname "$INSTALL_PATH") is not in your PATH"
    echo "Add this line to your shell configuration file (~/.bashrc, ~/.zshrc, etc.):"
    echo "  export PATH=\"$(dirname "$INSTALL_PATH"):\$PATH\""
    echo ""
fi

# Prompt for backend URL
echo ""
echo "🌐 Backend Configuration"
echo "Enter the URL of your lab server's backend API:"
echo "Example: http://lab-server.example.com:5000"
read -p "Backend URL: " BACKEND_URL

if [ -n "$BACKEND_URL" ]; then
    # Add to shell profile
    echo "💾 Configuring shell environment..."
    
    # Remove any existing LABCTL_API_URL lines
    if [ -f "$SHELL_PROFILE" ]; then
        grep -v "LABCTL_API_URL" "$SHELL_PROFILE" > "${SHELL_PROFILE}.tmp" || true
        mv "${SHELL_PROFILE}.tmp" "$SHELL_PROFILE"
    fi
    
    # Add new configuration
    echo "export LABCTL_API_URL=\"$BACKEND_URL\"" >> "$SHELL_PROFILE"
    echo "✅ Backend URL saved to $SHELL_PROFILE"
    
    # Set for current session
    export LABCTL_API_URL="$BACKEND_URL"
fi

# Test installation
echo ""
echo "🧪 Testing installation..."

if command -v labctl &> /dev/null; then
    if [ -n "$BACKEND_URL" ]; then
        echo "Testing connection to backend..."
        if labctl version > /dev/null 2>&1; then
            echo "✅ CLI installation successful and backend is reachable!"
        else
            echo "⚠️  CLI installed but cannot reach backend"
            echo "Make sure the backend is running at: $BACKEND_URL"
        fi
    else
        echo "✅ CLI installed successfully!"
        echo "Set LABCTL_API_URL environment variable to use"
    fi
else
    echo "⚠️  CLI command not found in PATH"
    echo "Try opening a new terminal or run: source $SHELL_PROFILE"
fi

echo ""
echo "🎉 Frontend installation complete!"
echo ""
echo "Usage:"
if [ -n "$BACKEND_URL" ]; then
    echo "  labctl repo list                    # List lab repositories"
    echo "  labctl repo add <git-url>          # Add a new lab"
    echo "  labctl deploy <lab-id>             # Deploy a lab"
    echo "  labctl status                      # Show active deployments"
else
    echo "  export LABCTL_API_URL=\"http://your-lab-server:5000\""
    echo "  labctl repo list                    # List lab repositories"
    echo "  labctl repo add <git-url>          # Add a new lab"
    echo "  labctl deploy <lab-id>             # Deploy a lab"
fi
echo ""
echo "For help: labctl --help"

if [[ "$OS" == "macOS" ]] || [[ "$SHELL_PROFILE" == *"zsh"* ]]; then
    echo ""
    echo "💡 Note: You may need to open a new terminal or run:"
    echo "   source $SHELL_PROFILE"
fi
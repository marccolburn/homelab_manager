#!/bin/bash
# Frontend/CLI Installation Script for User Workstations
# This installs only the labctl CLI tool (macOS/Linux)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLI_SCRIPT="$SCRIPT_DIR/labctl.sh"
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
    echo "❌ Error: labctl.sh not found in $SCRIPT_DIR"
    echo "Make sure you've cloned the complete repository"
    exit 1
fi

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

# Set up virtual environment in user space
VENV_DIR="$HOME/.labctl"
mkdir -p "$VENV_DIR"

if [ ! -f "$VENV_DIR/bin/python" ]; then
    echo "Setting up Python virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Install CLI dependencies
echo "Installing CLI dependencies..."
"$VENV_DIR/bin/pip" install --upgrade pip

# Get the project root
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Install from the appropriate requirements file
if [ -f "$PROJECT_ROOT/requirements/frontend.txt" ]; then
    "$VENV_DIR/bin/pip" install -r "$PROJECT_ROOT/requirements/frontend.txt"
elif [ -f "$PROJECT_ROOT/requirements-frontend.txt" ]; then
    "$VENV_DIR/bin/pip" install -r "$PROJECT_ROOT/requirements-frontend.txt"
else
    echo "❌ Could not find requirements-frontend.txt"
    exit 1
fi

# Copy the CLI module to user space
cp -r "$PROJECT_ROOT/src" "$VENV_DIR/"

# Update the CLI script to use the user's venv
echo "🔧 Configuring CLI script..."
cat > "$HOME/.labctl/labctl.sh" << 'EOF'
#!/bin/bash
# labctl CLI wrapper - calls the Python CLI with the user's virtual environment

VENV_PYTHON="$HOME/.labctl/bin/python"
CLI_DIR="$HOME/.labctl/src"

# Check if virtual environment exists
if [ ! -f "$VENV_PYTHON" ]; then
    echo "Error: Virtual environment not found at $HOME/.labctl"
    echo "Please run the frontend installation script again"
    exit 1
fi

# Check if CLI module exists
if [ ! -d "$CLI_DIR" ]; then
    echo "Error: CLI module not found at $CLI_DIR"
    exit 1
fi

# Execute the CLI with all arguments passed through
exec "$VENV_PYTHON" -m src.cli.main "$@"
EOF

# Make CLI script executable
chmod +x "$HOME/.labctl/labctl.sh"

# Create symlink
echo "🔗 Installing CLI command..."
if [ -w "/usr/local/bin" ]; then
    ln -sf "$HOME/.labctl/labctl.sh" "$INSTALL_PATH"
    echo "✅ CLI installed to $INSTALL_PATH"
else
    echo "📝 Creating CLI symlink (requires sudo)..."
    sudo ln -sf "$HOME/.labctl/labctl.sh" "$INSTALL_PATH"
    if [ $? -eq 0 ]; then
        echo "✅ CLI installed to $INSTALL_PATH"
    else
        echo "⚠️  Could not install to $INSTALL_PATH"
        echo "You can still use the CLI directly: $HOME/.labctl/labctl.sh"
        echo "Or add $HOME/.labctl to your PATH"
    fi
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
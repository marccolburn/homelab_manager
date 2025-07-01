#!/bin/bash
# Setup SSH key authentication for remote deployment host

echo "🔐 Homelab Manager - Remote SSH Setup"
echo "===================================="

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    case $1 in
        "success") echo -e "${GREEN}✅ $2${NC}" ;;
        "error") echo -e "${RED}❌ $2${NC}" ;;
        "warning") echo -e "${YELLOW}⚠️  $2${NC}" ;;
        "info") echo -e "ℹ️  $2" ;;
    esac
}

# Remote host configuration from clab_tools_files/config.yaml
REMOTE_HOST="10.1.91.4"
REMOTE_USER="mcolburn"

echo -e "\n1. Checking for existing SSH key..."
if [ -f "$HOME/.ssh/id_rsa" ] || [ -f "$HOME/.ssh/id_ed25519" ]; then
    print_status "success" "SSH key found"
else
    print_status "warning" "No SSH key found"
    echo -e "\n   Generating new SSH key..."
    ssh-keygen -t ed25519 -f "$HOME/.ssh/id_ed25519" -N "" -C "homelab-manager@$(hostname)"
    print_status "success" "SSH key generated"
fi

echo -e "\n2. Testing current SSH connectivity..."
if ssh -o ConnectTimeout=5 -o BatchMode=yes $REMOTE_USER@$REMOTE_HOST echo "SSH OK" 2>/dev/null; then
    print_status "success" "SSH connection already works (passwordless)"
    echo "   No further setup needed!"
else
    print_status "info" "SSH requires password authentication"
    
    echo -e "\n3. Setting up SSH key authentication..."
    echo "   You will be prompted for the password for $REMOTE_USER@$REMOTE_HOST"
    
    # Copy SSH key to remote host
    if ssh-copy-id -o ConnectTimeout=10 $REMOTE_USER@$REMOTE_HOST; then
        print_status "success" "SSH key copied to remote host"
        
        # Test passwordless connection
        echo -e "\n4. Testing passwordless SSH connection..."
        if ssh -o ConnectTimeout=5 -o BatchMode=yes $REMOTE_USER@$REMOTE_HOST echo "SSH OK" 2>/dev/null; then
            print_status "success" "Passwordless SSH connection confirmed!"
        else
            print_status "error" "SSH still requires password"
            echo "   Please check SSH configuration on remote host"
        fi
    else
        print_status "error" "Failed to copy SSH key"
        echo "   Please ensure:"
        echo "   - Remote host is accessible"
        echo "   - Correct password was entered"
        echo "   - SSH service is running on remote host"
    fi
fi

echo -e "\n5. Checking CLAB_TOOLS_PASSWORD environment variable..."
if [ -n "$CLAB_TOOLS_PASSWORD" ]; then
    print_status "success" "CLAB_TOOLS_PASSWORD is set"
else
    print_status "warning" "CLAB_TOOLS_PASSWORD is not set"
    echo "   This is required for sudo operations on remote host"
    echo -e "\n   Add to your shell profile (~/.bashrc or ~/.zshrc):"
    echo "   export CLAB_TOOLS_PASSWORD='your-sudo-password'"
    echo -e "\n   Or set it temporarily:"
    echo "   export CLAB_TOOLS_PASSWORD='your-sudo-password'"
fi

echo -e "\n6. Testing remote host requirements..."
echo "   Checking if clab-tools is available on remote host..."
if ssh -o ConnectTimeout=5 $REMOTE_USER@$REMOTE_HOST "which clab-tools" 2>/dev/null; then
    print_status "success" "clab-tools found on remote host"
else
    print_status "warning" "clab-tools not found in PATH on remote host"
    echo "   Make sure clab-tools is installed and in PATH"
fi

echo -e "\n✅ SSH setup complete!"
echo -e "\nNext steps:"
echo "1. If CLAB_TOOLS_PASSWORD is not set, set it in your shell"
echo "2. Run the deployment test script: ./scripts/test-deployment.sh"
echo "3. Try deploying via web UI or CLI: labctl deploy topology_jncie_sp_ssb"
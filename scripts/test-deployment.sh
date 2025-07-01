#!/bin/bash
# Test deployment script for Homelab Manager

echo "🧪 Homelab Manager Deployment Test Script"
echo "========================================"

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

# Check if backend is running
check_backend() {
    echo -e "\n1. Checking backend status..."
    if curl -s http://localhost:5001/api/health > /dev/null; then
        print_status "success" "Backend is running at http://localhost:5001"
        return 0
    else
        print_status "error" "Backend is not running"
        echo "   Start it with: ./run-backend.sh"
        return 1
    fi
}

# Check environment variables
check_environment() {
    echo -e "\n2. Checking environment variables..."
    
    if [ -n "$CLAB_TOOLS_PASSWORD" ]; then
        print_status "success" "CLAB_TOOLS_PASSWORD is set"
    else
        print_status "warning" "CLAB_TOOLS_PASSWORD is not set (required for remote deployments)"
        echo "   Set it with: export CLAB_TOOLS_PASSWORD='your-password'"
    fi
    
    if [ -n "$PYTHONPATH" ]; then
        print_status "success" "PYTHONPATH is set: $PYTHONPATH"
    else
        print_status "warning" "PYTHONPATH is not set"
    fi
}

# Test local deployment
test_local_deployment() {
    echo -e "\n3. Testing local deployment (without remote host)..."
    
    # Create a temporary local config
    LAB_DIR="$HOME/.labctl/repos/topology_jncie_sp_ssb"
    if [ ! -d "$LAB_DIR" ]; then
        print_status "error" "Lab repository not found at $LAB_DIR"
        return 1
    fi
    
    # Backup original config
    if [ -f "$LAB_DIR/clab_tools_files/config.yaml" ]; then
        cp "$LAB_DIR/clab_tools_files/config.yaml" "$LAB_DIR/clab_tools_files/config.yaml.bak"
        print_status "info" "Backed up original config.yaml"
    fi
    
    # Create local test config
    cat > "$LAB_DIR/clab_tools_files/config.local.yaml" << EOF
# Local test configuration (no remote host)
database:
  echo: false

logging:
  level: "INFO"
  format: "console"
  file_path: "./clab_tools_files/test_deployment.log"

topology:
  default_topology_name: "jncie_sp_ssb"
  default_prefix: "sp_ssb"
  default_mgmt_network: "mgmtclab"
  default_mgmt_subnet: "10.100.100.0/24"
  output_dir: "./test_outputs"

bridges:
  bridge_prefix: "br-"
  cleanup_on_exit: true

debug: true

lab:
  current_lab: "jncie_sp_ssb"
  auto_create_lab: true
  use_global_database: false

# Remote disabled for local testing
remote:
  enabled: false

node:
  default_username: admin
  default_password: admin@123
  ssh_port: 22
  connection_timeout: 30
EOF
    
    print_status "success" "Created local test configuration"
    
    # Try deployment via API
    echo -e "\n   Attempting deployment via API..."
    RESPONSE=$(curl -s -X POST http://localhost:5001/api/labs/topology_jncie_sp_ssb/deploy \
        -H "Content-Type: application/json" \
        -d '{"version": "latest", "allocate_ips": false}')
    
    if echo "$RESPONSE" | grep -q "task_id"; then
        TASK_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('task_id', ''))")
        print_status "success" "Deployment started with task ID: $TASK_ID"
        
        # Monitor task
        echo "   Monitoring deployment progress..."
        for i in {1..10}; do
            sleep 2
            TASK_STATUS=$(curl -s "http://localhost:5001/api/tasks/$TASK_ID" | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', 'unknown'))" 2>/dev/null)
            echo "   Task status: $TASK_STATUS"
            if [ "$TASK_STATUS" = "completed" ]; then
                break
            fi
        done
    else
        print_status "error" "Failed to start deployment"
        echo "   Response: $RESPONSE"
    fi
}

# Test remote deployment configuration
test_remote_config() {
    echo -e "\n4. Testing remote deployment configuration..."
    
    # Check SSH connectivity
    print_status "info" "Checking SSH connectivity to 10.1.91.4..."
    if ssh -o ConnectTimeout=5 -o BatchMode=yes mcolburn@10.1.91.4 echo "SSH OK" 2>/dev/null; then
        print_status "success" "SSH connection successful (passwordless)"
    else
        print_status "warning" "SSH connection failed or requires password"
        echo "   Run: ssh-copy-id mcolburn@10.1.91.4"
    fi
}

# Check NetBox configuration
check_netbox() {
    echo -e "\n5. Checking NetBox configuration..."
    
    CONFIG_FILE="$HOME/.labctl/config.yaml"
    if [ -f "$CONFIG_FILE" ]; then
        NETBOX_ENABLED=$(grep -A1 "netbox:" "$CONFIG_FILE" | grep "enabled:" | awk '{print $2}')
        if [ "$NETBOX_ENABLED" = "true" ]; then
            print_status "success" "NetBox is enabled in backend config"
            NETBOX_URL=$(grep -A3 "netbox:" "$CONFIG_FILE" | grep "url:" | awk '{print $2}')
            echo "   URL: $NETBOX_URL"
        else
            print_status "warning" "NetBox is disabled in backend config"
            echo "   To enable, edit $CONFIG_FILE and set netbox.enabled: true"
        fi
    fi
}

# Main execution
main() {
    check_backend || exit 1
    check_environment
    check_netbox
    
    echo -e "\n${YELLOW}Choose deployment type:${NC}"
    echo "1. Test LOCAL deployment (recommended for testing)"
    echo "2. Test REMOTE deployment configuration"
    echo "3. Exit"
    
    read -p "Enter choice (1-3): " choice
    
    case $choice in
        1) test_local_deployment ;;
        2) test_remote_config ;;
        3) echo "Exiting..." ;;
        *) print_status "error" "Invalid choice" ;;
    esac
    
    echo -e "\n✅ Test complete!"
}

# Run main function
main
# Homelab Manager - Quick Start Guide

Get up and running with Homelab Manager in 5 minutes! This guide covers the most common setup scenarios.

## Prerequisites

Before starting, ensure you have:
- Python 3.8 or higher
- Git
- clab-tools installed (for lab deployments)
- A Linux/macOS system (RHEL/Fedora recommended for backend)

## Installation Options

### Option 1: All-in-One Installation (Recommended for Testing)

Perfect for getting started quickly on a single machine:

```bash
# Clone the repository
git clone https://github.com/your-org/homelab-manager.git
cd homelab-manager

# Run the all-in-one installer
./scripts/install-labctl.sh
```

This installs both the CLI and backend service on the same machine.

### Option 2: Separate Backend and CLI (Recommended for Production)

**On your lab server (RHEL/Fedora):**
```bash
# Clone and install backend
git clone https://github.com/your-org/homelab-manager.git
cd homelab-manager
sudo ./scripts/install-backend.sh
```

**On your workstation:**
```bash
# Clone and install CLI only
git clone https://github.com/your-org/homelab-manager.git
cd homelab-manager
./scripts/install-frontend.sh

# When prompted, enter your backend URL:
# http://your-lab-server:5000
```

## First Steps

### 1. Verify Installation

```bash
# Check CLI is working
labctl --help

# Check backend connection (if using remote backend)
labctl version
```

### 2. Add Your First Lab

```bash
# Add a lab repository
labctl repo add https://github.com/example/my-lab.git

# List available labs
labctl repo list
```

### 3. Deploy a Lab

```bash
# Deploy the latest version
labctl deploy my-lab

# Deploy a specific version
labctl deploy my-lab v1.0.0

# Check deployment status
labctl status
```

### 4. Manage Lab Configurations

```bash
# List available configuration scenarios
labctl config list my-lab

# Apply a configuration scenario
labctl config apply my-lab baseline

# View deployment logs
labctl logs my-lab
```

### 5. Clean Up

```bash
# Destroy a deployed lab
labctl destroy my-lab

# Remove a lab repository
labctl repo remove my-lab
```

## Common Workflows

### Updating Labs

Pull the latest changes from a lab repository:

```bash
labctl repo update my-lab
```

### Working with Versions

Labs use Git tags for versioning:

```bash
# Deploy a specific tagged version
labctl deploy my-lab v2.1.0

# Deploy from a specific branch
labctl deploy my-lab --branch develop
```

### Configuration Scenarios

Apply different configurations to your deployed lab:

```bash
# Start with baseline configuration
labctl config apply my-lab baseline

# Switch to advanced scenario
labctl config apply my-lab advanced-bgp

# Reset to defaults
labctl config apply my-lab reset
```

## Environment Variables

### Backend Connection
```bash
# Set backend URL (if not using local backend)
export LABCTL_API_URL="http://lab-server:5000"
```

### Custom Lab Repository Path
```bash
# Change where labs are cloned (default: ~/lab_repos)
export LAB_REPOS_PATH="/opt/labs"
```

## Troubleshooting

### CLI Can't Connect to Backend

1. Check backend is running:
   ```bash
   systemctl status labctl-backend
   ```

2. Verify backend URL:
   ```bash
   echo $LABCTL_API_URL
   curl $LABCTL_API_URL/api/health
   ```

3. Check firewall settings:
   ```bash
   sudo firewall-cmd --list-ports
   ```

### Lab Deployment Fails

1. Check clab-tools is installed:
   ```bash
   which clab-tools
   ```

2. Verify lab repository structure:
   ```bash
   ls -la ~/lab_repos/my-lab/clab_tools_files/
   ```

3. Check deployment logs:
   ```bash
   labctl logs my-lab
   ```

### Permission Issues

If you get permission errors:

```bash
# For backend service
sudo systemctl restart labctl-backend
sudo journalctl -u labctl-backend -f

# For lab deployments
sudo chown -R $USER:$USER ~/lab_repos
```

## Next Steps

- Read the [CLI Command Reference](commands.md) for detailed command usage
- Learn about [Lab Repository Structure](../CLAUDE.md#lab-repository-standard)
- Configure [NetBox Integration](configuration.md#netbox-integration) for dynamic IP management
- Explore [API Documentation](api.md) for automation

## Getting Help

- Run `labctl --help` for command help
- Check logs: `journalctl -u labctl-backend -f`
- Visit project documentation: `docs/`
- Report issues: https://github.com/your-org/homelab-manager/issues
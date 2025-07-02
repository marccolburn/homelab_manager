# Configuration Guide

Complete guide to configuring Homelab Manager settings, including all available options and their defaults.

## Configuration Files

### Backend Configuration: `~/.labctl/config.yaml`

This is the main configuration file used by the backend. It's created automatically with defaults on first run.

**Location**: `~/.labctl/config.yaml`
**Format**: YAML
**Access**: Editable via Web UI Settings page or direct file editing

## Configuration Sections

### Basic Settings

```yaml
# Default configuration
repos_dir: "/Users/username/.labctl/repos"       # Where lab repositories are stored
logs_dir: "/Users/username/.labctl/logs"         # Where deployment logs are stored
state_file: "/Users/username/.labctl/state.json" # Application state file
clab_tools_cmd: "clab-tools"                     # clab-tools command path
git_cmd: "git"                                   # Git command path
```

### Remote Credentials

Configure passwords for remote lab host operations:

```yaml
clab_tools_password: ""                          # Password for clab-tools operations
remote_credentials:
  ssh_password: ""                               # SSH password for remote host
  sudo_password: ""                              # Sudo password for remote host
```

**Setting via Web UI**: 
- Go to `http://localhost:5001/settings.html`
- Configure in "Remote Credentials" section
- Passwords are stored encrypted and masked in the UI

**Environment Variable Override**:
```bash
export CLAB_TOOLS_PASSWORD="your-password"
export CLAB_REMOTE_PASSWORD="ssh-password"  
export CLAB_REMOTE_SUDO_PASSWORD="sudo-password"
```

### NetBox Integration

Configure NetBox for dynamic IP allocation:

```yaml
netbox:
  enabled: false                                 # Enable NetBox integration
  url: ""                                        # NetBox instance URL
  token: ""                                      # NetBox API token
  default_prefix: "10.100.100.0/24"            # Default IP prefix for labs
  default_site: "Lab Environment"               # Default site name
  default_role: "Lab Device"                    # Default device role
  cleanup_on_destroy: true                      # Release IPs when lab destroyed
```

**Setting via Web UI**:
- Go to Settings page → "NetBox Integration" section
- Toggle "Enable NetBox Integration"
- Configure URL, token, and prefix
- Use "Test Connection" to verify

**NetBox Requirements**:
- NetBox 3.0+ with API access
- API token with IP and device management permissions
- Configured prefix for lab management networks
- Site and device role must exist in NetBox

### Monitoring

Configure monitoring system URLs:

```yaml
monitoring:
  prometheus: "http://localhost:9090"           # Prometheus URL
  grafana: "http://localhost:3000"             # Grafana URL
```

**Setting via Web UI**:
- Go to Settings page → "Monitoring" section
- Configure Prometheus and Grafana URLs

## Lab Repository Configuration

Each lab repository contains its own configuration in `clab_tools_files/config.yaml`:

### Basic Lab Config

```yaml
# Lab-specific clab-tools configuration
topology:
  default_topology_name: "my-lab"
  default_mgmt_subnet: "10.100.100.0/24"
```

### Remote Deployment Config

```yaml
# Remote host configuration for clab-tools
remote:
  enabled: true
  host: "10.1.91.4"                            # Remote lab host IP
  user: "username"                             # SSH username
  topology_remote_dir: "/home/username/labs"   # Remote storage directory
  # Passwords come from backend configuration or environment variables
```

### Lab Metadata: `lab-metadata.yaml`

```yaml
# Lab discovery and management metadata
name: "BGP Advanced Features Lab"
id: "bgp-advanced"
version: "1.0.0"
category: "Routing"
vendor: "Juniper"
difficulty: "Intermediate"
description:
  short: "BGP communities, route reflection, and policies"
  long: |
    Detailed description of the lab...
requirements:
  memory_gb: 32
  cpu_cores: 16
  disk_gb: 40
  containerlab_version: ">=0.48.0"
platform: "containerlab"
netbox:
  enabled: true
  prefix: "10.100.100.0/24"
  site: "Lab Environment"
  role: "Lab Device"
tags:
  - bgp
  - routing
  - juniper
repository:
  url: "git@github.com:user/bgp-advanced-lab.git"
  branch: "main"
```

## Configuration Methods

### 1. Web UI Settings (Recommended)

**Access**: `http://localhost:5001/settings.html`

**Features**:
- Secure password input with masking
- Real-time validation
- Connection testing
- Form validation and error handling

**Sections**:
- Remote Credentials: SSH/sudo passwords
- NetBox Integration: URL, token, settings
- Monitoring: Prometheus/Grafana URLs

### 2. Direct File Editing

Edit `~/.labctl/config.yaml` directly:

```bash
# Open configuration file
nano ~/.labctl/config.yaml

# Restart backend to apply changes
./scripts/run-backend.sh
```

### 3. Environment Variables

Override configuration with environment variables:

```bash
# Remote credentials
export CLAB_TOOLS_PASSWORD="password"
export CLAB_REMOTE_PASSWORD="ssh-password"
export CLAB_REMOTE_SUDO_PASSWORD="sudo-password"

# NetBox settings
export NETBOX_URL="http://netbox.example.com"
export NETBOX_TOKEN="api-token"

# Start backend with environment overrides
./scripts/run-backend.sh
```

## Security Considerations

### Password Storage

- Passwords stored in `~/.labctl/config.yaml` are **not encrypted**
- File permissions should be `600` (user read/write only)
- Web UI masks passwords but stores them in plain text
- Environment variables are preferred for CI/CD environments

### File Permissions

```bash
# Secure configuration file
chmod 600 ~/.labctl/config.yaml

# Secure log directory
chmod 750 ~/.labctl/logs/
```

### Network Security

- Development: HTTP on localhost only
- Production: Use HTTPS with proper certificates
- Firewall: Restrict backend port (5001) to trusted networks

## Configuration Validation

### Test Configuration

```bash
# Via CLI
labctl doctor

# Via Web UI
# Go to Settings → "Test Connection"

# Check backend health
curl http://localhost:5001/api/health
```

### Validate NetBox

```bash
# Via CLI
labctl netbox

# Via API
curl http://localhost:5001/api/netbox/validate
```

### Debug Configuration

```bash
# View current configuration (passwords masked)
curl http://localhost:5001/api/config/settings

# Check system paths and commands
curl http://localhost:5001/api/config
```

## Common Configuration Issues

### 1. Remote Connection Failures

**Symptoms**: Deployments fail immediately
**Solutions**:
- Verify SSH access: `ssh user@remote-host`
- Check credentials in Settings page
- Ensure `clab-tools` installed on remote host
- Verify network connectivity

### 2. NetBox Integration Failures

**Symptoms**: IP allocation fails
**Solutions**:
- Test NetBox connectivity in Settings
- Verify API token permissions
- Check prefix exists in NetBox
- Ensure site and role are configured

### 3. Permission Issues

**Symptoms**: Configuration changes don't persist
**Solutions**:
- Check file permissions: `ls -la ~/.labctl/config.yaml`
- Ensure directory is writable: `ls -ld ~/.labctl/`
- Run with proper user permissions

### 4. Port Conflicts

**Symptoms**: Backend won't start
**Solutions**:
- Check port usage: `lsof -i :5001`
- Change port: `PORT=5002 ./scripts/run-backend.sh`
- Kill conflicting process

## Configuration Examples

### Minimal Configuration

```yaml
# ~/.labctl/config.yaml - Minimal working config
repos_dir: "/Users/username/.labctl/repos"
logs_dir: "/Users/username/.labctl/logs"
state_file: "/Users/username/.labctl/state.json"
clab_tools_cmd: "clab-tools"
git_cmd: "git"
```

### Full Configuration

```yaml
# ~/.labctl/config.yaml - Complete configuration
repos_dir: "/Users/username/.labctl/repos"
logs_dir: "/Users/username/.labctl/logs"
state_file: "/Users/username/.labctl/state.json"
clab_tools_cmd: "clab-tools"
git_cmd: "git"
clab_tools_password: "secure-password"
remote_credentials:
  ssh_password: "ssh-password"
  sudo_password: "sudo-password"
monitoring:
  prometheus: "http://monitoring.example.com:9090"
  grafana: "http://monitoring.example.com:3000"
netbox:
  enabled: true
  url: "http://netbox.example.com"
  token: "netbox-api-token"
  default_prefix: "10.100.100.0/24"
  default_site: "Lab Environment"
  default_role: "Lab Device"
  cleanup_on_destroy: true
```

### Development Configuration

```yaml
# ~/.labctl/config.yaml - Development setup
repos_dir: "/tmp/labctl-dev/repos"
logs_dir: "/tmp/labctl-dev/logs"
state_file: "/tmp/labctl-dev/state.json"
clab_tools_cmd: "clab-tools"
git_cmd: "git"
netbox:
  enabled: false
monitoring:
  prometheus: "http://localhost:9090"
  grafana: "http://localhost:3000"
```

## Configuration Migration

### From Old Versions

If upgrading from an older version:

1. Backup existing configuration
2. Check for new configuration options
3. Update configuration file structure
4. Test configuration with `labctl doctor`

### Configuration Backup

```bash
# Backup configuration
cp ~/.labctl/config.yaml ~/.labctl/config.yaml.backup

# Restore configuration
cp ~/.labctl/config.yaml.backup ~/.labctl/config.yaml
```
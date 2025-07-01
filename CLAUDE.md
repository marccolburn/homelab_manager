T# Homelab Manager - Development Guide

## Project Overview

This is a lab management system that acts as a wrapper around `clab-tools`, providing:
- Git-based lab repository management
- Version control via Git tags
- Simple CLI interface (`labctl`)
- Optional lightweight web UI
- Integration with existing `clab-tools` workflows
- NetBox integration for dynamic IP management
- Extensible architecture for future virtualization platforms

## Architecture

### Key Design Principles

1. **API-First Design**: Flask backend provides RESTful API for all operations
2. **Separation of Concerns**: CLI and Web UI are lightweight clients that call the API
3. **Leverage clab-tools**: Backend directly calls `clab-tools` for all containerlab operations
4. **Git-Native**: Each lab is a Git repository with standardized structure
5. **Extensible**: Designed to support multiple virtualization platforms (KVM, VMware, etc.)

### System Components (Phase 2 Reorganization Completed)

```
homelab-manager/
├── src/                       # Source code (NEW STRUCTURE)
│   ├── backend/              # Flask backend modules
│   │   ├── __init__.py
│   │   ├── app.py           # Main Flask application
│   │   ├── api/             # API route handlers
│   │   │   ├── __init__.py
│   │   │   ├── repos.py     # Repository management endpoints
│   │   │   ├── labs.py      # Lab deployment endpoints
│   │   │   ├── tasks.py     # Async task endpoints
│   │   │   └── health.py    # Health check endpoints
│   │   ├── core/            # Core business logic
│   │   │   ├── __init__.py
│   │   │   ├── lab_manager.py    # Lab management class
│   │   │   ├── git_ops.py        # Git operations
│   │   │   ├── clab_runner.py    # clab-tools integration
│   │   │   └── config.py         # Configuration management
│   │   ├── integrations/    # External integrations
│   │   │   ├── __init__.py
│   │   │   ├── netbox.py    # NetBox IP management (future)
│   │   │   └── monitoring.py # Prometheus/Grafana (future)
│   │   └── utils/           # Utilities
│   │       ├── __init__.py
│   │       ├── validators.py # Input validation
│   │       └── helpers.py    # Common helpers
│   ├── cli/                 # CLI client modules
│   │   ├── __init__.py
│   │   ├── main.py          # CLI entry point
│   │   ├── client.py        # API client
│   │   ├── commands/        # Command implementations
│   │   │   ├── __init__.py
│   │   │   ├── repo.py      # Repository commands
│   │   │   ├── lab.py       # Lab commands
│   │   │   ├── device_config.py  # Device config scenarios
│   │   │   └── system.py    # System/server commands
│   │   └── utils/           # CLI utilities
│   │       ├── __init__.py
│   │       ├── console.py   # Rich console helpers
│   │       └── validators.py # Input validation
│   └── web/                 # Future web UI
│       ├── static/
│       └── templates/
├── scripts/                  # Installation scripts
│   ├── install-backend.sh    # Backend installation
│   ├── install-frontend.sh   # CLI-only installation
│   └── install-labctl.sh     # All-in-one installation
├── config/                   # Configuration templates
│   ├── systemd/
│   │   └── labctl-backend.service
│   ├── nginx/
│   └── prometheus/
├── requirements/             # Dependency files
│   ├── backend.txt          # Backend dependencies
│   ├── frontend.txt         # CLI dependencies
│   └── all.txt              # Combined dependencies
├── tests/                    # Comprehensive test suite
│   ├── unit/                # Unit tests (26 tests)
│   ├── integration/         # Integration tests (23 tests)
│   ├── e2e/                 # End-to-end tests (4 tests)
│   └── run_tests.py         # Test runner
└── run-backend.sh           # Development helper script
```

### Phase 2 Reorganization Status - 🚧 EXTENDED

✅ **Core Reorganization Completed:**
1. Extracted LabManager class to `src/backend/core/lab_manager.py`
2. Created Git operations module in `src/backend/core/git_ops.py`
3. Created clab-tools runner module in `src/backend/core/clab_runner.py`
4. Split Flask API routes into separate modules in `src/backend/api/`
5. Moved main Flask app to `src/backend/app.py`
6. Extracted CLI commands into separate modules in `src/cli/commands/`
7. Created API client module in `src/cli/client.py`
8. Moved labctl.py functionality to `src/cli/main.py`
9. Updated all installation scripts for new directory structure
10. Updated systemd service file for new app.py location
11. **Comprehensive testing completed** - 53/53 tests passing
12. **Legacy files cleaned up** - Removed old app.py, labctl.py, lab_manager.py

📋 **Phase 2 Extended Tasks:**

**Priority 1 (High):**
- [ ] **Create labctl wrapper script** - User-friendly installation with PATH symlink
- [ ] **docs/quickstart.md** - Getting started guide  
- [ ] **docs/installation.md** - Installation guide

**Priority 2 (Medium):**
- [ ] **Convert to pytest** - Modernize test framework from unittest
- [ ] **docs/configuration.md** - Configuration guide
- [ ] **docs/commands.md** - CLI command reference
- [ ] **docs/api.md** - REST API documentation
- [ ] **docs/development.md** - Development workflow and architecture

**Extended Phase 2 Goals:**
- Improve user experience with simplified CLI installation
- Modernize testing infrastructure for better maintainability  
- Provide comprehensive documentation for all user types
- Enable easier onboarding for new developers and users

### ✅ **Phase 2 Test Results:**
- **Unit Tests**: 26/26 PASSED ✅ (lab_manager, git_ops, clab_runner)
- **Integration Tests**: 23/23 PASSED ✅ (API endpoints, CLI commands, module integration)  
- **End-to-End Tests**: 4/4 PASSED ✅ (complete workflows)
- **Total Coverage**: 53/53 tests passing

### ✅ **Test Infrastructure Created:**
- Comprehensive unit test suite with proper mocking
- Integration tests for Flask API and CLI client
- End-to-end workflow validation
- Flask application context handling
- Automated test runner with coverage reporting

### ✅ **Phase 3: NetBox Integration - COMPLETED**

**NetBox Integration Status:**
- ✅ **NetBox Module Created**: Complete `src/backend/integrations/netbox.py`
- ✅ **IP Allocation**: Dynamic IP allocation from NetBox prefixes
- ✅ **Device Registration**: Automatic device registration in NetBox
- ✅ **CSV Updates**: nodes.csv updated with allocated management IPs
- ✅ **Configuration Validation**: NetBox connectivity and configuration checks
- ✅ **Error Handling**: Proper rollback on allocation failures
- ✅ **API Endpoints**: `/api/netbox/validate` and deploy with `allocate_ips`
- ✅ **CLI Commands**: `labctl netbox` and `labctl deploy --allocate-ips`

**Phase 3 Test Results:**
- **Unit Tests**: 42/42 PASSED ✅ (26 existing + 16 NetBox)
- **Integration Tests**: 45/45 PASSED ✅ (23 existing + 22 NetBox) 
- **End-to-End Tests**: 7/7 PASSED ✅ (4 existing + 3 NetBox)
- **Total Coverage**: 94/94 tests passing

**NetBox Features Implemented:**
- Dynamic IP allocation from configurable prefixes
- Device registration with lab metadata and tags
- Automatic cleanup on lab destruction
- Configuration validation and error reporting
- Integration with existing deployment workflow
- Support for disabled NetBox (graceful degradation)

**Phase 4 Ready to Start:**
- Web UI Development
- Enhanced monitoring integration
- CI/CD pipeline implementation

### Key Module Responsibilities

**Backend Core Modules:**
- `lab_manager.py`: Orchestrates lab operations, state management
- `git_ops.py`: All Git operations (clone, pull, checkout, etc.)
- `clab_runner.py`: Executes bootstrap.sh/teardown.sh, interacts with clab-tools
- `config.py`: Configuration loading and management

**API Modules:**
- `repos.py`: `/api/repos` endpoints for repository management
- `labs.py`: `/api/labs` endpoints for deployment and management
- `tasks.py`: `/api/tasks` endpoints for async operation tracking
- `health.py`: `/api/health` and `/api/config` endpoints

**CLI Modules:**
- `client.py`: HTTP client for API communication
- `commands/repo.py`: `labctl repo` subcommands
- `commands/lab.py`: `labctl deploy/destroy/status/logs` commands
- `commands/device_config.py`: `labctl config` for device scenarios
- `commands/system.py`: `labctl doctor/version` commands

## Lab Repository Standard

### Required Structure
```
my-lab/
├── lab-metadata.yaml         # Lab discovery metadata
├── clab_tools_files/         # clab-tools configuration
│   ├── config.yaml          # clab-tools config (DO NOT CHANGE)
│   ├── nodes.csv            # Node definitions for clab-tools
│   ├── connections.csv      # Topology connections for clab-tools
│   ├── bootstrap.sh         # Lab deployment script
│   └── teardown.sh          # Lab cleanup script
├── device_configs/          # Device configurations
│   ├── baseline/            # Default configs
│   ├── scenario-1/          # Scenario configs
│   └── README.md            # Scenario descriptions
├── ansible/                 # Future: Ansible playbooks for VMs
│   ├── inventory.yml       
│   └── deploy.yml
├── tests/                   # Validation scripts (optional)
└── README.md                # Lab documentation
```

### lab-metadata.yaml Format
```yaml
# Metadata for lab discovery and management
name: "BGP Advanced Features Lab"
id: "bgp-advanced"
version: "1.0.0"
category: "Routing"
vendor: "Juniper"
difficulty: "Intermediate"
description:
  short: "BGP communities, route reflection, and policies"
  long: |
    This lab explores advanced BGP features including:
    - Community manipulation
    - Route reflection design
    - Complex routing policies
requirements:
  memory_gb: 32
  cpu_cores: 16
  disk_gb: 40
  containerlab_version: ">=0.48.0"
  
# Platform specification (future enhancement)
platform: "containerlab"  # or "kvm", "vmware", etc.

# NetBox integration for dynamic IP allocation
netbox:
  enabled: true
  prefix: "10.100.100.0/24"  # Lab management network
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

## CLI Tool (labctl)

### Core Commands
```bash
# Lab Repository Management
labctl repo add <git-url>              # Clone and register a lab
labctl repo update [lab-id]            # Pull latest changes
labctl repo list                       # List all registered labs
labctl repo remove <lab-id>            # Remove lab registration

# Lab Deployment (wraps clab-tools)
labctl deploy <lab-id> [version]       # Deploy specific version/tag
  --allocate-ips                       # Dynamically allocate IPs from NetBox
labctl destroy <lab-id>                # Teardown active lab
labctl status                          # Show deployed labs
labctl logs <lab-id>                   # Show deployment logs

# Configuration Management
labctl config list <lab-id>            # List available scenarios
labctl config apply <lab-id> <scenario> # Apply configuration scenario

# NetBox Integration
labctl netbox                          # Validate NetBox configuration and connectivity

# Utility Commands
labctl version                         # Show version info
labctl doctor                          # Check system requirements
```

### Implementation Details

**Flask Backend API (`app.py`):**
- Contains all business logic for lab management
- Manages Git repositories (clone, fetch, checkout tags)
- Reads lab-metadata.yaml for lab information
- Optionally allocates IPs from NetBox before deployment
- Updates nodes.csv with allocated IPs (if enabled)
- Executes bootstrap.sh/teardown.sh scripts
- These scripts call `clab-tools lab bootstrap/teardown` with the appropriate files
- Provides REST API endpoints for all operations
- Handles async operations with task tracking

**CLI Client (`labctl.py`):**
- Lightweight HTTP client that calls Flask API
- Rich console interface with progress bars and tables
- No business logic - pure API client
- Can be used for scripting and automation

**Communication Flow:**
1. CLI makes HTTP request to Flask API
2. Flask API performs Git/clab-tools operations
3. API returns JSON response to CLI
4. CLI displays formatted output to user

Example bootstrap.sh (unchanged - called by Flask backend):
```bash
#!/bin/bash
# This script is called by Flask backend and uses clab-tools

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# If nodes.csv was updated with dynamic IPs, it's already done by backend
# Just proceed with normal clab-tools bootstrap

# Use clab-tools to bootstrap the lab
clab-tools --config config.yaml --enable-remote lab bootstrap \
    --nodes nodes.csv \
    --connections connections.csv \
    --output "../${LAB_ID}.clab.yml"
```

## Web UI

### Single-Page Application (Future)
The web UI will be a simple HTML/CSS/JavaScript application that calls the same Flask API endpoints as the CLI. This ensures consistency and reduces code duplication.

**Features:**
- Lab repository browsing and management
- One-click lab deployment
- Real-time deployment status
- Configuration scenario management
- Deployment logs viewer
- Resource usage monitoring (via Prometheus/Grafana integration)

**Architecture:**
- Static files served by Flask backend (`app.py`)
- JavaScript makes AJAX calls to API endpoints
- No server-side rendering - pure client-side
- Server-Sent Events for real-time deployment updates

**Example API Usage:**
```javascript
// Deploy a lab
async function deployLab(labId, version = 'latest') {
    const response = await fetch(`/api/labs/${labId}/deploy`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({version, allocate_ips: false})
    });
    
    const result = await response.json();
    return result.task_id;
}

// Check deployment status
async function checkStatus(taskId) {
    const response = await fetch(`/api/tasks/${taskId}`);
    return await response.json();
}

// List available labs
async function listLabs() {
    const response = await fetch('/api/repos');
    return await response.json();
}
```

## Monitoring Integration

### Flexible Monitoring Setup

The monitoring stack supports both local and remote lab hosts:

```yaml
# monitoring/docker-compose.yml
version: '3'
services:
  # Only needed on the lab host
  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    ports:
      - "8080:8080"
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
      
  # Can run anywhere - scrapes from lab host
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - ./prometheus-remote.yml:/etc/prometheus/prometheus-remote.yml
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

### Remote Host Monitoring
```yaml
# monitoring/prometheus-remote.yml
global:
  scrape_interval: 15s

scrape_configs:
  # Scrape cAdvisor on remote lab host
  - job_name: 'cadvisor-remote'
    static_configs:
      - targets: ['lab-host.example.com:8080']
        labels:
          host: 'lab-host'
          
  # Scrape node exporter if available
  - job_name: 'node-exporter-remote'
    static_configs:
      - targets: ['lab-host.example.com:9100']
        labels:
          host: 'lab-host'
```

### Pre-built Dashboards
- Import containerlab dashboard: https://grafana.com/grafana/dashboards/15623
- Container metrics from cAdvisor
- Host metrics from node_exporter
- Custom lab status metrics

## NetBox Integration

### Dynamic IP Allocation

When `--allocate-ips` is used with `labctl deploy`:

1. Query NetBox for available IPs in the configured prefix
2. Allocate IPs for each node in the topology
3. Update nodes.csv with allocated IPs
4. Register devices in NetBox with allocated IPs
5. On teardown, release IPs back to the pool

### Configuration
```yaml
# config.yaml
netbox:
  url: "https://netbox.example.com"
  token: "your-api-token"
  default_prefix: "10.100.100.0/24"
  default_site: "Lab Environment"
  default_role: "Lab Device"
  cleanup_on_destroy: true  # Release IPs on lab teardown
```

## Workflow Examples

### Adding a New Lab
```bash
# 1. Create lab repository with standard structure
# 2. Ensure clab_tools_files/ contains proper files
# 3. Add lab-metadata.yaml
# 4. Push to Git with version tag

# Register the lab
labctl repo add git@github.com:user/my-new-lab.git

# Deploy specific version with dynamic IPs
labctl deploy my-new-lab v1.0.0 --allocate-ips
```

### Daily Usage
```bash
# List available labs
labctl repo list

# Deploy latest version of a lab
labctl deploy bgp-advanced

# Check status
labctl status

# Apply different configuration scenario
labctl config apply bgp-advanced mpls-scenario

# Destroy when done (releases IPs if allocated)
labctl destroy bgp-advanced
```

## Best Practices

1. **Don't Modify clab-tools Files**
   - Keep config.yaml as-is
   - Use standard nodes.csv/connections.csv format
   - Let clab-tools handle the heavy lifting

2. **Version Control**
   - Tag stable releases (v1.0.0, v1.1.0)
   - Use semantic versioning
   - Document changes in release notes

3. **Lab Design**
   - One learning objective per lab
   - Provide multiple configuration scenarios
   - Include reset/baseline configurations

4. **Documentation**
   - Clear README in each lab
   - Scenario descriptions
   - Resource requirements in metadata

5. **IP Management**
   - Use static IPs for stable labs
   - Use dynamic allocation for temporary deployments
   - Document IP requirements clearly

## Integration Points

### With clab-tools
- `labctl` calls bootstrap.sh/teardown.sh
- Scripts use `clab-tools lab bootstrap/teardown`
- All containerlab operations via clab-tools

### With Remote Hosts
- clab-tools handles remote deployment
- config.yaml contains remote settings
- Monitoring can scrape metrics remotely

### With Git
- Standard Git commands for repository management
- Native tag support for versions
- No special Git library needed

### With NetBox
- pynetbox for API interactions
- Dynamic IP allocation/deallocation from configured prefixes
- Automatic device registration with lab metadata
- Configuration validation and error reporting
- Support for disabled NetBox integration

### NetBox Configuration
Configure NetBox integration in your backend configuration:

```yaml
# Backend configuration
netbox:
  enabled: true
  url: "https://netbox.example.com"
  token: "your-api-token"
  default_prefix: "10.100.100.0/24"
  default_site: "Lab Environment"
  default_role: "Lab Device"
  cleanup_on_destroy: true  # Release IPs on lab teardown
```

**NetBox Setup Requirements:**
1. NetBox instance with API access
2. API token with IP and device management permissions
3. Configured prefix for lab management networks
4. Site and device role for lab devices

**Usage:**
```bash
# Validate NetBox configuration
labctl netbox

# Deploy with dynamic IP allocation
labctl deploy my-lab --allocate-ips

# Check NetBox integration status
labctl doctor
```

## Configuration Management

### Configuration Files

The Homelab Manager uses multiple configuration files for different purposes:

1. **Backend Configuration**: `~/.labctl/config.yaml`
   - Loaded by `src/backend/core/config.py`
   - Contains runtime settings for the backend
   - Created automatically with defaults if not present
   - Includes: repos_dir, logs_dir, state_file, NetBox settings

2. **Lab Repository Config**: `lab_manager_config.yaml` (in project root)
   - Reference configuration (not actively used by backend)
   - Shows example remote host and NetBox configurations
   - For documentation purposes

3. **Lab-specific Config**: `<lab_repo>/clab_tools_files/config.yaml`
   - Contains clab-tools specific configuration
   - Includes remote host settings for containerlab
   - Read by clab-tools during deployment

4. **Lab Metadata**: `<lab_repo>/lab-metadata.yaml`
   - Lab discovery and management metadata
   - Includes NetBox settings specific to the lab
   - Read by backend during repository scanning

### Remote Deployment Configuration

**IMPORTANT**: For remote deployments to work properly, you need:

1. **SSH Key Authentication**: The backend server must have passwordless SSH access to the remote host
   ```bash
   ssh-copy-id mcolburn@10.1.91.4
   ```

2. **Environment Variable for clab-tools Password** (if sudo is required):
   ```bash
   export CLAB_TOOLS_PASSWORD="your-password"
   ```

3. **Proper config.yaml in the lab repository**:
   ```yaml
   # clab_tools_files/config.yaml
   remote:
     host: 10.1.91.4
     user: mcolburn
     # Password should come from environment variable
   ```

4. **NetBox Configuration** (if using dynamic IPs):
   - Update `~/.labctl/config.yaml` with NetBox details:
   ```yaml
   netbox:
     enabled: true
     url: "http://10.1.80.12:8080"
     token: "your-api-token"
     default_prefix: "10.100.100.0/24"
   ```

### Common Deployment Issues

1. **Bootstrap Failed**: Usually means SSH/authentication issues
   - ✅ **Use SSH Setup Script**: `./scripts/setup-remote-ssh.sh`
   - This script automatically:
     - Generates SSH keys if needed
     - Sets up passwordless SSH authentication
     - Tests connectivity to remote host
     - Verifies clab-tools availability
   - Manual check: `ssh mcolburn@10.1.91.4`
   - Ensure clab-tools is installed on remote host
   - Check bootstrap.sh exists and is executable

2. **No Active Deployments**: Deployment failed during bootstrap
   - Check `/var/lib/labctl/logs/<deployment_id>.log` for details
   - Verify remote host has sufficient resources
   - Ensure all paths in config files are correct

3. **NetBox IP Allocation Failed**: 
   - Verify NetBox is accessible
   - Check API token has proper permissions
   - Ensure prefix exists in NetBox

4. **SSH Authentication Issues**: 
   - ✅ **Automated Fix Available**: Run `./scripts/setup-remote-ssh.sh`
   - Script handles SSH key generation and remote setup
   - Validates CLAB_TOOLS_PASSWORD environment variable
   - Tests end-to-end connectivity

5. **Active Deployments Silently Failing**: 
   - Deployments appear to start but fail without clear error messages
   - Web UI may show deployment initiated but no active deployments appear
   - **Troubleshooting Steps**:
     - Check backend logs for detailed error messages
     - Run `./scripts/test-deployment.sh` to validate configuration
     - Use `./tests/test_configuration.py` to verify all settings
     - Monitor deployment logs in real-time during attempts
   - **Common Causes**:
     - SSH connectivity issues (use setup-remote-ssh.sh)
     - Missing or incorrect lab configuration files
     - Remote host resource constraints
     - Incorrect file permissions on bootstrap.sh

## Development Environment

### Quick Start for Development

After Phase 2 reorganization, use these commands for development:

```bash
# Backend Development
./scripts/run-backend.sh  # Starts Flask on http://localhost:5001

# Or manually:
python3 -m venv .venv
.venv/bin/pip install -r requirements/backend.txt
PYTHONPATH=. .venv/bin/python -m src.backend.app

# CLI Development
# Install in development mode
./scripts/install-labctl.sh
# Then use labctl normally
labctl --help

# Running tests
PYTHONPATH=. .venv/bin/python tests/run_tests.py
```

### Testing Remote Deployments

To test remote deployments without an actual remote host:

1. **Local Testing**: Modify the lab's config.yaml to remove remote settings
2. **Mock Remote Host**: Use Docker container as fake remote host
3. **Unit Tests**: Run deployment tests with mocked SSH

```python
# Example test for remote deployment
def test_remote_deployment():
    # Mock SSH connection
    with patch('paramiko.SSHClient') as mock_ssh:
        # Test deployment logic
        result = lab_manager.deploy_lab('test-lab')
        assert result['success']
```

### Current Status (Post Phase 2)

The codebase has been reorganized into a modular structure:
- Backend logic separated into core modules (lab_manager, git_ops, clab_runner)
- API routes split by functionality (repos, labs, tasks, health)
- CLI commands modularized (repo, lab, device_config, system)
- All installation scripts updated for new structure

**Current Status (Post Phase 3):**

The codebase now includes complete NetBox integration:
- Dynamic IP allocation from NetBox prefixes
- Device registration with lab metadata
- Configuration validation and error handling
- CLI commands for NetBox operations
- Comprehensive test coverage (94 tests)

**Next Steps:**
1. Phase 4: Web UI Development
2. Enhanced monitoring integration
3. CI/CD pipeline implementation

## Future Enhancements

### Platform Drivers
```python
# drivers/base.py
class LabDriver(ABC):
    @abstractmethod
    def deploy(self, lab_path, version):
        pass
    
    @abstractmethod
    def destroy(self, lab_id):
        pass

# drivers/kvm.py
class KVMDriver(LabDriver):
    def deploy(self, lab_path, version):
        # Use Ansible to deploy KVM VMs
        ansible_runner.run(
            playbook='ansible/deploy.yml',
            inventory='ansible/inventory.yml'
        )
```

### Additional Features

1. **Lab Catalog**
   - Central registry of available labs
   - Search by tags/category
   - Community contributions

2. **Enhanced Monitoring**
   - Lab-specific Grafana dashboards
   - Resource usage tracking
   - Deployment history
   - Performance baselines

3. **Automation**
   - Scheduled lab deployments
   - Automatic cleanup after timeout
   - CI/CD integration for lab testing
   - Pre-deployment resource checks
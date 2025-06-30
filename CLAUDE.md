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
├── run-backend.sh           # Development helper script
├── app.py                   # Legacy (to be removed)
├── labctl.py                # Legacy (to be removed)
└── lab_manager.py           # Legacy FastAPI version (to be removed)
```

### Phase 2 Reorganization Status

✅ **Completed Tasks:**
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

⏳ **In Progress:**
- Testing all functionality after reorganization

📋 **Remaining:**
- Remove or archive old legacy files (app.py, labctl.py, lab_manager.py)

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
labctl netbox sync <lab-id>            # Sync lab devices to NetBox
labctl netbox allocate <lab-id>        # Pre-allocate IPs for a lab
labctl netbox release <lab-id>         # Release allocated IPs

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
- IP allocation/deallocation
- Device registration/removal

## Development Environment

### Quick Start for Development

After Phase 2 reorganization, use these commands for development:

```bash
# Backend Development
./run-backend.sh  # Starts Flask on http://localhost:5000

# Or manually:
python3 -m venv .venv
.venv/bin/pip install -r requirements/backend.txt
PYTHONPATH=. .venv/bin/python -m src.backend.app

# CLI Development
# Install in development mode
./scripts/install-labctl.sh
# Then use labctl normally
labctl --help

# Running tests (when implemented)
PYTHONPATH=. .venv/bin/pytest tests/
```

### Current Status (Post Phase 2)

The codebase has been reorganized into a modular structure:
- Backend logic separated into core modules (lab_manager, git_ops, clab_runner)
- API routes split by functionality (repos, labs, tasks, health)
- CLI commands modularized (repo, lab, device_config, system)
- All installation scripts updated for new structure

**Next Steps:**
1. Test all functionality with new structure
2. Remove legacy files (old app.py, labctl.py, lab_manager.py)
3. Begin Phase 3: NetBox Integration

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
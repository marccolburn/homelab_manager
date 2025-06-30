# Network Lab Management System

## Overview

This repository contains a comprehensive network lab management system designed for network engineers who need to demo and study network topologies. The system provides automated deployment, management, and teardown of containerized network labs.

## Features

- 🚀 **Automated Lab Deployment**: One-command lab deployment with validation
- 🌐 **Web Interface**: Modern UI for lab selection and management  
- 📊 **NetBox Integration**: Automatic device registration and inventory
- 🔄 **Git-based Workflow**: Trunk-based development with tagged releases
- ✅ **Pre/Post Validation**: Comprehensive testing of lab deployments
- 📱 **Multi-lab Support**: Centralized management of multiple topologies
- 🏷️ **Version Control**: Tagged releases with semantic versioning

## Architecture

### Repository Structure
```
lab-topology/
├── README.md                    # This file
├── lab-metadata.yaml           # Lab discovery metadata
├── topology.clab.yaml         # ContainerLab topology
├── requirements.txt            # Python dependencies
├── clab_tools_files/           # Bootstrap tools
│   ├── bootstrap.sh           # Deployment script
│   ├── teardown.sh           # Cleanup script
│   ├── config.yaml           # Lab configuration
│   ├── nodes.csv             # Node definitions
│   └── connections.csv       # Topology connections
├── router_configs/            # Device configurations
│   ├── set_configs/          # Junos set format
│   └── non_set_configs/      # Traditional format
├── slax_scripts/             # SLAX automation scripts
├── tests/                    # Validation scripts
│   └── validate-topology.py # Pre/post deployment tests
├── docs/                     # Documentation
├── .github/workflows/        # CI/CD pipeline
└── web_interface.html        # Lab management UI
```

## Quick Start

### 1. Prerequisites

- Python 3.11 or higher
- ContainerLab installed on target host
- SSH access to ContainerLab host
- Git configured for version control

### 2. Installation

```bash
# Clone this repository
git clone <repository-url>
cd <lab-directory>

# Install Python dependencies
pip install -r requirements.txt

# Make scripts executable
chmod +x clab_tools_files/*.sh
```

### 3. Configuration

Edit `clab_tools_files/config.yaml` to match your environment:

```yaml
remote:
  enabled: true
  host: "your-lab-host-ip"
  username: "your-username"
  topology_remote_dir: "/path/to/topology/storage"

topology:
  default_topology_name: "your-lab-name"
  default_mgmt_subnet: "10.100.100.0/24"
```

### 4. Deploy Lab

```bash
# Deploy the lab
./clab_tools_files/bootstrap.sh

# Or using the web interface
python lab_manager.py
# Then open http://localhost:8000 in your browser
```

### 5. Manage Lab

```bash
# Check deployment status
python tests/validate-topology.py --post-deploy

# Teardown lab
./clab_tools_files/teardown.sh
```

## Lab Management System

### Central Lab Manager

The `lab_manager.py` provides a REST API for managing multiple labs:

```bash
# Start the lab manager
python lab_manager.py

# API endpoints
GET  /labs                    # List available labs
POST /labs/{id}/deploy       # Deploy a lab
GET  /deployments            # List active deployments  
DELETE /deployments/{id}     # Teardown a deployment
```

### Web Interface

Open `web_interface.html` in your browser for a modern UI to:
- Browse available labs by category
- View lab requirements and descriptions
- Deploy labs with one click
- Monitor active deployments
- Teardown labs when complete

## Git Workflow

### Trunk-based Development

1. **Main Branch**: Always deployable, protected
2. **Feature Branches**: Short-lived, focused changes
3. **Tagged Releases**: Semantic versioning (v1.0.0, v1.1.0, etc.)

### Release Process

```bash
# Create and push a new release
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# GitHub Actions will automatically:
# - Validate the lab
# - Run security scans
# - Build documentation
# - Create a GitHub release
```

## NetBox Integration

Configure NetBox integration in `lab_manager_config.yaml`:

```yaml
netbox:
  enabled: true
  url: "http://your-netbox-instance"
  token: "your-api-token"
  site_name: "Lab Environment"
```

When labs are deployed, devices are automatically registered in NetBox with:
- Management IP addresses
- Device roles and types
- Site and tenant assignments
- Custom fields for lab metadata

## Validation and Testing

### Pre-deployment Validation
- Required files check
- YAML syntax validation
- Resource requirements check
- Remote connectivity test

### Post-deployment Validation
- Container status verification
- Management connectivity test
- Device configuration validation

```bash
# Run validation manually
python tests/validate-topology.py --pre-deploy
python tests/validate-topology.py --post-deploy
```

## Multi-Lab Repository Setup

### Directory Structure
```
network-labs/
├── lab-manager/              # Central management system
│   ├── lab_manager.py
│   ├── lab_manager_config.yaml
│   └── web_interface.html
└── repositories/            # Individual lab repos
    ├── jncie-sp-lab/
    ├── bgp-advanced-lab/
    ├── mpls-te-lab/
    └── datacenter-lab/
```

### Lab Discovery

The lab manager automatically discovers labs from configured Git repositories:

```yaml
# lab_manager_config.yaml
repositories:
  - url: "https://github.com/org/jncie-sp-lab.git"
    category: "Service Provider"
  - url: "https://github.com/org/bgp-advanced-lab.git"
    category: "BGP"
```

## Customization

### Adding New Device Types

1. Update `topology.clab.yaml` with new node definitions
2. Add device configurations in `router_configs/`
3. Update `lab-metadata.yaml` with new requirements
4. Test with validation scripts

### Custom Validation

Extend `tests/validate-topology.py`:

```python
def _check_custom_requirement(self) -> bool:
    """Add your custom validation logic"""
    # Implementation here
    return True
```

## Troubleshooting

### Common Issues

1. **Remote Connection Failed**
   - Check SSH connectivity: `ssh user@host`
   - Verify SSH key authentication
   - Check firewall rules

2. **Container Start Failed**
   - Verify image availability
   - Check resource requirements
   - Review ContainerLab logs

3. **Management Network Issues**
   - Verify subnet configuration
   - Check for IP conflicts
   - Validate bridge setup

### Debug Mode

Enable debug logging in `clab_tools_files/config.yaml`:

```yaml
debug: true
logging:
  level: "DEBUG"
  file_path: "./debug.log"
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make changes and test thoroughly
4. Submit a pull request

### Code Standards

- Follow PEP 8 for Python code
- Use meaningful commit messages
- Update documentation for new features
- Ensure all tests pass

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

- Create an issue for bugs or feature requests
- Check existing issues before creating new ones
- Provide detailed information for troubleshooting

## Roadmap

- [ ] Support for additional network vendors
- [ ] Integration with monitoring systems
- [ ] Lab scheduling and reservations
- [ ] Performance benchmarking tools
- [ ] Automated lab testing scenarios

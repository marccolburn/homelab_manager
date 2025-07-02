# Homelab Manager

A modern, API-first lab management system that simplifies network topology deployment and management. Built as a wrapper around `clab-tools`, it provides both CLI and web interfaces for managing containerized network labs.

## Features

- 🚀 **Automated Lab Deployment**: One-command deployment to remote hosts
- 🌐 **Modern Web UI**: Responsive dashboard for lab management and settings
- 📊 **NetBox Integration**: Dynamic IP allocation and device registration
- 🔄 **Git-based Workflow**: Repository management with version control
- ✅ **Real-time Monitoring**: Live deployment logs and status updates
- 📱 **Multi-interface**: Consistent CLI and web UI using shared API
- 🔐 **Secure Configuration**: Web-based settings for remote credentials

## Quick Start

### Prerequisites
- Python 3.11+
- `clab-tools` installed
- SSH access to lab host (for remote deployments)

### Installation
```bash
git clone https://github.com/your-org/homelab-manager.git
cd homelab-manager
./scripts/install-labctl.sh
```

### Start Backend
```bash
./scripts/run-backend.sh
# Access web UI: http://localhost:5001
```

### First Lab Deployment
1. **Web UI**: Open `http://localhost:5001` and follow the interface
2. **CLI**: 
   ```bash
   labctl repo add git@github.com:user/lab-repo.git
   labctl deploy lab-name
   ```

## Architecture

**API-First Design**: Flask backend provides RESTful API for all operations.

```
homelab-manager/
├── src/backend/     # Flask API server
├── src/cli/         # CLI client
├── src/web/static/  # Web UI (HTML/CSS/JS)
├── scripts/         # Installation scripts
└── docs/           # Documentation
```

## Documentation

- **[Quick Start Guide](docs/quickstart.md)** - 5-minute setup
- **[Installation Guide](docs/installation.md)** - Complete installation
- **[Web UI Guide](docs/web-ui-guide.md)** - Using the web interface
- **[CLI Reference](docs/commands.md)** - Command documentation
- **[Configuration Guide](docs/configuration.md)** - Settings and setup
- **[API Documentation](docs/api.md)** - REST API reference

## Support

- **Issues**: [GitHub Issues](https://github.com/your-org/homelab-manager/issues)
- **Documentation**: See `docs/` directory
- **Development**: See `docs/development.md`

## License

[Your License Here]
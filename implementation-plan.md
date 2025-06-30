# Homelab Manager Implementation Plan

## Overview

This document outlines the implementation plan for the API-first homelab management system that leverages `clab-tools` for all containerlab operations. The architecture separates concerns with a Flask backend API and lightweight CLI/Web clients.

## Phase 1: API-First Architecture (COMPLETED)

### 1.1 Flask Backend API (`app.py`) - ✅ COMPLETED
- RESTful API with all business logic
- Lab repository management (Git operations)
- Deployment orchestration via clab-tools
- Async task tracking for deployments  
- Configuration scenario management
- Health check and status endpoints

### 1.2 CLI Client (`labctl.py`) - ✅ COMPLETED
- Lightweight HTTP client using Click framework
- Rich console interface with progress bars
- API communication layer
- No business logic - pure client implementation

### 1.3 Installation System - ✅ COMPLETED
**Three deployment scenarios supported:**
- `install-backend.sh` - RHEL/Fedora lab server installation
- `install-frontend.sh` - User workstation CLI installation  
- `install-labctl.sh` - All-in-one installation

**Requirements files:**
- `requirements-backend.txt` - Backend-only dependencies
- `requirements-frontend.txt` - CLI-only dependencies
- `requirements.txt` - Combined for all-in-one install

### 1.4 RHEL/Fedora Integration - ✅ COMPLETED
- systemd service configuration
- firewalld automatic configuration
- dnf/yum package management
- Service user creation and permissions
- Comprehensive documentation

**Key Commands Implemented:**
- `labctl repo add/list/update/remove` - Repository management
- `labctl deploy/destroy/status` - Lab lifecycle management
- `labctl config list/apply` - Configuration scenarios
- `labctl logs` - Deployment log viewing

## Phase 2: Code Organization and Modularity (Current - Week 1)

### 2.1 Directory Restructuring - 🚧 IN PROGRESS
**Current flat structure needs reorganization for maintainability:**

**Proposed new structure:**
```
homelab-manager/
├── src/
│   ├── backend/
│   │   ├── __init__.py
│   │   ├── app.py              # Main Flask application
│   │   ├── api/                # API route handlers
│   │   │   ├── __init__.py
│   │   │   ├── repos.py        # Repository management endpoints
│   │   │   ├── labs.py         # Lab deployment endpoints
│   │   │   ├── tasks.py        # Async task endpoints
│   │   │   └── health.py       # Health check endpoints
│   │   ├── core/               # Core business logic
│   │   │   ├── __init__.py
│   │   │   ├── lab_manager.py  # Lab management class
│   │   │   ├── git_ops.py      # Git operations
│   │   │   ├── clab_runner.py  # clab-tools integration
│   │   │   └── config.py       # Configuration management
│   │   ├── integrations/       # External integrations
│   │   │   ├── __init__.py
│   │   │   ├── netbox.py       # NetBox IP management
│   │   │   └── monitoring.py   # Prometheus/Grafana
│   │   └── utils/              # Utilities
│   │       ├── __init__.py
│   │       ├── validators.py   # Input validation
│   │       └── helpers.py      # Common helpers
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── main.py             # CLI entry point
│   │   ├── client.py           # API client
│   │   ├── commands/           # Command implementations
│   │   │   ├── __init__.py
│   │   │   ├── repo.py         # Repository commands
│   │   │   ├── lab.py          # Lab commands
│   │   │   └── config.py       # Config commands
│   │   └── utils/              # CLI utilities
│   │       ├── __init__.py
│   │       ├── console.py      # Rich console helpers
│   │       └── validators.py   # Input validation
│   └── web/                    # Future web UI
│       ├── static/
│       │   ├── css/
│       │   ├── js/
│       │   └── index.html
│       └── templates/
├── scripts/                    # Installation scripts
│   ├── install-backend.sh
│   ├── install-frontend.sh
│   └── install-labctl.sh
├── config/                     # Configuration templates
│   ├── systemd/
│   │   └── labctl-backend.service
│   ├── nginx/
│   │   └── labctl.conf
│   └── prometheus/
│       └── prometheus.yml
├── tests/                      # Test suite
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── docs/                       # Documentation
├── requirements/               # Dependency files
│   ├── backend.txt
│   ├── frontend.txt
│   ├── dev.txt
│   └── all.txt
└── .github/                    # CI/CD workflows
    └── workflows/
```

### 2.2 Module Separation Tasks

**Detailed Task List:**
1. ✅ **Extract LabManager class** from app.py to src/backend/core/lab_manager.py - COMPLETED
2. ✅ **Create Git operations module** in src/backend/core/git_ops.py - COMPLETED
3. ✅ **Create clab-tools runner module** in src/backend/core/clab_runner.py - COMPLETED
4. ✅ **Split Flask API routes** into separate modules in src/backend/api/ - COMPLETED
   - repos.py - Repository management endpoints
   - labs.py - Lab deployment endpoints  
   - tasks.py - Async task endpoints
   - health.py - Health check endpoints
5. ✅ **Move main Flask app** to src/backend/app.py and update imports - COMPLETED
6. ✅ **Extract CLI commands** into separate modules in src/cli/commands/ - COMPLETED
   - repo.py - Repository commands
   - lab.py - Lab deployment commands
   - device_config.py - Device configuration scenarios
   - system.py - System/server configuration
7. ✅ **Create API client module** in src/cli/client.py - COMPLETED
8. ✅ **Move labctl.py** to src/cli/main.py and update imports - COMPLETED
9. ✅ **Update installation scripts** for new directory structure - COMPLETED
10. ✅ **Update systemd service file** for new app.py location - COMPLETED
11. ⏳ **Test all functionality** after reorganization - IN PROGRESS
12. 📋 **Remove or archive old lab_manager.py** file

### 2.3 Benefits of Reorganization
- **Improved maintainability** - Clear separation of concerns
- **Better testing** - Isolated modules easier to test
- **Team collaboration** - Developers can work on specific areas
- **Future expansion** - Room for additional integrations

## Phase 3: NetBox Integration (Week 2)

### 3.1 IP Allocation Module - 📋 PLANNED
**Implementation in `src/backend/integrations/netbox.py`:**
```python
class NetBoxManager:
    def allocate_ips(self, lab_id: str, nodes: List[str]) -> Dict[str, str]:
        """Allocate IPs from NetBox prefix for lab nodes"""
        
    def release_ips(self, lab_id: str) -> bool:
        """Release all IPs allocated to a lab"""
        
    def update_nodes_csv(self, nodes_file: Path, ip_assignments: Dict) -> None:
        """Update nodes.csv with allocated management IPs"""
```

### 3.2 Backend API Enhancement
- Add `--allocate-ips` flag to deploy endpoint
- Integrate IP allocation before clab-tools bootstrap
- Automatic IP release on lab destruction
- NetBox device registration with lab metadata

## Phase 4: Web UI Development (Week 3)

### 4.1 Single-Page Application - 📋 PLANNED
- **Pure HTML/CSS/JavaScript** - No build tools required
- **Real-time updates** via Server-Sent Events
- **Responsive design** for mobile/tablet access
- **API integration** using same endpoints as CLI

### 4.2 Features
- Lab repository browser with filtering/search
- One-click deployment with version selection
- Real-time deployment progress and logs
- Configuration scenario management
- Resource usage dashboards (Grafana integration)

## Phase 5: CI/CD Pipeline (Week 3-4)

### 5.1 GitHub Actions Workflows - 📋 PLANNED

**`.github/workflows/test-installation.yml`:**
```yaml
name: Test Installation Methods

on: [push, pull_request]

jobs:
  test-backend-install:
    runs-on: ubuntu-latest
    container: 
      image: registry.access.redhat.com/ubi9/ubi:latest
    steps:
      - uses: actions/checkout@v4
      - name: Install system dependencies
        run: dnf install -y python3 python3-pip git
      - name: Test backend installation
        run: |
          chmod +x scripts/install-backend.sh
          ./scripts/install-backend.sh
      - name: Verify backend service
        run: |
          systemctl status labctl-backend
          curl -f http://localhost:5000/api/health

  test-frontend-install:
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Test CLI installation
        run: |
          chmod +x scripts/install-frontend.sh
          ./scripts/install-frontend.sh
      - name: Verify CLI installation
        run: |
          labctl --help
          labctl version

  test-all-in-one:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Test all-in-one installation
        run: |
          chmod +x scripts/install-labctl.sh
          sudo ./scripts/install-labctl.sh
      - name: Verify installation
        run: |
          labctl --help
          systemctl status labctl-backend
          curl -f http://localhost:5000/api/health
```

### 5.2 Additional CI Tests
**Code Quality:**
```yaml
  lint-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements/dev.txt
      - name: Run linting
        run: |
          flake8 src/
          black --check src/
          mypy src/
      - name: Run unit tests
        run: pytest tests/unit/
      - name: Run integration tests
        run: pytest tests/integration/
```

**Security Scanning:**
```yaml
  security-scan:
    runs-name: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run security scan
        uses: pypa/gh-action-pip-audit@v1.0.8
      - name: Run Bandit security linter
        run: bandit -r src/
```

### 5.3 Container Testing
**Test installation in multiple environments:**
- RHEL 9 UBI container
- Fedora 40 container  
- Rocky Linux 9 container
- Ubuntu 22.04 (for comparison)

## Phase 6: Monitoring Integration (Week 4)

### 6.1 Enhanced Monitoring Stack - 📋 PLANNED
**Flexible deployment options:**
- **Local monitoring** - All components on lab server
- **Remote monitoring** - Prometheus/Grafana elsewhere, scrape lab server
- **Hybrid monitoring** - Mix of local and remote components

### 6.2 Monitoring Components
```yaml
# monitoring/docker-compose.yml
services:
  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    # Container metrics collection
    
  node-exporter:
    image: prom/node-exporter:latest
    # Host metrics collection
    
  prometheus:
    image: prom/prometheus:latest
    # Metrics storage and alerting
    
  grafana:
    image: grafana/grafana:latest
    # Visualization and dashboards
    
  alertmanager:
    image: prom/alertmanager:latest
    # Alert routing and notification
```

### 6.3 Custom Metrics
- Lab deployment status and duration
- Active lab resource usage
- API endpoint performance
- Error rates and availability

## Phase 7: Testing and Documentation (Week 5)

### 7.1 Comprehensive Testing - 📋 PLANNED
**Test Categories:**
- **Unit tests** - Individual functions and classes
- **Integration tests** - API endpoints and workflows  
- **E2E tests** - Complete user workflows
- **Installation tests** - All installation methods
- **Performance tests** - Load testing for API

### 7.2 Documentation Completion
- **API Reference** - Complete OpenAPI/Swagger documentation
- **CLI Reference** - Detailed command documentation  
- **Lab Creation Guide** - How to create new labs
- **Troubleshooting Guide** - Common issues and solutions
- **Migration Guide** - From existing lab_manager.py

### 7.3 Release Preparation
- Version tagging strategy
- Release notes generation
- Package building and distribution
- Security review and hardening

## Revised Implementation Timeline

### Phase 1: ✅ COMPLETED (Week 1)
- Flask backend API with all core functionality
- CLI client with comprehensive commands
- Three installation methods with automation
- RHEL/Fedora integration and documentation

### Phase 2: 🚧 Current Phase (Week 1-2)
**Code Organization Priority:**
1. **Day 1-2**: Create new directory structure
2. **Day 3-4**: Extract LabManager class and split API routes
3. **Day 5-7**: Reorganize CLI into command modules
4. **Week 2**: Update installation scripts for new structure

### Phase 3: 📋 Next Phase (Week 2-3)
**NetBox Integration:**
1. Implement NetBoxManager class
2. Add IP allocation to deployment workflow
3. Test with real NetBox instance
4. Document NetBox configuration

### Phase 4: 📋 Following Phase (Week 3-4)
**Web UI Development:**
1. Create single-page application
2. Implement real-time updates
3. Add responsive design
4. Integrate with existing API

### Phase 5: 📋 CI/CD Pipeline (Week 3-4)
**Parallel with Web UI:**
1. Set up GitHub Actions workflows
2. Test all installation methods
3. Add security scanning
4. Create multi-environment testing

### Phase 6-7: 📋 Final Phases (Week 4-5)
**Monitoring and Polish:**
1. Enhanced monitoring stack
2. Comprehensive testing suite
3. Complete documentation
4. Release preparation

## Success Metrics

### Technical Quality
- ✅ **API-first architecture** - Clean separation of concerns
- ✅ **Multiple deployment options** - Flexible installation
- ✅ **RHEL/Fedora optimization** - Target platform support
- 🚧 **Modular code structure** - Maintainable codebase
- 📋 **Comprehensive testing** - CI/CD validation
- 📋 **Production readiness** - Security and monitoring

### User Experience  
- ✅ **Simple CLI interface** - Easy to use commands
- ✅ **Automated installation** - One-script setup
- 📋 **Web UI option** - Browser-based management
- 📋 **Real-time feedback** - Progress and status updates
- 📋 **Good documentation** - Clear setup and usage guides

### Integration
- ✅ **clab-tools compatibility** - Leverages existing tooling
- 📋 **NetBox integration** - Dynamic IP management
- 📋 **Monitoring support** - Grafana/Prometheus integration
- 📋 **Git workflow** - Version control for labs

## Risk Mitigation

### Technical Risks
- **Breaking changes during reorganization** - Maintain backward compatibility
- **Installation failures** - Comprehensive CI testing
- **Performance issues** - Load testing and optimization
- **Security vulnerabilities** - Regular scanning and reviews

### Mitigation Strategies
- **Incremental refactoring** - Small, testable changes
- **Multi-environment testing** - Various RHEL/Fedora versions
- **Documentation first** - Clear upgrade paths
- **Community feedback** - Early user testing

## Testing Plan

### Unit Tests
- CLI command parsing
- Git operations
- NetBox integration
- State management

### Integration Tests
- Full deployment workflow
- IP allocation/deallocation
- Remote host operations
- Monitoring data flow

### Manual Testing
- Deploy various lab types
- Test version switching
- Verify cleanup operations
- Check monitoring dashboards

## Documentation Requirements

1. **README.md** - Quick start guide
2. **CLAUDE.md** - Development guide (already created)
3. **docs/cli-reference.md** - Complete CLI documentation
4. **docs/lab-creation.md** - Guide for creating new labs
5. **docs/monitoring.md** - Monitoring setup guide
6. **docs/netbox.md** - NetBox integration guide

## Success Criteria

1. **Simplicity**: Fewer dependencies, cleaner code
2. **Reliability**: Consistent deployments, proper cleanup
3. **Performance**: Fast operations, minimal overhead
4. **Maintainability**: Clear code structure, good documentation
5. **Compatibility**: Works with existing clab-tools workflows

## Future Considerations

### Phase 6: Platform Drivers (Future)
- Abstract deployment logic into drivers
- Add KVM support via Ansible
- Support for VMware environments
- Plugin architecture for new platforms

### Phase 7: Advanced Features (Future)
- Lab composition (multi-lab deployments)
- Resource reservation system
- CI/CD integration
- Lab marketplace/registry

## Risk Mitigation

1. **Backward Compatibility**: Keep existing lab repos working
2. **Data Loss**: Implement proper state backup
3. **Remote Failures**: Add retry logic and timeouts
4. **Resource Conflicts**: Check resources before deployment
5. **Version Conflicts**: Clear version resolution strategy
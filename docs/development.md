# Development Guide

This guide covers the development workflow, architecture, and best practices for contributing to the Homelab Manager project.

## Table of Contents

- [Development Setup](#development-setup)
- [Project Architecture](#project-architecture)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Code Standards](#code-standards)
- [Contributing](#contributing)
- [Debugging](#debugging)
- [Performance](#performance)
- [Deployment](#deployment)

## Development Setup

### Prerequisites

- Python 3.9+ 
- Git
- Virtual environment tool (venv, virtualenv, or conda)
- Optional: Docker (for containerized development)

### Quick Setup

```bash
# Clone the repository
git clone <repository-url>
cd homelab_manager

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements/all.txt

# Verify installation
python -m src.backend.app --help
```

### IDE Configuration

#### VS Code
Recommended extensions and settings:

```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./.venv/bin/python",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests"],
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length", "88"],
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        ".pytest_cache": true,
        "htmlcov": true
    }
}
```

#### PyCharm
- Set interpreter to `.venv/bin/python`
- Enable pytest as test runner
- Configure black as code formatter
- Set project root to repository root

### Environment Variables

```bash
# Development environment
export FLASK_ENV=development
export LABCTL_API_URL=http://localhost:5000
export PYTHONPATH=.

# Optional debugging
export FLASK_DEBUG=1
export LOG_LEVEL=DEBUG
```

## Project Architecture

### High-Level Overview

```
homelab-manager/
├── src/                    # Source code
│   ├── backend/           # Flask API server
│   ├── cli/               # Command-line interface
│   └── web/               # Web interface (future)
├── tests/                 # Test suite
├── docs/                  # Documentation
├── scripts/               # Installation & utility scripts
└── config/                # Configuration templates
```

### Backend Architecture

#### API-First Design
The Flask backend provides a REST API that serves as the single source of truth for all operations. Both CLI and web interfaces are thin clients.

```python
# Backend components
src/backend/
├── app.py                 # Flask application factory
├── api/                   # REST API endpoints
│   ├── repos.py          # Repository management
│   ├── labs.py           # Lab deployment
│   ├── tasks.py          # Async task tracking
│   └── health.py         # Health & config
├── core/                  # Business logic
│   ├── lab_manager.py    # Main orchestration
│   ├── git_ops.py        # Git operations
│   ├── clab_runner.py    # Containerlab integration
│   └── config.py         # Configuration management
├── integrations/          # External integrations
│   ├── netbox.py         # IP management (future)
│   └── monitoring.py     # Metrics & monitoring (future)
└── utils/                 # Utilities
    ├── validators.py     # Input validation
    └── helpers.py        # Common functions
```

#### Key Design Principles

1. **Separation of Concerns**: Each module has a single responsibility
2. **Dependency Injection**: Dependencies are injected for testability
3. **Error Handling**: Consistent error handling with detailed messages
4. **Async Operations**: Long-running operations use background tasks
5. **State Management**: Centralized state management with file persistence

### CLI Architecture

The CLI is a lightweight HTTP client that calls the Flask API:

```python
src/cli/
├── main.py               # CLI entry point & argument parsing
├── client.py             # HTTP client for API communication
├── commands/             # Command implementations
│   ├── repo.py          # Repository commands
│   ├── lab.py           # Lab deployment commands
│   ├── device_config.py # Configuration scenarios
│   └── system.py        # System utilities
└── utils/                # CLI utilities
    ├── console.py       # Rich console formatting
    └── validators.py    # Input validation
```

### Data Flow

```
CLI Command → HTTP Request → Flask API → Business Logic → External Tools
     ↓              ↓            ↓            ↓              ↓
Rich Output ← JSON Response ← API Response ← Result ← Tool Output
```

### State Management

The system maintains state in JSON files:

```json
{
    "repos": {
        "lab-id": {
            "id": "lab-id",
            "name": "Lab Name", 
            "path": "/path/to/repo",
            "url": "git://repo.git",
            "metadata": { ... }
        }
    },
    "deployments": {
        "deployment-id": {
            "lab_id": "lab-id",
            "version": "v1.0.0",
            "deployed_at": "2024-12-01T14:30:22",
            "status": "running"
        }
    }
}
```

## Development Workflow

### Setting Up for Development

1. **Clone and Setup**
```bash
git clone <repo-url>
cd homelab_manager
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/all.txt
```

2. **Start Backend in Development Mode**
```bash
# Terminal 1: Start backend
./run-backend.sh

# Or manually:
FLASK_ENV=development python -m src.backend.app
```

3. **Test CLI in Another Terminal**
```bash
# Terminal 2: Test CLI
source .venv/bin/activate
export LABCTL_API_URL=http://localhost:5000

# Use the CLI
./scripts/labctl --help
./scripts/labctl doctor
```

### Development Server

The development server provides:
- Hot reloading on code changes
- Detailed error messages
- Debug toolbar (if enabled)
- Request logging

```bash
# Start with debugging
FLASK_DEBUG=1 python -m src.backend.app

# Start with specific host/port
python -m src.backend.app --host 0.0.0.0 --port 8000
```

### Making Changes

#### Backend Changes

1. **API Endpoints**: Add new endpoints in `src/backend/api/`
2. **Business Logic**: Implement logic in `src/backend/core/`
3. **External Integrations**: Add to `src/backend/integrations/`

Example: Adding a new API endpoint
```python
# src/backend/api/labs.py
@labs_bp.route('/api/labs/<lab_id>/status', methods=['GET'])
def get_lab_status(lab_id):
    """Get detailed status of a specific lab"""
    status = current_app.lab_manager.get_lab_detailed_status(lab_id)
    if 'error' in status:
        return jsonify(status), 404
    return jsonify(status)
```

#### CLI Changes

1. **New Commands**: Add to `src/cli/commands/`
2. **API Client**: Update `src/cli/client.py` for new endpoints
3. **Main CLI**: Register commands in `src/cli/main.py`

Example: Adding a new CLI command
```python
# src/cli/commands/lab.py
@click.command()
@click.argument('lab_id')
@click.pass_context
def inspect(ctx, lab_id):
    """Inspect detailed lab status"""
    client = ctx.obj['client']
    status = client.get_lab_status(lab_id)
    
    # Display formatted output
    console.print_json(data=status)
```

### Testing Changes

Run tests frequently during development:

```bash
# Run all tests
python -m pytest

# Run specific test categories
python -m pytest -m unit
python -m pytest -m integration

# Run tests with coverage
python -m pytest --cov=src --cov-report=html

# Run specific test file
python -m pytest tests/unit/test_lab_manager.py

# Run tests in watch mode (requires pytest-watch)
ptw tests/ --clear
```

### Available Scripts

The project includes several convenience scripts:

```bash
# Development backend server
./run-backend.sh                    # Start Flask backend in development mode

# Installation scripts
./scripts/install-labctl.sh          # All-in-one installation (CLI + backend)
./scripts/install-backend.sh         # Backend-only installation (for servers)
./scripts/install-frontend.sh        # CLI-only installation (for workstations)

# CLI wrapper
./scripts/labctl                     # Pre-built CLI wrapper script

# Test runners
python tests/run_tests.py            # Original unittest runner
python tests/run_tests_pytest.py     # New pytest runner
```

### Debugging

#### Backend Debugging

1. **Enable Debug Mode**
```bash
FLASK_DEBUG=1 ./run-backend.sh
```

2. **Add Breakpoints**
```python
import pdb; pdb.set_trace()  # Simple breakpoint
```

3. **Use Python Debugger with pytest**
```bash
python -m pytest --pdb tests/unit/test_lab_manager.py::test_method
```

#### CLI Debugging

1. **Verbose Output**
```bash
./scripts/labctl -v doctor
```

2. **Debug API Calls**
```python
# In src/cli/client.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Common Issues

1. **Backend Not Running**
   - Error: Connection refused
   - Solution: Start Flask backend with `./run-backend.sh`

2. **Import Errors**
   - Error: ModuleNotFoundError
   - Solution: Set `PYTHONPATH=.` or use `python -m` syntax

3. **State File Corruption**
   - Error: JSON decode error
   - Solution: Delete state file and restart backend

4. **Dependency Issues**
   - Error: Package not found
   - Solution: Install requirements: `pip install -r requirements/all.txt`

## Testing

### Test Structure

```
tests/
├── conftest.py           # Shared fixtures
├── unit/                 # Fast, isolated tests
├── integration/          # Multi-component tests  
└── e2e/                  # End-to-end workflow tests
```

### Running Tests

#### Using pytest (Recommended)
```bash
# Run all tests
python -m pytest

# Run specific test categories
python -m pytest -m unit           # Unit tests only
python -m pytest -m integration    # Integration tests only
python -m pytest -m e2e           # End-to-end tests only

# Run with coverage
python -m pytest --cov=src --cov-report=html

# Using the pytest runner
python tests/run_tests_pytest.py unit
python tests/run_tests_pytest.py coverage
```

#### Using unittest (Legacy)
```bash
# Run all tests
python tests/run_tests.py

# Run specific categories
python -m unittest discover tests/unit
python -m unittest discover tests/integration
```

### Writing Tests

#### Unit Tests
Test individual components in isolation:

```python
import pytest
from src.backend.core.lab_manager import LabManager

@pytest.mark.unit
class TestLabManager:
    def test_list_repos(self, lab_manager):
        # Setup
        lab_manager.state['repos'] = {'test': {...}}
        
        # Execute
        repos = lab_manager.list_repos()
        
        # Verify
        assert len(repos) == 1
        assert repos[0]['id'] == 'test'
```

#### Integration Tests
Test API endpoints with real Flask app:

```python
@pytest.mark.integration
class TestRepoAPI:
    def test_add_repo(self, flask_client):
        response = flask_client.post('/api/repos', 
                                   json={'url': 'git://test.git'})
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
```

#### E2E Tests
Test complete workflows:

```python
@pytest.mark.e2e
class TestWorkflow:
    def test_complete_lab_deployment(self, flask_client):
        # Add repo
        response = flask_client.post('/api/repos', 
                                   json={'url': 'git://lab.git'})
        
        # Deploy lab
        response = flask_client.post('/api/labs/lab/deploy')
        task_id = response.get_json()['task_id']
        
        # Monitor deployment (mocked in tests)
        # ... verify deployment success
```

### Test Data

Use fixtures for consistent test data:

```python
@pytest.fixture
def sample_lab_metadata():
    return {
        "name": "Test Lab",
        "version": "1.0.0",
        "category": "Testing"
    }
```

### Mocking External Dependencies

Mock external tools and services:

```python
@pytest.fixture
def mock_git_ops():
    mock = Mock(spec=GitOperations)
    mock.clone.return_value = {'success': True}
    mock.pull.return_value = {'success': True}
    return mock
```

## Code Standards

### Python Style

Follow PEP 8 with these specifications:

- **Line Length**: 88 characters (Black default)
- **Imports**: Use isort for import sorting
- **Docstrings**: Google style docstrings
- **Type Hints**: Use type annotations where helpful

#### Code Formatting

```bash
# Format code with Black
black src/ tests/

# Sort imports with isort  
isort src/ tests/

# Check style with flake8
flake8 src/ tests/
```

#### Example Code Style

```python
"""
Module for Git operations
"""
from pathlib import Path
from typing import Dict, List, Optional
import subprocess
import logging

logger = logging.getLogger(__name__)


class GitOperations:
    """Handles Git repository operations.
    
    This class provides methods for cloning, updating, and managing
    Git repositories used for lab definitions.
    """
    
    def __init__(self, git_cmd: str = "git") -> None:
        """Initialize Git operations.
        
        Args:
            git_cmd: Path to git executable
        """
        self.git_cmd = git_cmd
    
    def clone(self, repo_url: str, target_path: Path) -> Dict[str, any]:
        """Clone a Git repository.
        
        Args:
            repo_url: Git repository URL
            target_path: Target directory for clone
            
        Returns:
            Dict containing success status and any error messages
            
        Raises:
            subprocess.CalledProcessError: If git command fails
        """
        try:
            result = self._run_command(['clone', repo_url, str(target_path)])
            return {'success': True, 'message': 'Repository cloned successfully'}
        except subprocess.CalledProcessError as e:
            logger.error(f"Git clone failed: {e}")
            return {'success': False, 'error': str(e)}
```

### Documentation Standards

#### Docstring Format
Use Google-style docstrings:

```python
def deploy_lab(self, lab_id: str, version: str = "latest") -> Dict:
    """Deploy a lab environment.
    
    Args:
        lab_id: Unique identifier for the lab
        version: Git tag or branch to deploy (default: "latest")
        
    Returns:
        Dictionary containing deployment status and metadata
        
    Raises:
        ValueError: If lab_id is not found
        RuntimeError: If deployment fails
        
    Example:
        >>> manager = LabManager(config)
        >>> result = manager.deploy_lab("bgp-lab", "v1.2.0")
        >>> print(result['success'])
        True
    """
```

#### API Documentation
Document API endpoints with clear examples:

```python
@labs_bp.route('/api/labs/<lab_id>/deploy', methods=['POST'])
def deploy_lab(lab_id):
    """Deploy a lab environment.
    
    Request Body:
        {
            "version": "v1.2.0",      # Optional, defaults to "latest"
            "allocate_ips": false     # Optional, defaults to false
        }
    
    Returns:
        202: {
            "task_id": "deploy_lab_20241201_143022",
            "message": "Deployment started"
        }
        
        400: {
            "error": "Lab not found: invalid-lab-id"
        }
    """
```

### Error Handling

#### Consistent Error Responses

```python
# Good: Consistent error structure
def handle_error(operation: str, error: Exception) -> Dict:
    return {
        'success': False,
        'error': f"{operation} failed: {str(error)}",
        'operation': operation,
        'timestamp': datetime.utcnow().isoformat()
    }

# API endpoint error handling
try:
    result = current_app.lab_manager.deploy_lab(lab_id)
    return jsonify(result)
except ValueError as e:
    return jsonify({'error': str(e)}), 400
except Exception as e:
    logger.exception("Unexpected error in deploy_lab")
    return jsonify({'error': 'Internal server error'}), 500
```

#### Logging Standards

```python
import logging

logger = logging.getLogger(__name__)

# Log levels
logger.debug("Detailed debugging information")
logger.info("General operational information") 
logger.warning("Something unexpected happened")
logger.error("Error occurred but application continues")
logger.critical("Serious error, application may stop")

# Structured logging
logger.info("Lab deployment started", extra={
    'lab_id': lab_id,
    'version': version,
    'user': user_id
})
```

## Contributing

### Contribution Workflow

1. **Fork the Repository**
```bash
git clone <your-fork-url>
cd homelab_manager
git remote add upstream <original-repo-url>
```

2. **Create Feature Branch**
```bash
git checkout -b feature/your-feature-name
```

3. **Make Changes**
```bash
# Make your changes
git add .
git commit -m "Add feature: your feature description"
```

4. **Run Tests**
```bash
python -m pytest
black src/ tests/
flake8 src/ tests/
```

5. **Push and Create PR**
```bash
git push origin feature/your-feature-name
# Create pull request on GitHub
```

### Code Review Process

#### Before Submitting PR

- [ ] All tests pass
- [ ] Code is formatted with Black
- [ ] Docstrings added for public functions
- [ ] Type hints added where appropriate
- [ ] Manual testing completed
- [ ] Documentation updated if needed

#### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature  
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
```

### Commit Message Format

```
type: brief description

Detailed explanation of what changed and why.

Fixes #123
```

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `style`, `chore`

## Performance

### Performance Considerations

1. **API Response Times**
   - Keep API responses under 200ms for simple operations
   - Use async operations for long-running tasks
   - Implement caching where appropriate

2. **Memory Usage**
   - Avoid loading large files into memory
   - Use generators for large datasets
   - Clean up temporary files

3. **Disk I/O**
   - Minimize file system operations
   - Use batch operations when possible
   - Implement proper cleanup

### Profiling

```bash
# Profile CLI operations
python -m cProfile -o profile.stats -m src.cli.main repo list

# Analyze profile
python -c "import pstats; pstats.Stats('profile.stats').sort_stats('cumulative').print_stats(20)"

# Profile API endpoints
pip install flask-profiler
# Add profiling middleware to Flask app
```

### Optimization Tips

1. **Database Queries**: Use indexes and limit result sets
2. **Network Calls**: Implement timeouts and retries
3. **File Operations**: Use context managers and proper cleanup
4. **Memory**: Profile memory usage with memory_profiler

## Deployment

### Development Deployment

```bash
# Local development
./run-backend.sh

# Development with specific configuration
FLASK_ENV=development CONFIG_FILE=custom.yaml python -m src.backend.app
```

### Production Deployment

#### Using Installation Scripts

```bash
# All-in-one installation (CLI + backend)
sudo ./scripts/install-labctl.sh

# Backend only (for servers)
sudo ./scripts/install-backend.sh

# CLI only (for workstations)
./scripts/install-frontend.sh
```

#### Manual Production Setup

```bash
# Install production dependencies
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 src.backend.app:app

# With configuration file
gunicorn -c gunicorn.conf.py src.backend.app:app
```

#### Using Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements/ requirements/
RUN pip install -r requirements/all.txt

COPY src/ src/
COPY scripts/ scripts/

EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "src.backend.app:app"]
```

#### Systemd Service
The installation scripts create systemd services, but you can also create them manually:

```ini
# /etc/systemd/system/labctl-backend.service
[Unit]
Description=Homelab Manager Backend
After=network.target

[Service]
Type=simple
User=labctl
WorkingDirectory=/opt/homelab-manager
Environment=FLASK_ENV=production
ExecStart=/opt/homelab-manager/.venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 src.backend.app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

### Configuration Management

#### Environment-Specific Configs

```yaml
# config/development.yaml
debug: true
repos_dir: /tmp/labctl/repos
logs_dir: /tmp/labctl/logs

# config/production.yaml  
debug: false
repos_dir: /opt/labctl/repos
logs_dir: /var/log/labctl
```

#### Secrets Management

```bash
# Use environment variables for secrets
export NETBOX_TOKEN=secret_token
export DATABASE_URL=postgresql://user:pass@host/db

# Or use secret management tools
vault kv put secret/labctl netbox_token=secret_token
```

### Monitoring and Logging

#### Application Monitoring

```python
# Add metrics collection
from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter('labctl_requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('labctl_request_duration_seconds', 'Request latency')

@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request  
def after_request(response):
    REQUEST_COUNT.labels(method=request.method, endpoint=request.endpoint).inc()
    REQUEST_LATENCY.observe(time.time() - request.start_time)
    return response
```

#### Structured Logging

```python
import structlog

logger = structlog.get_logger()

logger.info("Lab deployment started", 
           lab_id=lab_id, 
           version=version,
           user_id=user_id)
```

### Backup and Recovery

1. **State File Backup**: Regularly backup state JSON files
2. **Repository Backup**: Backup cloned lab repositories
3. **Configuration Backup**: Version control all configuration
4. **Database Backup**: If using database in future versions

This development guide provides a comprehensive foundation for contributing to and maintaining the Homelab Manager project. Keep it updated as the project evolves.
# Development Guide

Quick guide for developers working on Homelab Manager.

## Setup

### Prerequisites
- Python 3.9+
- Git
- Virtual environment tool

### Quick Start
```bash
git clone <repository-url>
cd homelab_manager

# Setup environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/all.txt

# Start backend
./scripts/run-backend.sh

# Test CLI (in another terminal)
source .venv/bin/activate
export LABCTL_API_URL=http://localhost:5001
./scripts/labctl --help
```

## Project Structure

See [Project Architecture](project_architecture.md) for detailed diagrams and code flow.

```
src/
├── backend/           # Flask API server
│   ├── app.py        # Main Flask application
│   ├── api/          # REST endpoints
│   ├── core/         # Business logic
│   └── integrations/ # External systems
├── cli/              # Command-line interface
│   ├── main.py       # CLI entry point
│   ├── client.py     # API client
│   └── commands/     # Command implementations
└── web/              # Web UI (HTML/JS/CSS)
    └── static/       # Static files
```

## Development Workflow

### Backend Development
```bash
# Start development server
./scripts/run-backend.sh

# Or manually with debugging
FLASK_DEBUG=1 python -m src.backend.app
```

### CLI Development
```bash
# Install in development mode
./scripts/install-labctl.sh

# Test commands
labctl doctor
labctl repo list
```

### Web UI Development
1. Start backend: `./scripts/run-backend.sh`
2. Access UI: `http://localhost:5001`
3. Edit files in `src/web/static/`
4. Refresh browser (no build step needed)

## Testing

### Run All Tests
```bash
# Using pytest (recommended)
python -m pytest

# Using unittest runner
python tests/run_tests.py
```

### Test Categories
```bash
# Unit tests only
python -m pytest -m unit

# Integration tests only  
python -m pytest -m integration

# With coverage
python -m pytest --cov=src --cov-report=html
```

### Test Structure
```
tests/
├── unit/         # Fast, isolated tests
├── integration/  # Multi-component tests
└── e2e/          # End-to-end workflows
```

## Code Standards

### Python Style
- **Formatter**: Black (88 char line length)
- **Import sorting**: isort
- **Linting**: flake8
- **Docstrings**: Google style

```bash
# Format code
black src/ tests/
isort src/ tests/
flake8 src/ tests/
```

### Docstring Example
```python
def deploy_lab(self, lab_id: str, version: str = "latest") -> Dict:
    """Deploy a lab environment.
    
    Args:
        lab_id: Unique identifier for the lab
        version: Git tag or branch to deploy
        
    Returns:
        Dictionary containing deployment status
        
    Raises:
        ValueError: If lab_id is not found
    """
```

## Adding New Features

### API Endpoint
```python
# src/backend/api/labs.py
@labs_bp.route('/api/labs/<lab_id>/action', methods=['POST'])
def lab_action(lab_id):
    """Perform action on lab"""
    result = current_app.lab_manager.action(lab_id)
    return jsonify(result)
```

### CLI Command
```python
# src/cli/commands/lab.py
@click.command()
@click.argument('lab_id')
@click.pass_context
def action(ctx, lab_id):
    """Perform action on lab"""
    client = ctx.obj['client']
    result = client.lab_action(lab_id)
    console.print(f"Action completed: {result}")

# Add to lab_commands list
lab_commands = [deploy, destroy, status, logs, action]
```

### Business Logic
```python
# src/backend/core/lab_manager.py
def action(self, lab_id: str) -> Dict:
    """Perform action on lab"""
    # Validate lab exists
    # Perform action
    # Update state
    # Return result
```

## Key Design Principles

1. **API-First**: All functionality via REST API
2. **Separation of Concerns**: CLI/Web are thin clients
3. **State Management**: Centralized in LabManager
4. **Error Handling**: Consistent error responses
5. **Testing**: Unit tests for all business logic

## Common Tasks

### Add New Lab Command
1. Add method to `LabManager` class
2. Add API endpoint in appropriate module
3. Add CLI command in `src/cli/commands/`
4. Add tests for all layers

### Debug Issues
```bash
# Backend logs
FLASK_DEBUG=1 ./scripts/run-backend.sh

# CLI verbose output
labctl -v doctor

# Check backend health
curl http://localhost:5001/api/health
```

### Database/State Issues
```bash
# Reset state (will lose all data)
rm ~/.labctl/state.json

# Check state file
cat ~/.labctl/state.json | jq
```

## Production Deployment

### Installation Scripts
```bash
# All-in-one (CLI + backend)
sudo ./scripts/install-labctl.sh

# Backend only (servers)
sudo ./scripts/install-backend.sh

# CLI only (workstations)  
./scripts/install-frontend.sh
```

### Manual Production
```bash
# Install production dependencies
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 src.backend.app:app
```

### Configuration
- Backend config: `~/.labctl/config.yaml`
- Lab metadata: `<lab_repo>/lab-metadata.yaml`
- Remote settings: `<lab_repo>/clab_tools_files/config.yaml`

## Architecture References

- [Project Architecture](project_architecture.md) - Detailed system design
- [API Documentation](api.md) - REST API reference
- [Commands Reference](commands.md) - CLI command guide

## Contributing

1. Fork repository
2. Create feature branch: `git checkout -b feature/name`
3. Make changes and add tests
4. Run tests: `python -m pytest`
5. Format code: `black src/ tests/`
6. Create pull request

### Before Submitting PR
- [ ] All tests pass
- [ ] Code formatted with Black
- [ ] Docstrings added for public functions
- [ ] Manual testing completed

This covers the essential development information without excessive detail.
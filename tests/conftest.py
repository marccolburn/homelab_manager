"""
Shared pytest fixtures for homelab manager tests
"""
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock
import sys
import os

# Add src to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.backend.app import create_app
from src.backend.core.git_ops import GitOperations
from src.backend.core.clab_runner import ClabRunner
from src.backend.core.lab_manager import LabManager
from src.cli.client import LabCtlClient


@pytest.fixture(scope="session")
def temp_base_dir():
    """Create a temporary directory for all tests in the session"""
    temp_dir = Path(tempfile.mkdtemp(prefix="labctl_test_"))
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def temp_dirs(temp_base_dir):
    """Create temporary directories for a single test"""
    test_dir = temp_base_dir / f"test_{os.getpid()}"
    repos_dir = test_dir / 'repos'
    logs_dir = test_dir / 'logs'
    state_file = test_dir / 'state.json'
    
    repos_dir.mkdir(parents=True)
    logs_dir.mkdir(parents=True)
    
    yield {
        'base': test_dir,
        'repos': repos_dir,
        'logs': logs_dir,
        'state_file': state_file
    }
    
    # Cleanup handled by session-level fixture


@pytest.fixture
def test_config(temp_dirs):
    """Create test configuration"""
    return {
        'repos_dir': str(temp_dirs['repos']),
        'logs_dir': str(temp_dirs['logs']),
        'state_file': str(temp_dirs['state_file']),
        'git_cmd': 'git',
        'clab_tools_cmd': 'clab-tools'
    }


@pytest.fixture
def mock_git_ops():
    """Create a mock GitOperations instance"""
    mock = Mock(spec=GitOperations)
    mock.clone.return_value = {'success': True}
    mock.pull.return_value = {'success': True}
    mock.get_tags.return_value = ['v1.0.0', 'v1.1.0']
    mock.checkout.return_value = {'success': True}
    mock.fetch_tags.return_value = {'success': True}
    return mock


@pytest.fixture
def mock_clab_runner():
    """Create a mock ClabRunner instance"""
    mock = Mock(spec=ClabRunner)
    mock.bootstrap_lab.return_value = (True, {'success': True, 'message': 'Deployment successful'})
    mock.teardown_lab.return_value = (True, {'success': True, 'message': 'Destroy successful'})
    mock.get_lab_status.return_value = {'status': 'running'}
    mock.check_clab_tools.return_value = True
    return mock


@pytest.fixture
def lab_manager(test_config, mock_git_ops, mock_clab_runner, monkeypatch):
    """Create a LabManager instance with mocked dependencies"""
    # Mock the state loading and directory creation
    def mock_load_state(self):
        return {'repos': {}, 'deployments': {}}
    
    def mock_ensure_directories(self):
        pass
    
    monkeypatch.setattr(LabManager, '_load_state', mock_load_state)
    monkeypatch.setattr(LabManager, '_ensure_directories', mock_ensure_directories)
    
    return LabManager(test_config, mock_git_ops, mock_clab_runner)


@pytest.fixture
def flask_app(test_config):
    """Create a Flask app for testing"""
    app = create_app(test_config=test_config)
    app.config['TESTING'] = True
    return app


@pytest.fixture
def flask_client(flask_app):
    """Create a Flask test client"""
    return flask_app.test_client()


@pytest.fixture
def app_context(flask_app):
    """Create and manage Flask application context"""
    with flask_app.app_context():
        yield flask_app


@pytest.fixture
def cli_client():
    """Create a CLI client for testing"""
    return LabCtlClient(api_url='http://localhost:5000')


@pytest.fixture
def sample_lab_metadata():
    """Sample lab metadata for testing"""
    return {
        "name": "Test BGP Lab",
        "id": "test-bgp-lab",
        "version": "1.0.0",
        "category": "Routing",
        "vendor": "Juniper",
        "difficulty": "Intermediate",
        "description": {
            "short": "Basic BGP configuration lab",
            "long": "A comprehensive lab for learning BGP fundamentals"
        },
        "requirements": {
            "memory_gb": 8,
            "cpu_cores": 4,
            "disk_gb": 20,
            "containerlab_version": ">=0.48.0"
        },
        "platform": "containerlab",
        "netbox": {
            "enabled": False,
            "prefix": "10.100.100.0/24",
            "site": "Lab Environment",
            "role": "Lab Device"
        },
        "tags": ["bgp", "routing", "juniper"],
        "repository": {
            "url": "git@github.com:user/test-bgp-lab.git",
            "branch": "main"
        }
    }


@pytest.fixture
def sample_repo_state():
    """Sample repository state for testing"""
    return {
        'test-bgp-lab': {
            'id': 'test-bgp-lab',
            'name': 'Test BGP Lab',
            'path': '/tmp/repos/test-bgp-lab',
            'url': 'git@github.com:user/test-bgp-lab.git',
            'metadata': {
                'name': 'Test BGP Lab',
                'version': '1.0.0',
                'category': 'Routing',
                'vendor': 'Juniper',
                'difficulty': 'Intermediate'
            }
        }
    }


@pytest.fixture
def sample_deployment_state():
    """Sample deployment state for testing"""
    return {
        'test-bgp-lab-deployment-1': {
            'deployment_id': 'test-bgp-lab-deployment-1',
            'lab_id': 'test-bgp-lab',
            'lab_name': 'Test BGP Lab',
            'version': '1.0.0',
            'deployed_at': '2024-12-01T14:30:22',
            'status': 'running'
        }
    }


# Marks for pytest
def pytest_configure(config):
    """Configure pytest marks"""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "requires_git: Tests requiring git")
    config.addinivalue_line("markers", "requires_containerlab: Tests requiring containerlab")


# Collection hooks
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on file location"""
    for item in items:
        # Add markers based on test file location
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
            item.add_marker(pytest.mark.slow)
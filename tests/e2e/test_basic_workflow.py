#!/usr/bin/env python3
"""
Basic end-to-end workflow test
"""
import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock

# Add src to path for testing
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.backend.app import create_app
from src.cli.client import LabCtlClient


class TestBasicWorkflow(unittest.TestCase):
    """Test basic end-to-end workflow"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.temp_dir = Path(tempfile.mkdtemp())
        cls.repos_dir = cls.temp_dir / 'repos'
        cls.logs_dir = cls.temp_dir / 'logs'
        cls.state_file = cls.temp_dir / 'state.json'
        
        cls.repos_dir.mkdir()
        cls.logs_dir.mkdir()
        
        cls.test_config = {
            'repos_dir': str(cls.repos_dir),
            'logs_dir': str(cls.logs_dir),
            'state_file': str(cls.state_file),
            'git_cmd': 'git',
            'clab_tools_cmd': 'clab-tools'
        }
        
        # Create Flask app
        cls.app = create_app(test_config=cls.test_config)
        cls.app.config['TESTING'] = True
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        
        # Create CLI client
        cls.client = LabCtlClient(api_url='http://localhost:5000')
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        cls.app_context.pop()
        shutil.rmtree(cls.temp_dir)
    
    def test_app_initialization(self):
        """Test that both backend and CLI can be initialized"""
        # Test backend app
        with self.app.test_client() as client:
            response = client.get('/api/health')
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertEqual(data['status'], 'healthy')
        
        # Test CLI client
        self.assertIsNotNone(self.client)
        self.assertEqual(self.client.api_url, 'http://localhost:5000')
    
    def test_module_imports(self):
        """Test that all core modules can be imported"""
        # Test backend modules
        from src.backend.core.lab_manager import LabManager
        from src.backend.core.git_ops import GitOperations
        from src.backend.core.clab_runner import ClabRunner
        from src.backend.core.config import load_config
        
        # Test API modules
        from src.backend.api import repos_bp, labs_bp, tasks_bp, health_bp
        
        # Test CLI modules
        from src.cli.commands import repo, lab_commands, config, system_commands
        
        # All imports successful
        self.assertTrue(True)
    
    def test_empty_repo_list(self):
        """Test listing repos when none exist"""
        with self.app.test_client() as client:
            response = client.get('/api/repos')
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertEqual(data, [])
    
    def test_mock_repo_workflow(self):
        """Test a complete workflow with mocked operations"""
        # Mock the lab_manager directly since it's more reliable
        with self.app.test_client() as client:
            # Mock the add_repo method
            self.app.lab_manager.add_repo = Mock(return_value={
                'success': True,
                'lab_id': 'lab',
                'metadata': {'name': 'Test Lab'}
            })
            
            # Mock list_repos method
            self.app.lab_manager.list_repos = Mock(return_value=[{
                'id': 'lab',
                'name': 'Test Lab',
                'version': '1.0.0',
                'url': 'https://github.com/test/lab.git'
            }])
            
            # Add a repo
            response = client.post('/api/repos', json={
                'url': 'https://github.com/test/lab.git'
            })
            self.assertEqual(response.status_code, 201)
            data = response.get_json()
            self.assertTrue(data['success'])
            
            # List repos
            response = client.get('/api/repos')
            self.assertEqual(response.status_code, 200)
            repos = response.get_json()
            self.assertEqual(len(repos), 1)
            self.assertEqual(repos[0]['id'], 'lab')


if __name__ == '__main__':
    unittest.main()
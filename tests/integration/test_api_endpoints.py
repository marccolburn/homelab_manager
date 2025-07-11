"""
Integration tests for API endpoints
"""
import unittest
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock

# Add src to path for testing
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.backend.app import create_app
from src.backend.core.config import load_config


class TestAPIEndpoints(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Set up test class with Flask app"""
        # Create temporary directories for testing
        cls.temp_dir = Path(tempfile.mkdtemp())
        cls.repos_dir = cls.temp_dir / 'repos'
        cls.logs_dir = cls.temp_dir / 'logs'
        cls.state_file = cls.temp_dir / 'state.json'
        
        cls.repos_dir.mkdir()
        cls.logs_dir.mkdir()
        
        # Create test config
        cls.test_config = {
            'repos_dir': str(cls.repos_dir),
            'logs_dir': str(cls.logs_dir),
            'state_file': str(cls.state_file),
            'git_cmd': 'git',
            'clab_tools_cmd': 'clab-tools'
        }
        
        # Create app with test config
        cls.app = create_app(test_config=cls.test_config)
        cls.app.config['TESTING'] = True
        cls.client = cls.app.test_client()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test directories"""
        shutil.rmtree(cls.temp_dir)
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = self.client.get('/api/health')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['service'], 'labctl-backend')
    
    def test_list_repos_empty(self):
        """Test listing repositories when none exist"""
        response = self.client.get('/api/repos')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data, [])
    
    def test_add_repo_missing_url(self):
        """Test adding repository without URL"""
        response = self.client.post('/api/repos', 
                                  json={},
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('Repository URL required', data['error'])
    
    def test_add_repo_success(self):
        """Test successful repository addition"""
        with self.app.app_context():
            # Mock the lab_manager method directly
            self.app.lab_manager.add_repo = Mock(return_value={
                'success': True,
                'lab_id': 'test-lab',
                'metadata': {'name': 'Test Lab'}
            })
            
            response = self.client.post('/api/repos',
                                      json={'url': 'https://github.com/test/repo.git'},
                                      content_type='application/json')
            
            self.assertEqual(response.status_code, 201)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(data['lab_id'], 'test-lab')
    
    def test_add_repo_failure(self):
        """Test failed repository addition"""
        with self.app.app_context():
            self.app.lab_manager.add_repo = Mock(return_value={
                'success': False,
                'error': 'Git clone failed'
            })
            
            response = self.client.post('/api/repos',
                                      json={'url': 'https://github.com/test/repo.git'},
                                      content_type='application/json')
            
            self.assertEqual(response.status_code, 400)
            data = json.loads(response.data)
            self.assertFalse(data['success'])
            self.assertIn('error', data)
    
    def test_update_repo(self):
        """Test repository update"""
        with self.app.app_context():
            self.app.lab_manager.update_repo = Mock(return_value={
                'success': True,
                'message': 'Repository updated'
            })
            
            response = self.client.put('/api/repos/test-lab')
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(data['message'], 'Repository updated')
    
    def test_deploy_lab(self):
        """Test lab deployment"""
        with self.app.app_context():
            self.app.lab_manager.deploy_lab_async = Mock(return_value='task-123')
            
            response = self.client.post('/api/labs/test-lab/deploy',
                                      json={'version': 'latest'},
                                      content_type='application/json')
            
            self.assertEqual(response.status_code, 202)
            data = json.loads(response.data)
            self.assertEqual(data['task_id'], 'task-123')
            self.assertIn('Deployment of test-lab started', data['message'])
    
    def test_get_deployments(self):
        """Test getting deployments"""
        with self.app.app_context():
            self.app.lab_manager.get_status = Mock(return_value={
                'deployments': [
                    {
                        'deployment_id': 'test-lab_20230101_120000',
                        'lab_id': 'test-lab',
                        'lab_name': 'Test Lab',
                        'version': '1.0.0',
                        'deployed_at': '2023-01-01T12:00:00'
                    }
                ],
                'total': 1
            })
            
            response = self.client.get('/api/deployments')
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(data['total'], 1)
            self.assertEqual(len(data['deployments']), 1)
            self.assertEqual(data['deployments'][0]['lab_id'], 'test-lab')
    
    def test_get_task_status(self):
        """Test getting task status"""
        with self.app.app_context():
            self.app.lab_manager.get_task_status = Mock(return_value={
                'status': 'completed',
                'result': {'success': True, 'message': 'Lab deployed'}
            })
            
            response = self.client.get('/api/tasks/task-123')
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(data['status'], 'completed')
            self.assertTrue(data['result']['success'])
    
    def test_get_task_status_not_found(self):
        """Test getting status of non-existent task"""
        with self.app.app_context():
            self.app.lab_manager.get_task_status = Mock(return_value={'error': 'Task not found'})
            
            response = self.client.get('/api/tasks/nonexistent')
            
            self.assertEqual(response.status_code, 404)
            data = json.loads(response.data)
            self.assertIn('error', data)


if __name__ == '__main__':
    unittest.main()
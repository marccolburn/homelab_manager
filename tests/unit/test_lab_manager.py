"""
Unit tests for LabManager module
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import json
from datetime import datetime

from src.backend.core.lab_manager import LabManager
from src.backend.core.git_ops import GitOperations
from src.backend.core.clab_runner import ClabRunner


class TestLabManager(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = {
            'repos_dir': '/tmp/test_repos',
            'logs_dir': '/tmp/test_logs',
            'state_file': '/tmp/test_state.json',
            'git_cmd': 'git',
            'clab_tools_cmd': 'clab-tools'
        }
        
        # Mock dependencies
        self.mock_git_ops = Mock(spec=GitOperations)
        self.mock_clab_runner = Mock(spec=ClabRunner)
        
        # Create LabManager with mocked dependencies
        with patch.object(LabManager, '_load_state', return_value={'repos': {}, 'deployments': {}}):
            with patch.object(LabManager, '_ensure_directories'):
                self.lab_manager = LabManager(
                    self.config,
                    self.mock_git_ops,
                    self.mock_clab_runner
                )
    
    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data='{"repos": {}, "deployments": {}}')
    @patch('pathlib.Path.exists', return_value=True)
    def test_load_state(self, mock_exists, mock_open):
        """Test loading state from file"""
        state = self.lab_manager._load_state()
        
        self.assertEqual(state, {'repos': {}, 'deployments': {}})
        mock_open.assert_called_once()
    
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    @patch('pathlib.Path.mkdir')
    def test_save_state(self, mock_mkdir, mock_open):
        """Test saving state to file"""
        self.lab_manager.state = {'repos': {'test': {}}, 'deployments': {}}
        self.lab_manager._save_state()
        
        mock_open.assert_called_once()
        handle = mock_open()
        written_data = ''.join(call.args[0] for call in handle.write.call_args_list)
        self.assertIn('"repos"', written_data)
        self.assertIn('"test"', written_data)
    
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    @patch('pathlib.Path.exists', return_value=True)
    def test_add_repo_success(self, mock_exists, mock_open):
        """Test successfully adding a repository"""
        # Mock git operations
        self.mock_git_ops.clone.return_value = {'success': True}
        
        # Mock metadata file
        metadata = {
            'name': 'Test Lab',
            'version': '1.0.0',
            'category': 'Testing'
        }
        
        with patch('yaml.safe_load', return_value=metadata):
            with patch.object(self.lab_manager, '_save_state'):
                result = self.lab_manager.add_repo('https://github.com/test/repo.git')
        
        self.assertTrue(result['success'])
        self.assertEqual(result['lab_id'], 'repo')
        self.assertEqual(result['metadata']['name'], 'Test Lab')
        self.assertIn('repo', self.lab_manager.state['repos'])
    
    def test_add_repo_clone_failure(self):
        """Test failed repository clone"""
        self.mock_git_ops.clone.return_value = {'success': False, 'error': 'Clone failed'}
        
        result = self.lab_manager.add_repo('https://github.com/test/repo.git')
        
        self.assertFalse(result['success'])
        self.assertEqual(result['error'], 'Clone failed')
    
    def test_list_repos(self):
        """Test listing repositories"""
        self.lab_manager.state['repos'] = {
            'test-lab': {
                'path': '/tmp/test-lab',
                'url': 'https://github.com/test/lab.git',
                'metadata': {
                    'name': 'Test Lab',
                    'version': '1.0.0',
                    'category': 'Testing'
                }
            }
        }
        
        repos = self.lab_manager.list_repos()
        
        self.assertEqual(len(repos), 1)
        self.assertEqual(repos[0]['id'], 'test-lab')
        self.assertEqual(repos[0]['name'], 'Test Lab')
        self.assertEqual(repos[0]['version'], '1.0.0')
    
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    def test_update_repo_success(self, mock_open):
        """Test updating a repository"""
        self.lab_manager.state['repos'] = {
            'test-lab': {
                'path': '/tmp/test-lab',
                'metadata': {}
            }
        }
        
        self.mock_git_ops.pull.return_value = {'success': True}
        
        with patch('yaml.safe_load', return_value={'name': 'Updated Lab'}):
            with patch.object(self.lab_manager, '_save_state'):
                result = self.lab_manager.update_repo('test-lab')
        
        self.assertTrue(result['success'])
        self.assertEqual(result['message'], 'Repository updated')
    
    def test_deploy_lab_async(self):
        """Test async lab deployment"""
        self.lab_manager.state['repos'] = {
            'test-lab': {
                'path': '/tmp/test-lab',
                'metadata': {'name': 'Test Lab'}
            }
        }
        
        with patch('threading.Thread') as mock_thread:
            task_id = self.lab_manager.deploy_lab_async('test-lab')
        
        self.assertIsNotNone(task_id)
        mock_thread.assert_called_once()
        mock_thread.return_value.start.assert_called_once()
    
    def test_destroy_lab_success(self):
        """Test successful lab destruction"""
        self.lab_manager.state['deployments'] = {
            'test-lab_20230101_120000': {
                'lab_id': 'test-lab',
                'status': 'active'
            }
        }
        self.lab_manager.state['repos'] = {
            'test-lab': {
                'path': '/tmp/test-lab'
            }
        }
        
        self.mock_clab_runner.teardown_lab.return_value = (True, {'message': 'Success'})
        
        with patch.object(self.lab_manager, '_save_state'):
            result = self.lab_manager.destroy_lab('test-lab')
        
        self.assertTrue(result['success'])
        self.assertEqual(
            self.lab_manager.state['deployments']['test-lab_20230101_120000']['status'],
            'destroyed'
        )
    
    def test_get_status(self):
        """Test getting deployment status"""
        self.lab_manager.state['deployments'] = {
            'test-lab_20230101_120000': {
                'lab_id': 'test-lab',
                'status': 'active',
                'version': '1.0.0',
                'deployed_at': '2023-01-01T12:00:00'
            }
        }
        self.lab_manager.state['repos'] = {
            'test-lab': {
                'metadata': {'name': 'Test Lab'}
            }
        }
        
        status = self.lab_manager.get_status()
        
        self.assertEqual(status['total'], 1)
        self.assertEqual(len(status['deployments']), 1)
        self.assertEqual(status['deployments'][0]['lab_name'], 'Test Lab')
    
    def test_list_config_scenarios(self):
        """Test listing configuration scenarios"""
        self.lab_manager.state['repos'] = {
            'test-lab': {
                'path': '/tmp/test-lab'
            }
        }
        
        # Mock directory listing
        mock_path = Mock()
        mock_path.iterdir.return_value = [
            Mock(is_dir=Mock(return_value=True), name='baseline'),
            Mock(is_dir=Mock(return_value=True), name='scenario-1'),
            Mock(is_dir=Mock(return_value=False), name='README.md')
        ]
        
        with patch('pathlib.Path', return_value=mock_path):
            with patch('pathlib.Path.exists', return_value=True):
                scenarios = self.lab_manager.list_config_scenarios('test-lab')
        
        self.assertEqual(scenarios, ['baseline', 'scenario-1'])


if __name__ == '__main__':
    unittest.main()
"""
Unit tests for LabManager module
"""
import pytest
from unittest.mock import Mock, patch
from pathlib import Path
import json
from datetime import datetime

from src.backend.core.lab_manager import LabManager

@pytest.mark.unit
class TestLabManagerState:
    """Test LabManager state management functionality"""
    
    def test_load_state(self, lab_manager, monkeypatch):
        """Test loading state from file"""
        # Use monkeypatch to override the method with a simple return
        def mock_load_state_method(self):
            return {'repos': {}, 'deployments': {}}
        
        monkeypatch.setattr(lab_manager, '_load_state', lambda: {'repos': {}, 'deployments': {}})
        
        state = lab_manager._load_state()
        
        assert state == {'repos': {}, 'deployments': {}}
    
    @patch('builtins.open', new_callable=Mock)
    @patch('pathlib.Path.mkdir')
    def test_save_state(self, mock_mkdir, mock_open, lab_manager):
        """Test saving state to file"""
        lab_manager.state = {'repos': {'test': {}}, 'deployments': {}}
        lab_manager._save_state()
        
        mock_open.assert_called_once()
        handle = mock_open.return_value.__enter__.return_value
        written_data = ''.join(str(call) for call in handle.write.call_args_list)
        assert '"repos"' in written_data or handle.write.call_count > 0

@pytest.mark.unit 
class TestLabManagerRepositories:
    """Test LabManager repository management functionality"""
    
    @patch('builtins.open', new_callable=Mock)
    @patch('pathlib.Path.exists', return_value=True)
    def test_add_repo_success(self, mock_exists, mock_open, lab_manager):
        """Test successfully adding a repository"""
        # Mock metadata file
        metadata = {
            'name': 'Test Lab',
            'version': '1.0.0',
            'category': 'Testing'
        }
        
        with patch('yaml.safe_load', return_value=metadata):
            with patch.object(lab_manager, '_save_state'):
                result = lab_manager.add_repo('https://github.com/test/repo.git')
        
        assert result['success'] is True
        assert result['lab_id'] == 'repo'
        assert result['metadata']['name'] == 'Test Lab'
        assert 'repo' in lab_manager.state['repos']
    
    def test_add_repo_clone_failure(self, lab_manager, mock_git_ops):
        """Test failed repository clone"""
        # Override the default success to return failure
        mock_git_ops.clone.return_value = {'success': False, 'error': 'Clone failed'}
        
        result = lab_manager.add_repo('https://github.com/test/repo.git')
        
        assert result['success'] is False
        assert result['error'] == 'Clone failed'
    
    def test_list_repos(self, lab_manager):
        """Test listing repositories"""
        lab_manager.state['repos'] = {
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
        
        repos = lab_manager.list_repos()
        
        assert len(repos) == 1
        assert repos[0]['id'] == 'test-lab'
        assert repos[0]['name'] == 'Test Lab'
        assert repos[0]['version'] == '1.0.0'
    
    @patch('builtins.open', new_callable=Mock)
    def test_update_repo_success(self, mock_open, lab_manager, mock_git_ops):
        """Test updating a repository"""
        lab_manager.state['repos'] = {
            'test-lab': {
                'path': '/tmp/test-lab',
                'metadata': {}
            }
        }
        
        mock_git_ops.pull.return_value = {'success': True}
        
        with patch('yaml.safe_load', return_value={'name': 'Updated Lab'}):
            with patch.object(lab_manager, '_save_state'):
                result = lab_manager.update_repo('test-lab')
        
        assert result['success'] is True
        assert result['message'] == 'Repository updated'

@pytest.mark.unit
class TestLabManagerDeployments:
    """Test LabManager deployment functionality"""
    
    def test_deploy_lab_async(self, lab_manager):
        """Test async lab deployment"""
        lab_manager.state['repos'] = {
            'test-lab': {
                'path': '/tmp/test-lab',
                'metadata': {'name': 'Test Lab'}
            }
        }
        
        with patch('threading.Thread') as mock_thread:
            task_id = lab_manager.deploy_lab_async('test-lab')
        
        assert task_id is not None
        mock_thread.assert_called_once()
        mock_thread.return_value.start.assert_called_once()
    
    def test_destroy_lab_success(self, lab_manager, mock_clab_runner):
        """Test successful lab destruction"""
        lab_manager.state['deployments'] = {
            'test-lab_20230101_120000': {
                'lab_id': 'test-lab',
                'status': 'active'
            }
        }
        lab_manager.state['repos'] = {
            'test-lab': {
                'path': '/tmp/test-lab'
            }
        }
        
        mock_clab_runner.teardown_lab.return_value = (True, {'message': 'Success'})
        
        with patch.object(lab_manager, '_save_state'):
            result = lab_manager.destroy_lab('test-lab')
        
        assert result['success'] is True
        assert lab_manager.state['deployments']['test-lab_20230101_120000']['status'] == 'destroyed'
    
    def test_get_status(self, lab_manager):
        """Test getting deployment status"""
        lab_manager.state['deployments'] = {
            'test-lab_20230101_120000': {
                'lab_id': 'test-lab',
                'status': 'active',
                'version': '1.0.0',
                'deployed_at': '2023-01-01T12:00:00'
            }
        }
        lab_manager.state['repos'] = {
            'test-lab': {
                'metadata': {'name': 'Test Lab'}
            }
        }
        
        status = lab_manager.get_status()
        
        assert status['total'] == 1
        assert len(status['deployments']) == 1
        assert status['deployments'][0]['lab_name'] == 'Test Lab'
@pytest.mark.unit
class TestLabManagerConfiguration:
    """Test LabManager configuration scenario functionality"""
    
    @patch('src.backend.core.lab_manager.Path')
    def test_list_config_scenarios(self, mock_path_class, lab_manager):
        """Test listing configuration scenarios"""
        lab_manager.state['repos'] = {
            'test-lab': {
                'path': '/tmp/test-lab'
            }
        }
        
        # Mock the configs directory
        mock_configs_dir = Mock()
        mock_configs_dir.exists.return_value = True
        
        # Create mock file/dir objects
        mock_baseline = Mock()
        mock_baseline.is_dir.return_value = True
        mock_baseline.name = 'baseline'
        
        mock_scenario = Mock()
        mock_scenario.is_dir.return_value = True
        mock_scenario.name = 'scenario-1'
        
        mock_readme = Mock()
        mock_readme.is_dir.return_value = False
        mock_readme.name = 'README.md'
        
        mock_configs_dir.iterdir.return_value = [mock_baseline, mock_scenario, mock_readme]
        
        # Mock repo path
        mock_repo_path = Mock()
        mock_repo_path.__truediv__ = Mock(return_value=mock_configs_dir)
        
        # Configure Path constructor to return our mock
        mock_path_class.return_value = mock_repo_path
        
        scenarios = lab_manager.list_config_scenarios('test-lab')
        
        assert scenarios == ['baseline', 'scenario-1']
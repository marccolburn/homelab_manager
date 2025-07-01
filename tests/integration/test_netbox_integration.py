"""
Integration tests for NetBox with LabManager
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import shutil
import csv

from src.backend.core.lab_manager import LabManager
from src.backend.core.git_ops import GitOperations
from src.backend.core.clab_runner import ClabRunner
from src.backend.integrations.netbox import NetBoxManager


@pytest.mark.integration
class TestNetBoxLabManagerIntegration:
    """Test NetBox integration with LabManager"""
    
    @pytest.fixture
    def temp_lab_repo(self):
        """Create a temporary lab repository"""
        temp_dir = Path(tempfile.mkdtemp())
        
        # Create lab structure
        (temp_dir / "clab_tools_files").mkdir()
        
        # Create nodes.csv
        nodes_file = temp_dir / "clab_tools_files" / "nodes.csv"
        with open(nodes_file, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=['hostname', 'platform', 'type'])
            writer.writeheader()
            writer.writerows([
                {'hostname': 'r1', 'platform': 'juniper', 'type': 'router'},
                {'hostname': 'r2', 'platform': 'juniper', 'type': 'router'},
                {'hostname': 'sw1', 'platform': 'arista', 'type': 'switch'}
            ])
        
        # Create lab-metadata.yaml
        metadata_file = temp_dir / "lab-metadata.yaml"
        with open(metadata_file, 'w') as f:
            f.write("""
name: Test Lab
id: test-lab
version: 1.0.0
category: Testing
vendor: Generic
difficulty: Easy
""")
        
        yield temp_dir
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def mock_netbox_manager(self):
        """Create mock NetBox manager"""
        mock = Mock(spec=NetBoxManager)
        mock.enabled = True
        mock.allocate_ips.return_value = {
            'r1': '10.100.100.1',
            'r2': '10.100.100.2', 
            'sw1': '10.100.100.3'
        }
        mock.update_nodes_csv.return_value = True
        mock.register_devices.return_value = ['test-lab-r1', 'test-lab-r2', 'test-lab-sw1']
        mock.release_ips.return_value = True
        mock.unregister_devices.return_value = True
        mock.validate_config.return_value = (True, [])
        return mock
    
    @pytest.fixture
    def lab_manager_with_netbox(self, test_config, mock_git_ops, mock_clab_runner, 
                               mock_netbox_manager, monkeypatch):
        """Create LabManager with NetBox integration"""
        # Mock state loading
        def mock_load_state(self):
            return {
                'repos': {
                    'test-lab': {
                        'id': 'test-lab',
                        'name': 'Test Lab',
                        'path': '/tmp/test-lab',
                        'metadata': {'name': 'Test Lab'}
                    }
                },
                'deployments': {}
            }
        
        def mock_ensure_directories(self):
            pass
        
        monkeypatch.setattr(LabManager, '_load_state', mock_load_state)
        monkeypatch.setattr(LabManager, '_ensure_directories', mock_ensure_directories)
        
        # Create LabManager with mocked NetBox
        manager = LabManager(test_config, mock_git_ops, mock_clab_runner, mock_netbox_manager)
        return manager
    
    def test_deploy_with_ip_allocation(self, lab_manager_with_netbox, mock_clab_runner, 
                                      mock_netbox_manager, temp_lab_repo, monkeypatch):
        """Test lab deployment with NetBox IP allocation"""
        # Update lab manager state with correct path
        lab_manager_with_netbox.state['repos']['test-lab']['path'] = str(temp_lab_repo)
        
        # Mock successful deployment
        mock_clab_runner.bootstrap_lab.return_value = (True, {
            'message': 'Deployment successful',
            'log_file': '/tmp/test.log'
        })
        
        # Mock save state
        monkeypatch.setattr(lab_manager_with_netbox, '_save_state', Mock())
        
        # Deploy with IP allocation
        result = lab_manager_with_netbox._deploy_lab('test-lab', 'latest', allocate_ips=True)
        
        # Verify success
        assert result['success'] is True
        assert 'deployment_id' in result
        
        # Verify NetBox methods were called
        mock_netbox_manager.allocate_ips.assert_called_once_with('test-lab', ['r1', 'r2', 'sw1'])
        mock_netbox_manager.update_nodes_csv.assert_called_once()
        mock_netbox_manager.register_devices.assert_called_once()
        
        # Verify deployment state includes NetBox info
        deployments = lab_manager_with_netbox.state['deployments']
        assert len(deployments) == 1
        deployment = list(deployments.values())[0]
        assert deployment['netbox_ips_allocated'] is True
        assert deployment['ip_assignments'] == {
            'r1': '10.100.100.1',
            'r2': '10.100.100.2',
            'sw1': '10.100.100.3'
        }
    
    def test_deploy_with_allocation_failure(self, lab_manager_with_netbox, mock_netbox_manager, 
                                          temp_lab_repo):
        """Test deployment when IP allocation fails"""
        # Update lab manager state with correct path
        lab_manager_with_netbox.state['repos']['test-lab']['path'] = str(temp_lab_repo)
        
        # Mock allocation failure
        mock_netbox_manager.allocate_ips.return_value = {}
        
        # Attempt deployment
        result = lab_manager_with_netbox._deploy_lab('test-lab', 'latest', allocate_ips=True)
        
        # Verify failure
        assert result['success'] is False
        assert 'Failed to allocate IPs' in result['error']
    
    def test_deploy_rollback_on_failure(self, lab_manager_with_netbox, mock_clab_runner,
                                       mock_netbox_manager, temp_lab_repo, monkeypatch):
        """Test IP rollback when deployment fails after allocation"""
        # Update lab manager state with correct path
        lab_manager_with_netbox.state['repos']['test-lab']['path'] = str(temp_lab_repo)
        
        # Mock deployment failure
        mock_clab_runner.bootstrap_lab.return_value = (False, {
            'error': 'Deployment failed'
        })
        
        # Mock save state
        monkeypatch.setattr(lab_manager_with_netbox, '_save_state', Mock())
        
        # Attempt deployment
        result = lab_manager_with_netbox._deploy_lab('test-lab', 'latest', allocate_ips=True)
        
        # Verify failure and rollback
        assert result['success'] is False
        mock_netbox_manager.release_ips.assert_called_once_with('test-lab')
    
    def test_destroy_with_netbox_cleanup(self, lab_manager_with_netbox, mock_clab_runner,
                                        mock_netbox_manager, monkeypatch):
        """Test lab destruction with NetBox cleanup"""
        # Add active deployment with NetBox allocation
        lab_manager_with_netbox.state['deployments']['test-deployment'] = {
            'lab_id': 'test-lab',
            'status': 'active',
            'netbox_ips_allocated': True,
            'ip_assignments': {'r1': '10.100.100.1'}
        }
        
        # Mock successful teardown
        mock_clab_runner.teardown_lab.return_value = (True, {'message': 'Teardown successful'})
        
        # Mock save state
        monkeypatch.setattr(lab_manager_with_netbox, '_save_state', Mock())
        
        # Destroy lab
        result = lab_manager_with_netbox.destroy_lab('test-lab')
        
        # Verify success
        assert result['success'] is True
        
        # Verify NetBox cleanup was called
        mock_netbox_manager.release_ips.assert_called_once_with('test-lab')
        mock_netbox_manager.unregister_devices.assert_called_once_with('test-lab')
        
        # Verify deployment state updated
        assert lab_manager_with_netbox.state['deployments']['test-deployment']['status'] == 'destroyed'
    
    def test_destroy_without_netbox(self, lab_manager_with_netbox, mock_clab_runner,
                                   mock_netbox_manager, monkeypatch):
        """Test lab destruction when NetBox was not used"""
        # Add deployment without NetBox allocation
        lab_manager_with_netbox.state['deployments']['test-deployment'] = {
            'lab_id': 'test-lab',
            'status': 'active',
            'netbox_ips_allocated': False
        }
        
        # Mock successful teardown
        mock_clab_runner.teardown_lab.return_value = (True, {'message': 'Teardown successful'})
        
        # Mock save state
        monkeypatch.setattr(lab_manager_with_netbox, '_save_state', Mock())
        
        # Destroy lab
        result = lab_manager_with_netbox.destroy_lab('test-lab')
        
        # Verify success
        assert result['success'] is True
        
        # Verify NetBox cleanup was NOT called
        mock_netbox_manager.release_ips.assert_not_called()
        mock_netbox_manager.unregister_devices.assert_not_called()
    
    def test_validate_netbox_config(self, lab_manager_with_netbox, mock_netbox_manager):
        """Test NetBox configuration validation"""
        # Test validation
        result = lab_manager_with_netbox.validate_netbox_config()
        
        assert result['enabled'] is True
        assert result['valid'] is True
        assert result['message'] == 'NetBox configuration is valid'
        
        # Test with validation errors
        mock_netbox_manager.validate_config.return_value = (False, ['Error 1', 'Error 2'])
        result = lab_manager_with_netbox.validate_netbox_config()
        
        assert result['valid'] is False
        assert len(result['errors']) == 2
        assert 'NetBox configuration has errors' in result['message']
    
    def test_nodes_csv_update_verification(self, temp_lab_repo):
        """Test actual nodes.csv update functionality"""
        nodes_file = temp_lab_repo / "clab_tools_files" / "nodes.csv"
        
        # Create real NetBox manager (but mocked API)
        config = {'enabled': True}
        manager = NetBoxManager(config)
        
        # Update CSV
        ip_assignments = {
            'r1': '10.100.100.1',
            'r2': '10.100.100.2',
            'sw1': '10.100.100.3'
        }
        result = manager.update_nodes_csv(nodes_file, ip_assignments)
        
        assert result is True
        
        # Verify file contents
        with open(nodes_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        assert rows[0]['hostname'] == 'r1'
        assert rows[0]['mgmt_ip'] == '10.100.100.1'
        assert rows[1]['hostname'] == 'r2'
        assert rows[1]['mgmt_ip'] == '10.100.100.2'
        assert rows[2]['hostname'] == 'sw1'
        assert rows[2]['mgmt_ip'] == '10.100.100.3'
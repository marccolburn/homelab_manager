"""
End-to-end tests for NetBox integration workflow
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import shutil
import csv
import json

from src.backend.app import create_app
from src.cli.client import LabCtlClient


@pytest.mark.e2e
class TestNetBoxWorkflowE2E:
    """End-to-end NetBox integration workflow tests"""
    
    @pytest.fixture
    def netbox_config(self):
        """NetBox configuration for testing"""
        return {
            'enabled': True,
            'url': 'https://netbox.example.com',
            'token': 'test-token',
            'default_prefix': '10.100.100.0/24',
            'default_site': 'Lab Environment',
            'default_role': 'Lab Device'
        }
    
    @pytest.fixture
    def app_with_netbox(self, test_config, netbox_config):
        """Create Flask app with NetBox enabled"""
        test_config['netbox'] = netbox_config
        app = create_app(test_config=test_config)
        app.config['TESTING'] = True
        return app
    
    @pytest.fixture
    def test_lab_repo(self):
        """Create a complete test lab repository"""
        temp_dir = Path(tempfile.mkdtemp())
        
        # Create full lab structure
        clab_dir = temp_dir / "clab_tools_files"
        clab_dir.mkdir()
        
        # Create nodes.csv
        nodes_file = clab_dir / "nodes.csv"
        with open(nodes_file, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=['hostname', 'platform', 'type', 'mgmt_ip'])
            writer.writeheader()
            writer.writerows([
                {'hostname': 'spine1', 'platform': 'arista', 'type': 'switch', 'mgmt_ip': ''},
                {'hostname': 'spine2', 'platform': 'arista', 'type': 'switch', 'mgmt_ip': ''},
                {'hostname': 'leaf1', 'platform': 'arista', 'type': 'switch', 'mgmt_ip': ''},
                {'hostname': 'leaf2', 'platform': 'arista', 'type': 'switch', 'mgmt_ip': ''}
            ])
        
        # Create other required files
        (clab_dir / "connections.csv").touch()
        (clab_dir / "config.yaml").touch()
        (clab_dir / "bootstrap.sh").touch()
        (clab_dir / "teardown.sh").touch()
        
        # Create lab-metadata.yaml
        with open(temp_dir / "lab-metadata.yaml", 'w') as f:
            f.write("""
name: EVPN-VXLAN Spine-Leaf Lab
id: evpn-spine-leaf
version: 2.1.0
category: Data Center
vendor: Arista
difficulty: Advanced
description:
  short: EVPN-VXLAN spine-leaf topology
  long: Complete EVPN-VXLAN implementation with spine-leaf architecture
requirements:
  memory_gb: 16
  cpu_cores: 8
  disk_gb: 30
platform: containerlab
netbox:
  enabled: true
  prefix: "10.100.100.0/24"
tags:
  - evpn
  - vxlan
  - datacenter
""")
        
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_complete_netbox_deployment_workflow(self, app_with_netbox, test_lab_repo):
        """Test complete workflow: add repo, validate NetBox, deploy with IPs, destroy"""
        
        with app_with_netbox.app_context():
            # Setup mock NetBox API
            with patch('src.backend.integrations.netbox.pynetbox') as mock_pynetbox:
                with patch('src.backend.integrations.netbox.NETBOX_AVAILABLE', True):
                    # Configure mock NetBox API
                    mock_api = Mock()
                    mock_pynetbox.api.return_value = mock_api
                    mock_api.status.return_value = {'netbox-version': '3.5.0'}
                    
                    # Mock prefix
                    mock_prefix = Mock()
                    mock_prefix.available_ips.list.return_value = [
                        {'address': '10.100.100.10/24'},
                        {'address': '10.100.100.11/24'},
                        {'address': '10.100.100.12/24'},
                        {'address': '10.100.100.13/24'}
                    ]
                    mock_api.ipam.prefixes.get.return_value = mock_prefix
                    
                    # Mock IP creation
                    mock_ips = []
                    for i, addr in enumerate(['10.100.100.10/24', '10.100.100.11/24', 
                                            '10.100.100.12/24', '10.100.100.13/24']):
                        mock_ip = Mock()
                        mock_ip.address = addr
                        mock_ips.append(mock_ip)
                    mock_api.ipam.ip_addresses.create.side_effect = mock_ips
                    
                    # Mock device creation infrastructure
                    mock_site = Mock(id=1)
                    mock_role = Mock(id=2)
                    mock_device_type = Mock(id=3)
                    mock_manufacturer = Mock(id=4)
                    
                    mock_api.dcim.sites.get.return_value = mock_site
                    mock_api.dcim.device_roles.get.return_value = mock_role
                    mock_api.dcim.device_types.get.return_value = mock_device_type
                    mock_api.dcim.manufacturers.get.return_value = mock_manufacturer
                    mock_api.dcim.devices.get.return_value = None  # No existing devices
                    mock_api.dcim.devices.create.return_value = Mock(name='device')
                    
                    # Mock cleanup
                    mock_api.ipam.ip_addresses.filter.return_value = mock_ips
                    mock_api.dcim.devices.filter.return_value = [Mock(name='device1'), Mock(name='device2')]
                    
                    lab_manager = app_with_netbox.lab_manager
                    
                    # Step 1: Add lab repository - just add to state directly for testing
                    lab_manager.state['repos']['evpn-spine-leaf'] = {
                        'id': 'evpn-spine-leaf',
                        'name': 'EVPN-VXLAN Spine-Leaf Lab',
                        'path': str(test_lab_repo),
                        'url': f'file://{test_lab_repo}',
                        'metadata': {
                            'name': 'EVPN-VXLAN Spine-Leaf Lab',
                            'id': 'evpn-spine-leaf',
                            'version': '2.1.0'
                        }
                    }
                    
                    # Step 2: Validate NetBox configuration
                    validation_result = lab_manager.validate_netbox_config()
                    assert validation_result['enabled'] is True
                    assert validation_result['valid'] is True
                    
                    # Step 3: Deploy lab with IP allocation
                    with patch.object(lab_manager.clab_runner, 'bootstrap_lab') as mock_bootstrap:
                        mock_bootstrap.return_value = (True, {
                            'message': 'Lab deployed successfully',
                            'log_file': '/tmp/deployment.log'
                        })
                        
                        # Deploy with NetBox IPs
                        deploy_result = lab_manager._deploy_lab('evpn-spine-leaf', 'latest', allocate_ips=True)
                        
                        assert deploy_result['success'] is True
                        assert 'deployment_id' in deploy_result
                        
                        # Verify deployment state includes NetBox info
                        deployment_id = deploy_result['deployment_id']
                        deployment_info = lab_manager.state['deployments'][deployment_id]
                        assert deployment_info['netbox_ips_allocated'] is True
                        assert len(deployment_info['ip_assignments']) == 4
                        
                        # Verify nodes.csv was updated
                        nodes_file = test_lab_repo / "clab_tools_files" / "nodes.csv"
                        with open(nodes_file, 'r') as f:
                            reader = csv.DictReader(f)
                            nodes = list(reader)
                        
                        # Check that IPs were assigned
                        ip_assigned_count = sum(1 for node in nodes if node['mgmt_ip'])
                        assert ip_assigned_count == 4
                    
                    # Step 4: Check deployment status
                    status = lab_manager.get_status()
                    assert status['total'] == 1
                    assert len(status['deployments']) == 1
                    
                    # Step 5: Destroy lab (should clean up NetBox resources)
                    with patch.object(lab_manager.clab_runner, 'teardown_lab') as mock_teardown:
                        mock_teardown.return_value = (True, {'message': 'Lab destroyed successfully'})
                        
                        destroy_result = lab_manager.destroy_lab('evpn-spine-leaf')
                        
                        assert destroy_result['success'] is True
                        
                        # Verify NetBox cleanup was called
                        # IPs should be deleted
                        for mock_ip in mock_ips:
                            mock_ip.delete.assert_called_once()
                        
                        # Devices should be deleted
                        for device in mock_api.dcim.devices.filter.return_value:
                            device.delete.assert_called_once()
    
    def test_netbox_allocation_failure_recovery(self, app_with_netbox, test_lab_repo):
        """Test recovery when NetBox IP allocation fails"""
        
        with app_with_netbox.app_context():
            with patch('src.backend.integrations.netbox.pynetbox') as mock_pynetbox:
                with patch('src.backend.integrations.netbox.NETBOX_AVAILABLE', True):
                    # Configure mock NetBox API
                    mock_api = Mock()
                    mock_pynetbox.api.return_value = mock_api
                    mock_api.status.return_value = {'netbox-version': '3.5.0'}
                    
                    # Mock prefix with insufficient IPs
                    mock_prefix = Mock()
                    mock_prefix.available_ips.list.return_value = [
                        {'address': '10.100.100.10/24'}  # Only 1 IP for 4 nodes
                    ]
                    mock_api.ipam.prefixes.get.return_value = mock_prefix
                    
                    lab_manager = app_with_netbox.lab_manager
                    
                    # Add repo to state
                    lab_manager.state['repos']['evpn-spine-leaf'] = {
                        'id': 'evpn-spine-leaf',
                        'name': 'EVPN-VXLAN Spine-Leaf Lab',
                        'path': str(test_lab_repo),
                        'metadata': {'name': 'EVPN-VXLAN Spine-Leaf Lab'}
                    }
                    
                    # Attempt deployment with insufficient IPs
                    deploy_result = lab_manager._deploy_lab('evpn-spine-leaf', 'latest', allocate_ips=True)
                    
                    # Should fail due to insufficient IPs
                    assert deploy_result['success'] is False
                    assert 'Failed to allocate IPs' in deploy_result['error']
                    
                    # Verify no deployments were created
                    assert len(lab_manager.state['deployments']) == 0
    
    def test_netbox_deployment_with_api_integration(self, app_with_netbox, test_lab_repo):
        """Test NetBox deployment through API endpoints"""
        
        client = app_with_netbox.test_client()
        
        with app_with_netbox.app_context():
            with patch('src.backend.integrations.netbox.pynetbox') as mock_pynetbox:
                with patch('src.backend.integrations.netbox.NETBOX_AVAILABLE', True):
                    # Setup NetBox mocking
                    mock_api = Mock()
                    mock_pynetbox.api.return_value = mock_api
                    mock_api.status.return_value = {'netbox-version': '3.5.0'}
                    mock_api.ipam.prefixes.get.return_value = Mock()
                    
                    lab_manager = app_with_netbox.lab_manager
                    
                    # Add repo to state
                    lab_manager.state['repos']['evpn-spine-leaf'] = {
                        'id': 'evpn-spine-leaf',
                        'name': 'EVPN-VXLAN Spine-Leaf Lab',
                        'path': str(test_lab_repo),
                        'metadata': {'name': 'EVPN-VXLAN Spine-Leaf Lab'}
                    }
                    
                    # Test NetBox validation endpoint
                    response = client.get('/api/netbox/validate')
                    assert response.status_code == 200
                    data = response.get_json()
                    assert data['enabled'] is True
                    
                    # Test deployment with allocate_ips through API
                    with patch.object(lab_manager, 'deploy_lab_async') as mock_deploy:
                        mock_deploy.return_value = 'task-123'
                        
                        response = client.post('/api/labs/evpn-spine-leaf/deploy',
                                             json={'allocate_ips': True, 'version': 'latest'})
                        
                        assert response.status_code == 202
                        data = response.get_json()
                        assert data['task_id'] == 'task-123'
                        
                        # Verify allocate_ips was passed correctly
                        mock_deploy.assert_called_once_with('evpn-spine-leaf', 'latest', True)
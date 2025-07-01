"""
Unit tests for NetBox integration module
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import csv
import tempfile

from src.backend.integrations.netbox import NetBoxManager


@pytest.mark.unit
class TestNetBoxManager:
    """Test NetBox integration functionality"""
    
    @pytest.fixture
    def netbox_config(self):
        """Sample NetBox configuration"""
        return {
            'enabled': True,
            'url': 'https://netbox.example.com',
            'token': 'test-token',
            'default_prefix': '10.100.100.0/24',
            'default_site': 'Lab Environment',
            'default_role': 'Lab Device'
        }
    
    @pytest.fixture
    def mock_pynetbox(self):
        """Mock pynetbox module"""
        with patch('src.backend.integrations.netbox.pynetbox') as mock:
            # Mock API object
            mock_api = Mock()
            mock.api.return_value = mock_api
            
            # Mock status endpoint
            mock_api.status.return_value = {'netbox-version': '3.5.0'}
            
            yield mock_api
    
    @pytest.fixture
    def netbox_manager(self, netbox_config, mock_pynetbox):
        """Create NetBoxManager with mocked pynetbox"""
        with patch('src.backend.integrations.netbox.NETBOX_AVAILABLE', True):
            manager = NetBoxManager(netbox_config)
            manager._api = mock_pynetbox
            return manager
    
    def test_init_enabled(self, netbox_config):
        """Test NetBox manager initialization when enabled"""
        with patch('src.backend.integrations.netbox.NETBOX_AVAILABLE', True):
            manager = NetBoxManager(netbox_config)
            assert manager.enabled is True
            assert manager.config == netbox_config
    
    def test_init_disabled(self):
        """Test NetBox manager initialization when disabled"""
        config = {'enabled': False}
        manager = NetBoxManager(config)
        assert manager.enabled is False
    
    def test_init_no_pynetbox(self, netbox_config):
        """Test initialization when pynetbox is not available"""
        with patch('src.backend.integrations.netbox.NETBOX_AVAILABLE', False):
            manager = NetBoxManager(netbox_config)
            assert manager.enabled is False
    
    def test_allocate_ips_success(self, netbox_manager, mock_pynetbox):
        """Test successful IP allocation"""
        # Mock prefix lookup
        mock_prefix = Mock()
        mock_pynetbox.ipam.prefixes.get.return_value = mock_prefix
        
        # Mock available IPs
        available_ips = [
            {'address': '10.100.100.1/24'},
            {'address': '10.100.100.2/24'},
            {'address': '10.100.100.3/24'}
        ]
        mock_prefix.available_ips.list.return_value = available_ips
        
        # Mock IP creation
        mock_ip_objects = []
        for ip in available_ips:
            mock_ip = Mock()
            mock_ip.address = ip['address']
            mock_ip_objects.append(mock_ip)
        mock_pynetbox.ipam.ip_addresses.create.side_effect = mock_ip_objects
        
        # Test allocation
        nodes = ['node1', 'node2', 'node3']
        result = netbox_manager.allocate_ips('test-lab', nodes)
        
        assert len(result) == 3
        assert result['node1'] == '10.100.100.1'
        assert result['node2'] == '10.100.100.2'
        assert result['node3'] == '10.100.100.3'
        
        # Verify IP creation calls
        assert mock_pynetbox.ipam.ip_addresses.create.call_count == 3
    
    def test_allocate_ips_insufficient(self, netbox_manager, mock_pynetbox):
        """Test allocation failure when not enough IPs available"""
        # Mock prefix lookup
        mock_prefix = Mock()
        mock_pynetbox.ipam.prefixes.get.return_value = mock_prefix
        
        # Mock insufficient available IPs
        available_ips = [{'address': '10.100.100.1/24'}]
        mock_prefix.available_ips.list.return_value = available_ips
        
        # Test allocation
        nodes = ['node1', 'node2', 'node3']
        result = netbox_manager.allocate_ips('test-lab', nodes)
        
        assert result == {}
    
    def test_allocate_ips_rollback(self, netbox_manager, mock_pynetbox):
        """Test IP allocation rollback on failure"""
        # Mock prefix lookup
        mock_prefix = Mock()
        mock_pynetbox.ipam.prefixes.get.return_value = mock_prefix
        
        # Mock available IPs
        available_ips = [
            {'address': '10.100.100.1/24'},
            {'address': '10.100.100.2/24'}
        ]
        mock_prefix.available_ips.list.return_value = available_ips
        
        # Mock IP creation - second one fails
        mock_ip1 = Mock()
        mock_ip1.address = '10.100.100.1/24'
        mock_pynetbox.ipam.ip_addresses.create.side_effect = [
            mock_ip1,
            Exception("Creation failed")
        ]
        
        # Test allocation
        nodes = ['node1', 'node2']
        result = netbox_manager.allocate_ips('test-lab', nodes)
        
        assert result == {}
        # Verify rollback was called
        mock_ip1.delete.assert_called_once()
    
    def test_release_ips(self, netbox_manager, mock_pynetbox):
        """Test IP release"""
        # Mock IP objects
        mock_ips = [Mock(), Mock(), Mock()]
        mock_pynetbox.ipam.ip_addresses.filter.return_value = mock_ips
        
        # Test release
        result = netbox_manager.release_ips('test-lab')
        
        assert result is True
        # Verify all IPs were deleted
        for mock_ip in mock_ips:
            mock_ip.delete.assert_called_once()
    
    def test_update_nodes_csv(self, netbox_manager):
        """Test updating nodes.csv with allocated IPs"""
        # Create temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.DictWriter(f, fieldnames=['hostname', 'platform', 'type'])
            writer.writeheader()
            writer.writerows([
                {'hostname': 'r1', 'platform': 'juniper', 'type': 'router'},
                {'hostname': 'r2', 'platform': 'juniper', 'type': 'router'}
            ])
            temp_file = Path(f.name)
        
        try:
            # Test update
            ip_assignments = {
                'r1': '10.100.100.1',
                'r2': '10.100.100.2'
            }
            result = netbox_manager.update_nodes_csv(temp_file, ip_assignments)
            
            assert result is True
            
            # Verify CSV was updated
            with open(temp_file, 'r') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                
            assert 'mgmt_ip' in rows[0]
            assert rows[0]['mgmt_ip'] == '10.100.100.1'
            assert rows[1]['mgmt_ip'] == '10.100.100.2'
            
        finally:
            temp_file.unlink()
    
    def test_register_devices(self, netbox_manager, mock_pynetbox):
        """Test device registration in NetBox"""
        # Mock site, role, device type
        mock_site = Mock(id=1)
        mock_role = Mock(id=2)
        mock_device_type = Mock(id=3)
        mock_manufacturer = Mock(id=4)
        
        mock_pynetbox.dcim.sites.get.return_value = mock_site
        mock_pynetbox.dcim.device_roles.get.return_value = mock_role
        mock_pynetbox.dcim.device_types.get.return_value = mock_device_type
        mock_pynetbox.dcim.manufacturers.get.return_value = mock_manufacturer
        
        # Mock device creation
        mock_pynetbox.dcim.devices.create.return_value = Mock(name='test-lab-r1')
        mock_pynetbox.dcim.devices.get.return_value = None  # No existing device
        
        # Test registration
        nodes = [
            {'hostname': 'r1', 'mgmt_ip': '10.100.100.1'},
            {'hostname': 'r2', 'mgmt_ip': '10.100.100.2'}
        ]
        result = netbox_manager.register_devices('test-lab', 'Test Lab', nodes)
        
        assert len(result) == 2
        assert mock_pynetbox.dcim.devices.create.call_count == 2
    
    def test_unregister_devices(self, netbox_manager, mock_pynetbox):
        """Test device unregistration"""
        # Mock devices
        mock_devices = [Mock(name='test-lab-r1'), Mock(name='test-lab-r2')]
        mock_pynetbox.dcim.devices.filter.return_value = mock_devices
        
        # Test unregistration
        result = netbox_manager.unregister_devices('test-lab')
        
        assert result is True
        # Verify all devices were deleted
        for device in mock_devices:
            device.delete.assert_called_once()
    
    def test_validate_config_success(self, netbox_manager, mock_pynetbox):
        """Test successful configuration validation"""
        # Mock prefix exists
        mock_pynetbox.ipam.prefixes.get.return_value = Mock()
        
        # Test validation
        is_valid, errors = netbox_manager.validate_config()
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_config_missing_prefix(self, netbox_manager, mock_pynetbox):
        """Test validation with missing prefix"""
        # Mock prefix not found
        mock_pynetbox.ipam.prefixes.get.return_value = None
        
        # Test validation
        is_valid, errors = netbox_manager.validate_config()
        
        assert is_valid is False
        assert len(errors) > 0
        assert any('prefix' in error.lower() for error in errors)
    
    def test_validate_config_connection_error(self, netbox_manager, mock_pynetbox):
        """Test validation with connection error"""
        # Mock connection failure
        mock_pynetbox.status.side_effect = Exception("Connection failed")
        
        # Test validation
        is_valid, errors = netbox_manager.validate_config()
        
        assert is_valid is False
        assert len(errors) > 0
        assert any('connection' in error.lower() for error in errors)


@pytest.mark.unit 
class TestNetBoxManagerDisabled:
    """Test NetBox manager when disabled"""
    
    @pytest.fixture
    def disabled_manager(self):
        """Create disabled NetBox manager"""
        config = {'enabled': False}
        return NetBoxManager(config)
    
    def test_allocate_ips_disabled(self, disabled_manager):
        """Test IP allocation returns empty when disabled"""
        result = disabled_manager.allocate_ips('test-lab', ['node1'])
        assert result == {}
    
    def test_release_ips_disabled(self, disabled_manager):
        """Test IP release returns True when disabled"""
        result = disabled_manager.release_ips('test-lab')
        assert result is True
    
    def test_validate_disabled(self, disabled_manager):
        """Test validation returns valid when disabled"""
        is_valid, errors = disabled_manager.validate_config()
        assert is_valid is True
        assert len(errors) == 0
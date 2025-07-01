"""
Integration tests for NetBox CLI commands
"""
import pytest
from unittest.mock import Mock, patch
from click.testing import CliRunner

from src.cli.main import cli
from src.cli.client import LabCtlClient


@pytest.mark.integration
class TestNetBoxCLICommands:
    """Test NetBox-related CLI commands"""
    
    @pytest.fixture
    def mock_client(self):
        """Create mock API client"""
        client = Mock(spec=LabCtlClient)
        client.health_check.return_value = True
        client.session = Mock()
        client.api_url = 'http://localhost:5001'
        return client
    
    @pytest.fixture
    def cli_runner(self):
        """Create click test runner"""
        return CliRunner()
    
    def test_netbox_command_valid_config(self, cli_runner, mock_client):
        """Test netbox command with valid configuration"""
        # Mock API response for valid NetBox config
        mock_response = Mock()
        mock_response.json.return_value = {
            'enabled': True,
            'valid': True,
            'message': 'NetBox configuration is valid'
        }
        mock_response.raise_for_status.return_value = None
        mock_client.session.get.return_value = mock_response
        
        # Test command
        with patch('src.cli.main.LabCtlClient', return_value=mock_client):
            result = cli_runner.invoke(cli, ['netbox'])
        
        assert result.exit_code == 0
        assert '✓ NetBox configuration is valid' in result.output
    
    def test_netbox_command_invalid_config(self, cli_runner, mock_client):
        """Test netbox command with invalid configuration"""
        # Mock API response for invalid NetBox config
        mock_response = Mock()
        mock_response.json.return_value = {
            'enabled': True,
            'valid': False,
            'errors': [
                'Default prefix not found in NetBox',
                'Failed to connect to NetBox API'
            ],
            'message': 'NetBox configuration has errors'
        }
        mock_response.raise_for_status.return_value = None
        mock_client.session.get.return_value = mock_response
        
        # Test command
        with patch('src.cli.main.LabCtlClient', return_value=mock_client):
            result = cli_runner.invoke(cli, ['netbox'])
        
        assert result.exit_code == 0
        assert '✗ NetBox configuration has errors:' in result.output
        assert 'Default prefix not found in NetBox' in result.output
        assert 'Failed to connect to NetBox API' in result.output
    
    def test_netbox_command_disabled(self, cli_runner, mock_client):
        """Test netbox command when NetBox is disabled"""
        # Mock API response for disabled NetBox
        mock_response = Mock()
        mock_response.json.return_value = {
            'enabled': False,
            'valid': True,
            'message': 'NetBox integration is disabled'
        }
        mock_response.raise_for_status.return_value = None
        mock_client.session.get.return_value = mock_response
        
        # Test command
        with patch('src.cli.main.LabCtlClient', return_value=mock_client):
            result = cli_runner.invoke(cli, ['netbox'])
        
        assert result.exit_code == 0
        assert 'NetBox integration is disabled' in result.output
    
    def test_netbox_command_connection_error(self, cli_runner, mock_client):
        """Test netbox command with connection error"""
        # Mock connection error
        mock_client.session.get.side_effect = Exception("Connection refused")
        
        # Test command
        with patch('src.cli.main.LabCtlClient', return_value=mock_client):
            result = cli_runner.invoke(cli, ['netbox'])
        
        assert result.exit_code == 0
        assert 'Error validating NetBox: Connection refused' in result.output
    
    def test_deploy_with_allocate_ips_flag(self, cli_runner, mock_client):
        """Test deploy command with --allocate-ips flag"""
        # Mock successful deployment
        mock_client.deploy_lab.return_value = {
            'task_id': 'test-task-123'
        }
        
        # Mock task status - completed
        mock_client.get_task_status.return_value = {
            'status': 'completed',
            'result': {
                'success': True,
                'message': 'Lab deployed successfully',
                'deployment_id': 'test-lab-deployment'
            }
        }
        
        # Test deploy command with IP allocation
        with patch('src.cli.main.LabCtlClient', return_value=mock_client):
            result = cli_runner.invoke(cli, ['deploy', 'test-lab', '--allocate-ips'])
        
        assert result.exit_code == 0
        assert 'Lab deployed successfully' in result.output
        
        # Verify allocate_ips was passed to API
        mock_client.deploy_lab.assert_called_once_with('test-lab', 'latest', True)
    
    def test_deploy_without_allocate_ips(self, cli_runner, mock_client):
        """Test deploy command without --allocate-ips flag"""
        # Mock successful deployment
        mock_client.deploy_lab.return_value = {
            'task_id': 'test-task-123'
        }
        
        # Mock task status - completed
        mock_client.get_task_status.return_value = {
            'status': 'completed',
            'result': {
                'success': True,
                'message': 'Lab deployed successfully',
                'deployment_id': 'test-lab-deployment'
            }
        }
        
        # Test deploy command without IP allocation
        with patch('src.cli.main.LabCtlClient', return_value=mock_client):
            result = cli_runner.invoke(cli, ['deploy', 'test-lab'])
        
        assert result.exit_code == 0
        assert 'Lab deployed successfully' in result.output
        
        # Verify allocate_ips was False
        mock_client.deploy_lab.assert_called_once_with('test-lab', 'latest', False)
    
    def test_doctor_command_shows_netbox_info(self, cli_runner, mock_client):
        """Test that doctor command shows NetBox configuration"""
        # Mock doctor response with NetBox info
        mock_client.get_config.return_value = {
            'repos_dir': '/opt/labctl/repos',
            'logs_dir': '/opt/labctl/logs',
            'netbox': {
                'enabled': True,
                'url': 'https://netbox.example.com',
                'default_prefix': '10.100.100.0/24'
            }
        }
        
        # Test doctor command
        with patch('src.cli.main.LabCtlClient', return_value=mock_client):
            result = cli_runner.invoke(cli, ['doctor'])
        
        assert result.exit_code == 0
        assert '✓ Backend is healthy' in result.output
        assert 'NetBox integration: Enabled' in result.output
        assert 'NetBox URL: https://netbox.example.com' in result.output
    
    def test_help_includes_netbox_command(self, cli_runner):
        """Test that help output includes netbox command"""
        result = cli_runner.invoke(cli, ['--help'])
        
        assert result.exit_code == 0
        assert 'netbox' in result.output
        assert 'Validate NetBox configuration and connectivity' in result.output
    
    def test_netbox_help(self, cli_runner):
        """Test netbox command help"""
        result = cli_runner.invoke(cli, ['netbox', '--help'])
        
        assert result.exit_code == 0
        assert 'Validate NetBox configuration and connectivity' in result.output
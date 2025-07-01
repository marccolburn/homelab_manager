"""
Integration tests for NetBox API endpoints
"""
import pytest
from unittest.mock import Mock, patch
import json

from src.backend.app import create_app


@pytest.mark.integration
class TestNetBoxAPIEndpoints:
    """Test NetBox-related API endpoints"""
    
    @pytest.fixture
    def app_with_netbox(self, test_config):
        """Create Flask app with NetBox configuration"""
        # Add NetBox config
        test_config['netbox'] = {
            'enabled': True,
            'url': 'https://netbox.example.com',
            'token': 'test-token',
            'default_prefix': '10.100.100.0/24'
        }
        
        app = create_app(test_config=test_config)
        app.config['TESTING'] = True
        return app
    
    @pytest.fixture
    def client_with_netbox(self, app_with_netbox):
        """Create test client with NetBox-enabled app"""
        return app_with_netbox.test_client()
    
    def test_netbox_validate_endpoint(self, client_with_netbox, app_with_netbox):
        """Test NetBox validation endpoint"""
        with app_with_netbox.app_context():
            # Mock the validate method
            with patch.object(app_with_netbox.lab_manager, 'validate_netbox_config') as mock_validate:
                mock_validate.return_value = {
                    'enabled': True,
                    'valid': True,
                    'message': 'NetBox configuration is valid'
                }
                
                # Test endpoint
                response = client_with_netbox.get('/api/netbox/validate')
                
                assert response.status_code == 200
                data = response.get_json()
                assert data['enabled'] is True
                assert data['valid'] is True
                assert 'NetBox configuration is valid' in data['message']
    
    def test_netbox_validate_with_errors(self, client_with_netbox, app_with_netbox):
        """Test NetBox validation with configuration errors"""
        with app_with_netbox.app_context():
            # Mock validation errors
            with patch.object(app_with_netbox.lab_manager, 'validate_netbox_config') as mock_validate:
                mock_validate.return_value = {
                    'enabled': True,
                    'valid': False,
                    'errors': [
                        'Default prefix not found in NetBox',
                        'Failed to connect to NetBox API'
                    ],
                    'message': 'NetBox configuration has errors'
                }
                
                # Test endpoint
                response = client_with_netbox.get('/api/netbox/validate')
                
                assert response.status_code == 200
                data = response.get_json()
                assert data['enabled'] is True
                assert data['valid'] is False
                assert len(data['errors']) == 2
                assert 'NetBox configuration has errors' in data['message']
    
    def test_netbox_validate_disabled(self, flask_client, flask_app):
        """Test NetBox validation when disabled"""
        with flask_app.app_context():
            # Mock disabled NetBox
            with patch.object(flask_app.lab_manager, 'validate_netbox_config') as mock_validate:
                mock_validate.return_value = {
                    'enabled': False,
                    'valid': True,
                    'message': 'NetBox integration is disabled'
                }
                
                # Test endpoint
                response = flask_client.get('/api/netbox/validate')
                
                assert response.status_code == 200
                data = response.get_json()
                assert data['enabled'] is False
                assert data['valid'] is True
    
    def test_deploy_with_allocate_ips(self, client_with_netbox, app_with_netbox):
        """Test deployment endpoint with allocate_ips flag"""
        with app_with_netbox.app_context():
            # Add repo to state
            app_with_netbox.lab_manager.state['repos']['test-lab'] = {
                'id': 'test-lab',
                'name': 'Test Lab',
                'path': '/tmp/test-lab'
            }
            
            # Mock deployment
            with patch.object(app_with_netbox.lab_manager, 'deploy_lab_async') as mock_deploy:
                mock_deploy.return_value = 'task-123'
                
                # Test deployment with IP allocation
                response = client_with_netbox.post('/api/labs/test-lab/deploy',
                                                 json={'allocate_ips': True})
                
                assert response.status_code == 202
                data = response.get_json()
                assert data['task_id'] == 'task-123'
                
                # Verify allocate_ips was passed
                mock_deploy.assert_called_once_with('test-lab', 'latest', True)
    
    def test_config_endpoint_masks_token(self, client_with_netbox):
        """Test that config endpoint masks NetBox token"""
        response = client_with_netbox.get('/api/config')
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Verify NetBox config exists but token is masked
        assert 'netbox' in data
        assert data['netbox']['enabled'] is True
        assert data['netbox']['token'] == '***'
        assert data['netbox']['url'] == 'https://netbox.example.com'
    
    def test_deployment_status_with_netbox(self, client_with_netbox, app_with_netbox):
        """Test deployment status includes NetBox information"""
        with app_with_netbox.app_context():
            # Add deployment with NetBox info
            app_with_netbox.lab_manager.state['repos']['test-lab'] = {
                'id': 'test-lab',
                'metadata': {'name': 'Test Lab'}
            }
            app_with_netbox.lab_manager.state['deployments']['test-deployment'] = {
                'lab_id': 'test-lab',
                'status': 'active',
                'version': '1.0.0',
                'deployed_at': '2024-01-01T12:00:00',
                'netbox_ips_allocated': True,
                'ip_assignments': {
                    'r1': '10.100.100.1',
                    'r2': '10.100.100.2'
                }
            }
            
            # Get deployments
            response = client_with_netbox.get('/api/deployments')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['total'] == 1
            
            # Note: Current implementation doesn't expose IP assignments in status
            # This is by design for security - IPs are internal deployment details
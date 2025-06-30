"""
Integration tests for CLI commands
"""
import unittest
from unittest.mock import patch, Mock
from click.testing import CliRunner
import json

# Add src to path for testing
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.cli.main import cli


class TestCLICommands(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.runner = CliRunner()
        self.api_url = 'http://localhost:5001'
    
    @patch('src.cli.client.LabCtlClient.health_check')
    @patch('src.cli.client.LabCtlClient.list_repos')
    def test_repo_list_command(self, mock_list_repos, mock_health_check):
        """Test repo list command"""
        mock_health_check.return_value = True
        mock_list_repos.return_value = [
            {
                'id': 'test-lab',
                'name': 'Test Lab',
                'version': '1.0.0',
                'category': 'Testing',
                'vendor': 'Test Vendor',
                'difficulty': 'Easy'
            }
        ]
        
        result = self.runner.invoke(cli, [
            '--api-url', self.api_url,
            'repo', 'list'
        ])
        
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Test Lab', result.output)
        self.assertIn('test-lab', result.output)
    
    @patch('src.cli.client.LabCtlClient.health_check')
    @patch('src.cli.client.LabCtlClient.list_repos')
    def test_repo_list_json_output(self, mock_list_repos, mock_health_check):
        """Test repo list command with JSON output"""
        mock_health_check.return_value = True
        test_data = [{'id': 'test-lab', 'name': 'Test Lab'}]
        mock_list_repos.return_value = test_data
        
        result = self.runner.invoke(cli, [
            '--api-url', self.api_url,
            'repo', 'list', '--json'
        ])
        
        self.assertEqual(result.exit_code, 0)
        # Output should be valid JSON
        output_data = json.loads(result.output)
        self.assertEqual(output_data, test_data)
    
    @patch('src.cli.client.LabCtlClient.health_check')
    @patch('src.cli.client.LabCtlClient.add_repo')
    def test_repo_add_command(self, mock_add_repo, mock_health_check):
        """Test repo add command"""
        mock_health_check.return_value = True
        mock_add_repo.return_value = {
            'success': True,
            'metadata': {'name': 'Test Lab'}
        }
        
        result = self.runner.invoke(cli, [
            '--api-url', self.api_url,
            'repo', 'add', 'https://github.com/test/repo.git'
        ])
        
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Successfully added lab: Test Lab', result.output)
        mock_add_repo.assert_called_once_with('https://github.com/test/repo.git', None)
    
    @patch('src.cli.client.LabCtlClient.health_check')
    @patch('src.cli.client.LabCtlClient.get_deployments')
    def test_status_command(self, mock_get_deployments, mock_health_check):
        """Test status command"""
        mock_health_check.return_value = True
        mock_get_deployments.return_value = {
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
        }
        
        result = self.runner.invoke(cli, [
            '--api-url', self.api_url,
            'status'
        ])
        
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Active Deployments', result.output)
        self.assertIn('test-lab', result.output)
        self.assertIn('Total active deployments: 1', result.output)
    
    @patch('src.cli.client.LabCtlClient.health_check')
    @patch('src.cli.client.LabCtlClient.get_config')
    def test_doctor_command(self, mock_get_config, mock_health_check):
        """Test doctor command"""
        mock_health_check.return_value = True
        mock_get_config.return_value = {
            'repos_dir': '/tmp/repos',
            'logs_dir': '/tmp/logs',
            'git_cmd': 'git',
            'clab_tools_cmd': 'clab-tools',
            'netbox': {'enabled': False},
            'monitoring': {
                'prometheus': 'http://localhost:9090',
                'grafana': 'http://localhost:3000'
            }
        }
        
        result = self.runner.invoke(cli, [
            '--api-url', self.api_url,
            'doctor'
        ])
        
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Backend is healthy', result.output)
        self.assertIn('Backend Configuration', result.output)
        self.assertIn('/tmp/repos', result.output)
    
    def test_version_command(self):
        """Test version command"""
        with patch('src.cli.client.LabCtlClient.health_check', return_value=True):
            result = self.runner.invoke(cli, [
                '--api-url', self.api_url,
                'version'
            ])
        
        self.assertEqual(result.exit_code, 0)
        self.assertIn('labctl - Homelab Manager CLI', result.output)
        self.assertIn('Backend Status: Healthy', result.output)
    
    @patch('src.cli.client.LabCtlClient.health_check')
    @patch('src.cli.client.LabCtlClient.list_scenarios')
    def test_config_list_command(self, mock_list_scenarios, mock_health_check):
        """Test config list command"""
        mock_health_check.return_value = True
        mock_list_scenarios.return_value = ['baseline', 'scenario-1']
        
        result = self.runner.invoke(cli, [
            '--api-url', self.api_url,
            'config', 'list', 'test-lab'
        ])
        
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Configuration Scenarios for test-lab', result.output)
        self.assertIn('baseline', result.output)
        self.assertIn('scenario-1', result.output)
    
    def test_backend_health_check_failure(self):
        """Test CLI behavior when backend is unhealthy"""
        with patch('src.cli.client.LabCtlClient.health_check', return_value=False):
            result = self.runner.invoke(cli, [
                '--api-url', self.api_url,
                'repo', 'list'
            ])
        
        self.assertEqual(result.exit_code, 1)
        self.assertIn('Backend is not healthy', result.output)


if __name__ == '__main__':
    unittest.main()
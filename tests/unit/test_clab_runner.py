"""
Unit tests for ClabRunner module
"""
import unittest
from unittest.mock import Mock, patch, MagicMock, mock_open
from pathlib import Path
import subprocess
import os

from src.backend.core.clab_runner import ClabRunner


class TestClabRunner(unittest.TestCase):
    
    def setUp(self):
        # Use temp directory for tests
        self.clab_runner = ClabRunner(logs_dir=Path('/tmp/test_logs'))
    
    @patch('subprocess.run')
    @patch('os.chmod')
    @patch('builtins.open', new_callable=mock_open)
    def test_bootstrap_lab_success(self, mock_file, mock_chmod, mock_run):
        """Test successful lab bootstrap"""
        mock_run.return_value = Mock(returncode=0, stdout='Bootstrap successful', stderr='')
        
        with patch('pathlib.Path.exists', return_value=True):
            success, result = self.clab_runner.bootstrap_lab(
                'test-lab', 
                Path('/tmp/test-repo')
            )
        
        self.assertTrue(success)
        self.assertIn('deployment_id', result)
        self.assertIn('log_file', result)
        self.assertIn('Lab test-lab deployed successfully', result['message'])
        mock_chmod.assert_called_once()
    
    @patch('subprocess.run')
    def test_bootstrap_lab_script_not_found(self, mock_run):
        """Test bootstrap when script doesn't exist"""
        with patch('pathlib.Path.exists', return_value=False):
            success, result = self.clab_runner.bootstrap_lab(
                'test-lab',
                Path('/tmp/test-repo')
            )
        
        self.assertFalse(success)
        self.assertEqual(result['error'], 'bootstrap.sh not found')
        mock_run.assert_not_called()
    
    @patch('subprocess.run')
    @patch('os.chmod')
    def test_teardown_lab_success(self, mock_chmod, mock_run):
        """Test successful lab teardown"""
        mock_run.return_value = Mock(returncode=0)
        
        with patch('pathlib.Path.exists', return_value=True):
            success, result = self.clab_runner.teardown_lab(
                'test-lab',
                Path('/tmp/test-repo')
            )
        
        self.assertTrue(success)
        self.assertIn('Lab test-lab destroyed successfully', result['message'])
        mock_chmod.assert_called_once()
    
    def test_get_lab_status_deployed(self):
        """Test checking status of deployed lab"""
        with patch('pathlib.Path.exists', return_value=True):
            status = self.clab_runner.get_lab_status('test-lab', Path('/tmp/test-repo'))
        
        self.assertTrue(status['deployed'])
        self.assertIn('clab_file', status)
        self.assertIn('Lab test-lab appears to be deployed', status['message'])
    
    def test_get_lab_status_not_deployed(self):
        """Test checking status of non-deployed lab"""
        with patch('pathlib.Path.exists', return_value=False):
            status = self.clab_runner.get_lab_status('test-lab', Path('/tmp/test-repo'))
        
        self.assertFalse(status['deployed'])
        self.assertIn('Lab test-lab is not deployed', status['message'])
    
    def test_get_node_list(self):
        """Test getting node list from nodes.csv"""
        csv_content = "name,type,image\nrouter1,ceos,ceos:latest\nrouter2,ceos,ceos:latest"
        
        with patch('builtins.open', mock_open(read_data=csv_content)):
            with patch('pathlib.Path.exists', return_value=True):
                nodes = self.clab_runner.get_node_list('test-lab', Path('/tmp/test-repo'))
        
        self.assertEqual(nodes, ['router1', 'router2'])
    
    def test_validate_lab_files_valid(self):
        """Test validation of lab files - all present"""
        with patch('pathlib.Path.exists', return_value=True):
            is_valid, missing = self.clab_runner.validate_lab_files(Path('/tmp/test-repo'))
        
        self.assertTrue(is_valid)
        self.assertEqual(missing, [])
    
    def test_validate_lab_files_missing(self):
        """Test validation of lab files - some missing"""
        def exists_side_effect(path):
            # Make bootstrap.sh missing
            return 'bootstrap.sh' not in str(path)
        
        with patch('pathlib.Path.exists', side_effect=exists_side_effect):
            is_valid, missing = self.clab_runner.validate_lab_files(Path('/tmp/test-repo'))
        
        self.assertFalse(is_valid)
        self.assertIn('clab_tools_files/bootstrap.sh', missing)
    
    @patch('subprocess.run')
    def test_check_clab_tools_available(self, mock_run):
        """Test checking clab-tools availability"""
        mock_run.return_value = Mock(returncode=0)
        
        self.assertTrue(self.clab_runner.check_clab_tools())
        
        mock_run.return_value = Mock(returncode=1)
        self.assertFalse(self.clab_runner.check_clab_tools())


if __name__ == '__main__':
    unittest.main()
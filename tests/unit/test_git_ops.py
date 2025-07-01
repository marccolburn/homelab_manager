"""
Unit tests for GitOperations module
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import subprocess

from src.backend.core.git_ops import GitOperations


class TestGitOperations(unittest.TestCase):
    
    def setUp(self):
        self.git_ops = GitOperations()
    
    @patch('subprocess.run')
    def test_clone_success(self, mock_run):
        """Test successful repository clone"""
        mock_run.return_value = Mock(returncode=0, stdout='', stderr='')
        
        result = self.git_ops.clone('https://github.com/test/repo.git', Path('/tmp/test'))
        
        self.assertTrue(result['success'])
        self.assertIn('Repository cloned', result['message'])
        mock_run.assert_called_once()
        
    @patch('subprocess.run')
    def test_clone_failure(self, mock_run):
        """Test failed repository clone"""
        mock_run.return_value = Mock(returncode=1, stdout='', stderr='Error cloning')
        
        result = self.git_ops.clone('https://github.com/test/repo.git', Path('/tmp/test'))
        
        self.assertFalse(result['success'])
        self.assertIn('Git clone failed', result['error'])
    
    @patch('subprocess.run')
    def test_pull_success(self, mock_run):
        """Test successful git pull"""
        mock_run.return_value = Mock(returncode=0, stdout='', stderr='')
        
        with patch.object(self.git_ops, 'is_git_repo', return_value=True):
            result = self.git_ops.pull(Path('/tmp/test'))
        
        self.assertTrue(result['success'])
        self.assertEqual(result['message'], 'Repository updated')
    
    @patch('subprocess.run')
    def test_pull_not_git_repo(self, mock_run):
        """Test pull on non-git directory"""
        with patch.object(self.git_ops, 'is_git_repo', return_value=False):
            result = self.git_ops.pull(Path('/tmp/test'))
        
        self.assertFalse(result['success'])
        self.assertIn('is not a git repository', result['error'])
        mock_run.assert_not_called()
    
    @patch('subprocess.run')
    def test_checkout(self, mock_run):
        """Test git checkout"""
        mock_run.return_value = Mock(returncode=0, stdout='', stderr='')
        
        with patch.object(self.git_ops, 'is_git_repo', return_value=True):
            result = self.git_ops.checkout(Path('/tmp/test'), 'v1.0.0')
        
        self.assertTrue(result['success'])
        self.assertIn('Checked out v1.0.0', result['message'])
    
    @patch('subprocess.run')
    def test_get_tags(self, mock_run):
        """Test getting repository tags"""
        mock_run.return_value = Mock(returncode=0, stdout='v1.0.0\nv1.1.0\nv2.0.0', stderr='')
        
        with patch.object(self.git_ops, 'is_git_repo', return_value=True):
            tags = self.git_ops.get_tags(Path('/tmp/test'))
        
        self.assertEqual(tags, ['v1.0.0', 'v1.1.0', 'v2.0.0'])
    
    def test_is_git_repo(self):
        """Test git repository detection"""
        with patch('pathlib.Path.exists') as mock_exists:
            with patch('pathlib.Path.is_dir') as mock_is_dir:
                # Test valid git repo
                mock_exists.side_effect = [True, True]  # repo exists, .git exists
                mock_is_dir.return_value = True
                
                self.assertTrue(self.git_ops.is_git_repo(Path('/tmp/test')))
                
                # Test non-git directory
                mock_exists.side_effect = [True, False]  # repo exists, .git doesn't
                self.assertFalse(self.git_ops.is_git_repo(Path('/tmp/test')))


if __name__ == '__main__':
    unittest.main()
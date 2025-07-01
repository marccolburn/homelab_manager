#!/usr/bin/env python3
"""
Integration test to verify Phase 2 reorganization functionality
"""
import unittest
import sys
import os
from pathlib import Path

# Add project root to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class TestModuleIntegration(unittest.TestCase):
    """Test Phase 2 module reorganization and integration"""
    
    def test_backend_imports(self):
        """Test that all backend modules can be imported"""
        from src.backend.core.config import load_config
        from src.backend.core.git_ops import GitOperations
        from src.backend.core.clab_runner import ClabRunner
        from src.backend.core.lab_manager import LabManager
        
        # All imports successful
        self.assertTrue(True)
    
    def test_api_imports(self):
        """Test that all API blueprint modules can be imported"""
        from src.backend.api import repos_bp, labs_bp, tasks_bp, health_bp
        
        # Verify blueprints are properly configured
        self.assertIsNotNone(repos_bp)
        self.assertIsNotNone(labs_bp)
        self.assertIsNotNone(tasks_bp)
        self.assertIsNotNone(health_bp)
    
    def test_cli_imports(self):
        """Test that all CLI modules can be imported"""
        from src.cli.client import LabCtlClient
        from src.cli.commands import repo, lab_commands, config, system_commands
        
        # All imports successful
        self.assertTrue(True)
    
    def test_module_instantiation(self):
        """Test that core modules can be instantiated with dependencies"""
        from src.backend.core.config import load_config
        from src.backend.core.git_ops import GitOperations
        from src.backend.core.clab_runner import ClabRunner
        from src.backend.core.lab_manager import LabManager
        
        # Test instantiation
        config = load_config()
        self.assertIsInstance(config, dict)
        
        git_ops = GitOperations()
        self.assertIsNotNone(git_ops)
        
        clab_runner = ClabRunner(logs_dir=Path("./logs"))
        self.assertIsNotNone(clab_runner)
        
        lab_manager = LabManager(config, git_ops, clab_runner)
        self.assertIsNotNone(lab_manager)
    
    def test_flask_app_creation(self):
        """Test that Flask app can be created with new structure"""
        from src.backend.app import create_app
        
        app = create_app()
        self.assertIsNotNone(app)
        self.assertTrue(hasattr(app, 'lab_manager'))


if __name__ == '__main__':
    unittest.main()
#!/usr/bin/env python3
"""
Test script to verify Phase 2 reorganization functionality
"""
import sys
import os
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing Phase 2 module imports...")

try:
    # Test backend imports
    print("\n1. Testing backend imports:")
    from src.backend.core.config import load_config
    print("   ✓ config module")
    
    from src.backend.core.git_ops import GitOperations
    print("   ✓ git_ops module")
    
    from src.backend.core.clab_runner import ClabRunner
    print("   ✓ clab_runner module")
    
    from src.backend.core.lab_manager import LabManager
    print("   ✓ lab_manager module")
    
    # Test API imports
    print("\n2. Testing API imports:")
    from src.backend.api import repos_bp, labs_bp, tasks_bp, health_bp
    print("   ✓ All API blueprints")
    
    # Test CLI imports
    print("\n3. Testing CLI imports:")
    from src.cli.client import LabCtlClient
    print("   ✓ client module")
    
    from src.cli.commands import repo, lab_commands, config, system_commands
    print("   ✓ All command modules")
    
    # Test instantiation
    print("\n4. Testing module instantiation:")
    config = load_config()
    print("   ✓ Config loaded")
    
    git_ops = GitOperations()
    print("   ✓ GitOperations created")
    
    clab_runner = ClabRunner(logs_dir=Path("./logs"))
    print("   ✓ ClabRunner created")
    
    lab_manager = LabManager(config, git_ops, clab_runner)
    print("   ✓ LabManager created with dependencies")
    
    print("\n✅ All imports and instantiations successful!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
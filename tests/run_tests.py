#!/usr/bin/env python3
"""
Test runner for homelab manager tests
"""
import unittest
import sys
import os
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_unit_tests():
    """Run unit tests"""
    print("Running unit tests...")
    loader = unittest.TestLoader()
    suite = loader.discover('unit', pattern='test_*.py')
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()

def run_integration_tests():
    """Run integration tests"""
    print("\nRunning integration tests...")
    loader = unittest.TestLoader()
    suite = loader.discover('integration', pattern='test_*.py')
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()

def main():
    """Run all tests"""
    os.chdir(Path(__file__).parent)
    
    print("=" * 60)
    print("HOMELAB MANAGER - PHASE 2 TEST SUITE")
    print("=" * 60)
    
    unit_success = run_unit_tests()
    integration_success = run_integration_tests()
    
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"Unit Tests: {'PASSED' if unit_success else 'FAILED'}")
    print(f"Integration Tests: {'PASSED' if integration_success else 'FAILED'}")
    
    if unit_success and integration_success:
        print("\n✅ All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1

if __name__ == '__main__':
    sys.exit(main())
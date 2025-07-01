#!/usr/bin/env python3
"""
Pytest-based test runner for homelab manager tests
"""
import sys
import os
from pathlib import Path
import subprocess

# Add src to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_pytest_with_markers(*markers, verbose=True):
    """Run pytest with specific markers"""
    cmd = ['python', '-m', 'pytest']
    
    if verbose:
        cmd.append('-v')
    
    if markers:
        marker_expr = ' or '.join(markers)
        cmd.extend(['-m', marker_expr])
    
    # Add test directory
    cmd.append('tests')
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=project_root)
    return result.returncode == 0


def run_unit_tests():
    """Run unit tests"""
    print("Running unit tests...")
    return run_pytest_with_markers('unit')


def run_integration_tests():
    """Run integration tests"""
    print("\nRunning integration tests...")
    return run_pytest_with_markers('integration')


def run_e2e_tests():
    """Run end-to-end tests"""
    print("\nRunning end-to-end tests...")
    return run_pytest_with_markers('e2e')


def run_all_tests():
    """Run all tests without marker filtering"""
    print("\nRunning all tests...")
    cmd = ['python', '-m', 'pytest', '-v', 'tests']
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=project_root)
    return result.returncode == 0


def run_coverage():
    """Run tests with coverage"""
    print("\nRunning tests with coverage...")
    cmd = [
        'python', '-m', 'pytest', 
        '--cov=src', 
        '--cov-report=html', 
        '--cov-report=term-missing',
        '--cov-report=xml',
        '-v', 
        'tests'
    ]
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=project_root)
    return result.returncode == 0


def main():
    """Run test suite based on command line arguments"""
    os.chdir(project_root)
    
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
        
        if test_type == 'unit':
            success = run_unit_tests()
        elif test_type == 'integration':
            success = run_integration_tests()
        elif test_type == 'e2e':
            success = run_e2e_tests()
        elif test_type == 'coverage':
            success = run_coverage()
        elif test_type == 'all':
            success = run_all_tests()
        else:
            print(f"Unknown test type: {test_type}")
            print("Usage: python run_tests_pytest.py [unit|integration|e2e|all|coverage]")
            return 1
    else:
        # Run all test categories individually for detailed reporting
        print("=" * 60)
        print("HOMELAB MANAGER - PYTEST TEST SUITE")
        print("=" * 60)
        
        unit_success = run_unit_tests()
        integration_success = run_integration_tests()
        e2e_success = run_e2e_tests()
        
        print("\n" + "=" * 60)
        print("TEST RESULTS SUMMARY")
        print("=" * 60)
        print(f"Unit Tests: {'PASSED' if unit_success else 'FAILED'}")
        print(f"Integration Tests: {'PASSED' if integration_success else 'FAILED'}")
        print(f"End-to-End Tests: {'PASSED' if e2e_success else 'FAILED'}")
        
        success = unit_success and integration_success and e2e_success
    
    if success:
        print("\n✅ All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1


if __name__ == '__main__':
    sys.exit(main())
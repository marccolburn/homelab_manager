# Pytest Migration Guide

This document describes the migration from unittest to pytest for the Homelab Manager test suite.

## What's Changed

### 1. Test Framework Migration
- **Before**: `unittest.TestCase` classes with `setUp()` methods
- **After**: Pytest classes with fixture injection

### 2. Test Structure
- **Before**: 
  ```python
  class TestLabManager(unittest.TestCase):
      def setUp(self):
          self.config = {...}
      
      def test_something(self):
          self.assertEqual(result, expected)
  ```

- **After**:
  ```python
  @pytest.mark.unit
  class TestLabManager:
      def test_something(self, lab_manager):
          assert result == expected
  ```

### 3. Configuration Files Added
- `pytest.ini`: Main pytest configuration
- `tests/conftest.py`: Shared fixtures and configuration
- `tests/run_tests_pytest.py`: New pytest-based test runner

### 4. Enhanced Requirements
Added pytest plugins to `requirements/all.txt`:
- `pytest>=7.4.0`
- `pytest-cov>=4.1.0` (coverage reporting)
- `pytest-timeout>=2.1.0` (test timeouts)
- `pytest-mock>=3.11.0` (enhanced mocking)

## Key Benefits

### 1. Improved Test Organization
- **Markers**: Tests automatically marked by location (unit/integration/e2e)
- **Fixtures**: Reusable test setup with dependency injection
- **Better Discovery**: More flexible test collection patterns

### 2. Enhanced Features
- **Parametrized Tests**: Easy to run same test with different inputs
- **Coverage Reporting**: Built-in coverage analysis
- **Parallel Execution**: Can run tests in parallel (with pytest-xdist)
- **Better Output**: More readable test results and failure information

### 3. Modern Testing Patterns
- **Dependency Injection**: Fixtures provide clean test setup
- **Automatic Cleanup**: Session and function-scoped resource management
- **Mocking Integration**: Better integration with unittest.mock

## Running Tests

### Basic Commands
```bash
# Run all tests
python -m pytest

# Run specific test categories
python -m pytest -m unit           # Unit tests only
python -m pytest -m integration    # Integration tests only
python -m pytest -m e2e           # End-to-end tests only

# Run specific test file
python -m pytest tests/unit/test_lab_manager.py

# Run specific test method
python -m pytest tests/unit/test_lab_manager.py::TestLabManagerState::test_load_state

# Verbose output
python -m pytest -v

# Show test coverage
python -m pytest --cov=src --cov-report=html
```

### Using the Test Runner
```bash
# Use the new pytest runner
python tests/run_tests_pytest.py

# Run specific test types
python tests/run_tests_pytest.py unit
python tests/run_tests_pytest.py integration
python tests/run_tests_pytest.py e2e
python tests/run_tests_pytest.py coverage
```

## Test Markers

Tests are automatically marked based on their location:

- `@pytest.mark.unit`: Tests in `tests/unit/`
- `@pytest.mark.integration`: Tests in `tests/integration/`
- `@pytest.mark.e2e`: Tests in `tests/e2e/`
- `@pytest.mark.slow`: E2E tests (automatically applied)

### Custom Markers
Available for manual use:
- `@pytest.mark.requires_git`: Tests that need git command
- `@pytest.mark.requires_containerlab`: Tests that need containerlab

## Available Fixtures

### Core Fixtures
- `temp_dirs`: Temporary directories for test isolation
- `test_config`: Configuration dictionary for testing
- `lab_manager`: LabManager instance with mocked dependencies
- `mock_git_ops`: Mock GitOperations instance
- `mock_clab_runner`: Mock ClabRunner instance

### Flask/API Fixtures
- `flask_app`: Flask application for testing
- `flask_client`: Flask test client
- `app_context`: Flask application context
- `cli_client`: CLI client for testing

### Data Fixtures
- `sample_lab_metadata`: Sample lab metadata dictionary
- `sample_repo_state`: Sample repository state data
- `sample_deployment_state`: Sample deployment state data

## Example Conversions

### Before (unittest)
```python
import unittest
from unittest.mock import Mock, patch

class TestLabManager(unittest.TestCase):
    def setUp(self):
        self.config = {'repos_dir': '/tmp/repos'}
        self.mock_git = Mock()
        self.lab_manager = LabManager(self.config, self.mock_git)
    
    def test_list_repos(self):
        self.lab_manager.state = {'repos': {'test': {}}}
        repos = self.lab_manager.list_repos()
        self.assertEqual(len(repos), 1)
```

### After (pytest)
```python
import pytest
from unittest.mock import Mock, patch

@pytest.mark.unit
class TestLabManager:
    def test_list_repos(self, lab_manager):
        lab_manager.state = {'repos': {'test': {}}}
        repos = lab_manager.list_repos()
        assert len(repos) == 1
```

## Migration Status

### ✅ Completed
1. **Core Infrastructure**
   - pytest.ini configuration
   - conftest.py with shared fixtures
   - pytest test runner script
   - Requirements updated with pytest plugins

2. **Sample Conversion**
   - `test_lab_manager.py` partially converted to demonstrate patterns
   - All test classes converted to pytest style
   - Fixtures working correctly

### 🔄 In Progress
1. **Complete File Conversions**
   - `test_git_ops.py`
   - `test_clab_runner.py`
   - `test_api_endpoints.py`
   - `test_cli_commands.py`
   - `test_basic_workflow.py`

### 📋 TODO
1. **Enhanced Features**
   - Parametrized tests for better coverage
   - Parallel test execution setup
   - CI/CD integration scripts
   - Performance benchmarking tests

## Development Workflow

### Writing New Tests
1. Create test files in appropriate directory (`unit/`, `integration/`, `e2e/`)
2. Use fixtures for setup instead of `setUp()` methods
3. Use `assert` statements instead of `self.assertEqual()`
4. Add appropriate markers if needed

### Running Tests During Development
```bash
# Quick unit test run
python -m pytest -m unit -x  # Stop on first failure

# Watch mode (requires pytest-watch)
ptw tests/unit/

# Specific test with output
python -m pytest tests/unit/test_lab_manager.py::TestLabManager::test_specific -v -s
```

### Coverage Analysis
```bash
# Generate HTML coverage report
python -m pytest --cov=src --cov-report=html tests/

# View coverage report
open htmlcov/index.html
```

## Best Practices

### 1. Test Organization
- Group related tests in classes
- Use descriptive test names
- Add docstrings for complex tests

### 2. Fixture Usage
- Use fixtures for shared setup
- Prefer dependency injection over global state
- Create focused, single-purpose fixtures

### 3. Mocking
- Mock external dependencies
- Use `monkeypatch` for temporary changes
- Prefer unittest.mock over custom mocking

### 4. Assertions
- Use simple `assert` statements
- Add custom messages for complex assertions
- Use pytest's rich assertion introspection

## Troubleshooting

### Common Issues

1. **Fixture Not Found**
   ```bash
   Error: fixture 'lab_manager' not found
   ```
   - Ensure conftest.py is in the right location
   - Check fixture import paths

2. **Mock Attribute Errors**
   ```bash
   AttributeError: Mock object has no attribute 'method_name'
   ```
   - Verify the spec class has the expected methods
   - Update mock setup in conftest.py

3. **Test Discovery Issues**
   ```bash
   No tests collected
   ```
   - Check test file naming (`test_*.py`)
   - Verify test function naming (`test_*`)
   - Check directory structure

### Debugging Tests
```bash
# Run with debugging output
python -m pytest -v -s --tb=long

# Run specific test with pdb
python -m pytest --pdb tests/unit/test_lab_manager.py::TestLabManager::test_method

# Show fixture setup
python -m pytest --setup-show tests/unit/test_lab_manager.py
```

## Future Enhancements

1. **Performance Testing**: Add benchmarking with pytest-benchmark
2. **Property-Based Testing**: Add hypothesis for property-based tests
3. **Parallel Execution**: Configure pytest-xdist for faster test runs
4. **Test Reporting**: Enhanced reporting with pytest-html
5. **Database Testing**: Add pytest-postgresql for database tests (future)

This migration provides a solid foundation for modern, maintainable testing practices while preserving all existing test functionality.
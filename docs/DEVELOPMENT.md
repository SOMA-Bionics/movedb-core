# Developer Setup Guide

## Quick Start for Testing

### 1. Create and Activate Development Environment
```bash
# Clone the repository
git clone https://github.com/SOMA-Bionics/movedb-core.git
cd movedb-core

# Create conda environment with all testing dependencies
conda env create -f environment.yml
conda activate movedb-core-dev

# OR use any conda environment with the required dependencies
conda create -n my-movedb-env python=3.11
conda activate my-movedb-env
conda install -c conda-forge -c opensim-org pytest pytest-cov black flake8 mypy numpy polars pydantic loguru ezc3d
```

### 2. Install Package in Development Mode
```bash
pip install -e .
```

### 3. Run Tests
```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src/movedb --cov-report=html

# Run specific test file
pytest tests/test_basic.py -v

# Run tests with verbose output
pytest -v

# Run tests and stop on first failure
pytest -x

# Run tests matching a pattern
pytest -k "test_trial" -v
```

### 4. Common Test Commands
```bash
# Quick test run (no coverage)
pytest --no-cov

# Test with coverage and open HTML report
pytest --cov=src/movedb --cov-report=html && open htmlcov/index.html

# Test specific functionality
pytest tests/test_basic.py::test_trial_creation -v

# Run tests in parallel (if pytest-xdist is installed)
pytest -n auto
```

## Testing Best Practices

### Import Style for Tests
Use explicit submodule imports in tests:
```python
# Recommended for tests
from movedb.core import Trial, Event, Points, Analogs
from movedb.file_io import C3DLoader, OpenSimExporter

# Instead of flat imports
from movedb import Trial, Event  # Still works but less clear
```

### Test File Organization
- `tests/test_basic.py` - Basic functionality and imports
- `tests/test_core/` - Core functionality tests
- `tests/test_file_io/` - File I/O tests
- `tests/test_integration/` - Integration tests

### Writing Tests
```python
import pytest
from movedb.core import Trial, Event

def test_example():
    """Test description."""
    # Test implementation
    pass

def test_example_with_fixtures():
    """Test with fixtures."""
    # Use fixtures for common setup
    pass
```

## CI/CD Integration

Tests are automatically run on:
- Pull requests
- Push to main branch
- Release creation

## Troubleshooting

### Common Issues
1. **Import errors**: Make sure package is installed with `pip install -e .`
2. **Missing dependencies**: Run `conda env update -f environment.yml` or install required packages
3. **Test failures**: Check that you're in a conda environment with pytest installed
4. **Environment name**: The test runner works with any conda environment that has the required dependencies

### Environment Issues
```bash
# Recreate environment if needed
conda env remove -n movedb-core-dev  # or your environment name
conda env create -f environment.yml
conda activate movedb-core-dev        # or your environment name
pip install -e .

# OR install dependencies in existing environment
conda install -c conda-forge -c opensim-org pytest pytest-cov
pip install -e .
```

### Coverage Issues
If coverage isn't working:
```bash
# Install coverage dependencies
conda install pytest-cov coverage
```

## VSCode Integration

Add to your VSCode `settings.json`:
```json
{
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": [
        "tests"
    ],
    "python.testing.unittestEnabled": false,
    "python.testing.cwd": "${workspaceFolder}",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black"
}
```

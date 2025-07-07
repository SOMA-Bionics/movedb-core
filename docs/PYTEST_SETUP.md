# Testing Guide

## ✅ Complete Testing Setup

### 1. **Comprehensive Environment Configuration**
- `environment.yml` includes all testing dependencies (pytest, pytest-cov, black, etc.)
- `pyproject.toml` has comprehensive pytest configuration with:
  - Coverage settings
  - Test markers for organization
  - Warning filters for cleaner output
  - Sensible defaults for test discovery

### 2. **Flexible Test Running Options**

#### **Makefile Commands** (recommended approach)
```bash
make test-quick        # Fast tests without coverage
make test             # Full test suite with coverage
make test-specific FILE=test_basic.py  # Run specific test file
make test-pattern PATTERN=imports      # Run tests matching pattern
make format           # Format code with black
make lint             # Run linting
make clean            # Clean build artifacts
make help             # Show all commands
```

#### **Python Test Runner** (`run_tests.py`)
```bash
python run_tests.py            # Run all tests with coverage
python run_tests.py --help     # Show help
python run_tests.py -v         # Verbose output
python run_tests.py -k imports # Pattern matching
```

#### **Direct pytest Usage**
```bash
pytest                         # Run all tests
pytest --no-cov               # Skip coverage
pytest tests/test_basic.py -v  # Specific file
pytest -k "imports" -v         # Pattern matching
```

## 🔧 Environment Flexibility

### **Works with Any Environment**
The test runner no longer requires specific environment names. It works with:

```bash
# Option 1: Use provided environment.yml (recommended)
conda env create -f environment.yml
conda activate movedb-core-dev

# Option 2: Create custom environment
conda create -n my-custom-env python=3.11
conda activate my-custom-env
conda install -c conda-forge -c opensim-org pytest pytest-cov black flake8 mypy

# Option 3: Use existing environment
conda activate existing-env
conda install pytest pytest-cov  # add missing dependencies
```

### **Smart Environment Detection**
The `run_tests.py` script now:
- Detects any conda environment automatically
- Warns about missing dependencies instead of failing
- Checks for actual package availability
- Provides helpful guidance when issues are found

## 🧪 Test Organization
- VSCode settings documented in `docs/DEVELOPMENT.md`
Tests are structured using explicit submodule imports:
```python
# Recommended style for tests
from movedb.core import Trial, Event
from movedb.file_io import C3DLoader

# Tests support this future-ready API structure
```

## 📊 Coverage and Quality Tools

- **Coverage Reports**: HTML coverage reports generated in `htmlcov/`
- **Code Formatting**: black configured and ready
- **Linting**: flake8 for code quality
- **Type Checking**: mypy for static type analysis
- **All Pre-configured**: Ready to use out of the box

## 🚀 Quick Developer Onboarding

New developers can get started with just:
```bash
git clone https://github.com/SOMA-Bionics/movedb-core.git
cd movedb-core
conda env create -f environment.yml
conda activate movedb-core-dev
pip install -e .
make test-quick
```

## 🔄 Recent Improvements

### **run_tests.py Enhancements**

#### **What Was Fixed**
- **Removed Hard-coded Environment Name**: No longer requires `'movedb-core-dev'` specifically
- **Flexible Environment Checking**: Works with any conda environment
- **Better Error Handling**: Warns instead of failing on environment issues
- **Removed Conflicting Configuration**: Fixed duplicate `pytest.ini` file

#### **How It Works Now**
```python
def check_environment():
    """Check if we're in a conda environment with required dependencies."""
    conda_env = os.environ.get('CONDA_DEFAULT_ENV')
    if not conda_env:
        print("⚠️  Warning: No conda environment detected")
        return True  # Don't fail, just warn
    
    # Check if pytest is available
    try:
        import pytest
        print(f"✅ Running in conda environment: {conda_env}")
        return True
    except ImportError:
        print(f"⚠️  Warning: pytest not available in environment '{conda_env}'")
        return False
```

## � IDE Integration

- VSCode settings documented in `docs/DEVELOPMENT.md`
- pytest configuration in `pyproject.toml` works with most IDEs
- Automatic test discovery and debugging support

## 🔧 What This Solves

1. **No more manual pytest setup** - Everything is pre-configured
2. **Consistent testing across developers** - Same environment for everyone  
3. **Easy test discovery** - Clear commands for different test scenarios
4. **IDE integration** - Works with VSCode, PyCharm, etc.
5. **CI/CD ready** - All tools configured for automation
6. **Environment flexibility** - Works with any properly configured environment
7. **Better error handling** - Helpful warnings instead of hard failures

## 🎯 Key Benefits

### ✅ **Flexible Environment Support**
- Works with any conda environment that has the required dependencies
- No hard-coded environment name requirements
- Automatic dependency checking and helpful warnings

### ✅ **Multiple Testing Approaches**
- Makefile commands for standard workflows
- Python script for custom options
- Direct pytest for advanced users
- IDE integration for interactive development

### ✅ **Quality Assurance**
- Comprehensive coverage reporting
- Code formatting and linting
- Type checking integration
- Consistent tool configuration

### ✅ **Developer Experience**
- Fast feedback with quick test options
- Clear documentation and examples
- Easy onboarding for new contributors
- Seamless CI/CD integration

Developers can now focus on writing tests and code instead of configuring tools!

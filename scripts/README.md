# Developer Scripts

This directory contains utility scripts for development, testing, and packaging of movedb-core.

## Build and Packaging Scripts

### `build_conda.sh`
Builds the conda package locally.
```bash
./scripts/build_conda.sh
```

### `validate_package.sh`
Validates the built conda package by installing it in a clean environment and running basic tests.
```bash
./scripts/validate_package.sh
```

### `setup_anaconda_integration.sh`
Interactive script to set up GitHub repository secrets for automatic conda package uploads to Anaconda.org.
```bash
./scripts/setup_anaconda_integration.sh
```

### `prepare_conda_forge.py`
Helps prepare the package for conda-forge submission by checking requirements and generating conda-forge recipe.
```bash
python scripts/prepare_conda_forge.py
```

### `check_v1_readiness.py`
Checks package readiness for v1.0.0 release by evaluating coverage, quality, documentation, and other metrics.
```bash
python scripts/check_v1_readiness.py
```

## Testing Scripts

### `run_tests.py`
Flexible test runner with options for coverage, specific test files, and patterns.
```bash
# Run all tests
python scripts/run_tests.py

# Run specific test file
python scripts/run_tests.py --file test_basic.py

# Run tests matching pattern
python scripts/run_tests.py --pattern trial

# Run without coverage (faster)
python scripts/run_tests.py --no-coverage
```

### `test_dev_setup.py`
Tests the development environment setup to ensure all dependencies are available.
```bash
python scripts/test_dev_setup.py
```

## Version Management

### `bump_version.py`
Automated version bumping with git tagging support.
```bash
# Bump patch version
python scripts/bump_version.py patch

# Bump minor version
python scripts/bump_version.py minor

# Bump major version
python scripts/bump_version.py major

# Bump to specific version
python scripts/bump_version.py 1.2.3

# Bump and create git tag
python scripts/bump_version.py patch --tag

# Bump, tag, and push
python scripts/bump_version.py patch --tag --push
```

## CI/CD Verification

### `verify_github_actions.py`
Validates GitHub Actions workflow files for syntax and configuration issues.
```bash
python scripts/verify_github_actions.py
```

## Usage from Project Root

All scripts are designed to be run from the project root directory:
```bash
# From project root
./scripts/build_conda.sh
python scripts/run_tests.py
python scripts/bump_version.py patch
```

## Integration with Makefile

Many of these scripts are integrated into the Makefile for easier access:
```bash
make build          # Uses scripts/build_conda.sh
make test           # Uses scripts/run_tests.py
make bump-patch     # Uses scripts/bump_version.py patch
make validate       # Uses scripts/validate_package.sh
```

See the main project `Makefile` for all available commands.

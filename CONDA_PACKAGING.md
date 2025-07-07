# MoveDB Core Conda Package Setup

This document describes the conda package setup for the movedb-core repository.

## 📁 Package Structure

The following files have been created/modified to enable conda packaging:

### Core Package Files
- `pyproject.toml` - Modern Python package configuration
- `src/movedb/__init__.py` - Package initialization with version and exports
- `LICENSE` - MIT license file
- `README.md` - Enhanced project description
- `MANIFEST.in` - Controls which files are included in the distribution

### Conda-Specific Files
- `conda-recipe/meta.yaml` - Conda build recipe
- `conda-recipe/conda_build_config.yaml` - Build configuration for multiple Python versions
- `environment.yml` - Development environment specification

### Build & Validation Scripts
- `build_conda.sh` - Automated conda package building script
- `validate_package.sh` - Package validation script
- `INSTALL.md` - Installation and upload instructions

### Development Files
- `.github/workflows/build.yml` - GitHub Actions CI/CD workflow
- `tests/test_basic.py` - Basic package tests
- `.gitignore` - Git ignore patterns

## 🔧 Dependencies

The package depends on the following conda packages:

### Runtime Dependencies
- `python >=3.8`
- `numpy >=1.20.0`
- `polars >=0.20.0`
- `pydantic >=2.0.0`
- `loguru >=0.6.0`
- `ezc3d >=1.5.0`
- `opensim-org::opensim >=4.0.0`

### Build Dependencies
- `hatchling` - Modern Python build backend
- `conda-build` - For building conda packages
- `conda-verify` - For validating conda packages

## 🚀 Building the Package

### Prerequisites
1. Install conda/miniconda
2. Install conda-build: `conda install conda-build`

### Build Process
```bash
# 1. Validate the package setup
./validate_package.sh

# 2. Build the conda package
./build_conda.sh

# 3. The package will be created in dist/conda/
```

### Manual Build
```bash
# Build for current platform
conda build conda-recipe --output-folder dist/conda

# Build for specific platform
conda build conda-recipe --output-folder dist/conda --python 3.11

# Build for multiple platforms
conda build conda-recipe --output-folder dist/conda --python 3.8 3.9 3.10 3.11 3.12
```

## 📦 Installation Options

### From Built Package
```bash
# Install locally built package
conda install dist/conda/noarch/movedb-core-0.1.0-*.tar.bz2

# Or with specific path
conda install /path/to/movedb-core-0.1.0-py_0.tar.bz2
```

### From Source (Development)
```bash
# Create development environment
conda env create -f environment.yml
conda activate movedb-core-dev

# Install in development mode
pip install -e .
```

## 🌐 Publishing Options

### Option 1: Conda-Forge (Recommended)
Conda-forge is the most popular conda channel for community packages.

1. Fork the [staged-recipes](https://github.com/conda-forge/staged-recipes) repository
2. Create a new recipe in `recipes/movedb-core/meta.yaml`
3. Submit a pull request
4. Once accepted, you'll get a dedicated feedstock repository

### Option 2: Anaconda.org
Upload to your personal anaconda.org account:

```bash
# Install anaconda-client
conda install anaconda-client

# Login to anaconda.org
anaconda login

# Upload the package
anaconda upload dist/conda/noarch/movedb-core-0.1.0-*.tar.bz2

# Users can then install with:
# conda install -c yourusername movedb-core
```

### Option 3: Private/Custom Channel
For internal or private distribution:

```bash
# Create a local channel
conda index /path/to/your/channel

# Add the channel
conda config --add channels file:///path/to/your/channel

# Install from custom channel
conda install movedb-core
```

## 🧪 Testing

### Basic Import Test
```bash
# Test basic import
python -c "import movedb; print(movedb.__version__)"

# Test core functionality
python -c "from movedb import Trial, Event; print('Import successful')"
```

### Run Full Test Suite
```bash
# Install test dependencies
pip install pytest

# Run tests
pytest tests/
```

## 🔄 Version Management

The package version is managed in three places:
1. `pyproject.toml` - Project configuration
2. `src/movedb/__init__.py` - Package initialization
3. `conda-recipe/meta.yaml` - Conda recipe

The validation script ensures all versions are consistent.

### Updating Version
1. Update version in `pyproject.toml`
2. Update version in `src/movedb/__init__.py`
3. Update version in `conda-recipe/meta.yaml`
4. Run `./validate_package.sh` to verify consistency

## 📋 Checklist for New Releases

- [ ] Update version numbers in all files
- [ ] Update `CHANGELOG.md` (if exists)
- [ ] Run `./validate_package.sh`
- [ ] Run `./build_conda.sh`
- [ ] Test the built package
- [ ] Create git tag: `git tag v0.1.0`
- [ ] Push to GitHub: `git push origin v0.1.0`
- [ ] Upload to conda-forge/anaconda.org

## 🔧 Troubleshooting

### Common Issues

1. **Import errors during build**
   - Check dependencies in `meta.yaml`
   - Ensure all required packages are available in conda

2. **Version mismatches**
   - Run `./validate_package.sh` to identify issues
   - Update all version references consistently

3. **Build failures**
   - Check conda-build logs for specific errors
   - Verify Python syntax with `python -m py_compile`

4. **Package not found after install**
   - Check package is in correct conda environment
   - Verify installation path with `conda list`

### Getting Help

- [Conda-build documentation](https://docs.conda.io/projects/conda-build/en/latest/)
- [Conda-forge documentation](https://conda-forge.org/docs/)
- [Python packaging guide](https://packaging.python.org/)

## 📝 Notes

- The package is configured as `noarch: python` for platform independence
- All dependencies are pinned to minimum versions for compatibility
- The build process supports Python 3.8-3.12
- Tests are run automatically in CI/CD pipeline

# Conda Packaging and Distribution

This document describes the conda packaging and automated distribution setup for movedb-core.

## Overview

The project uses conda for packaging and distribution, with automatic uploads to Anaconda.org through GitHub Actions CI/CD. This ensures reliable distribution of the package with all its dependencies, including `ezc3d` and `opensim` which are not available on PyPI.

## Package Structure

### Conda Recipe

The conda package is defined in `conda-recipe/meta.yaml`:

- **Package metadata**: Name, version, description, license
- **Dependencies**: Runtime and build dependencies
- **Build configuration**: Entry points, test commands
- **About section**: Documentation links, license info

### Build Configuration

`conda-recipe/conda_build_config.yaml` defines:
- Supported Python versions (3.8-3.12)
- Build matrix configuration
- Channel priorities

## Automated Distribution

### GitHub Actions Workflow

The CI/CD workflow (`/.github/workflows/ci-cd.yml`) includes two distribution jobs:

#### 1. Release Job (Tagged Releases)
- **Trigger**: Git tags matching `v*` (e.g., `v1.0.0`)
- **Action**: Uploads to main channel on Anaconda.org
- **Installation**: `conda install -c YOUR_USERNAME movedb-core`

#### 2. Upload Job (Main Branch)
- **Trigger**: Pushes to `main` branch
- **Action**: Uploads to `dev` channel on Anaconda.org
- **Installation**: `conda install -c YOUR_USERNAME -c dev movedb-core`

### Required Secrets

Configure these secrets in your GitHub repository settings:

1. **ANACONDA_USER**: Your Anaconda.org username
2. **ANACONDA_API_TOKEN**: API token with upload permissions

#### Creating an API Token

1. Go to [Anaconda.org](https://anaconda.org)
2. Sign in to your account
3. Navigate to: Account Settings → Access → API tokens
4. Create a new token with upload permissions
5. Copy the token (shown only once)

## Manual Building and Upload

### Local Build

```bash
# Install build dependencies
conda install -c conda-forge conda-build conda-verify

# Build package
./scripts/build_conda.sh

# Verify build
conda-verify dist/conda/**/*.conda
```

### Manual Upload

```bash
# Install anaconda-client
conda install -c conda-forge anaconda-client

# Login to anaconda.org
anaconda login

# Upload package
anaconda upload dist/conda/**/*.conda

# Upload to specific channel
anaconda upload --label dev dist/conda/**/*.conda
```

## Installation Methods

### For End Users

```bash
# Stable release
conda install -c YOUR_USERNAME movedb-core

# Development version
conda install -c YOUR_USERNAME -c dev movedb-core
```

### For Developers

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/movedb-core.git
cd movedb-core

# Create development environment
conda env create -f environment.yml
conda activate movedb-core-dev

# Install in development mode
pip install -e .
```

## Package Channels

- **Main channel**: Stable releases from tagged versions
- **Dev channel**: Development builds from main branch
- **Testing**: Local builds and testing

## Build Process

1. **Source preparation**: Code is packaged from the repository
2. **Dependency resolution**: Conda resolves all dependencies
3. **Build execution**: Package is built in isolated environment
4. **Testing**: Built package is tested with specified test commands
5. **Upload**: Package is uploaded to Anaconda.org

## Best Practices

### Version Management

- Use semantic versioning (e.g., `v1.0.0`)
- Tag releases properly for stable channel upload
- Development versions get automatic version suffixes

### Dependencies

- Specify exact dependency versions for reproducibility
- Use conda-forge channel for most dependencies
- Document any special dependency requirements

### Testing

- All packages are tested before upload
- CI/CD ensures quality before distribution
- Local testing available with `conda-verify`

## Troubleshooting

### Common Issues

1. **Build failures**: Check dependency versions in `meta.yaml`
2. **Upload failures**: Verify API token permissions
3. **Missing dependencies**: Ensure all deps are available in specified channels

### Debug Commands

```bash
# Check build log
conda build conda-recipe/ --debug

# List package contents
conda search --info movedb-core

# Check dependencies
conda inspect linkages movedb-core
```

## Monitoring

- Monitor build status in GitHub Actions
- Check package availability on Anaconda.org
- Monitor download statistics and feedback

## Security

- API tokens are stored as GitHub secrets
- Never commit tokens to repository
- Rotate tokens regularly
- Use least-privilege access for tokens

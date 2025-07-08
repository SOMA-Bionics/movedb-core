# GitHub Actions CI/CD

This document describes the complete GitHub Actions setup for automated testing, building, and deployment of movedb-core.

## Overview

The repository uses GitHub Actions for:

- **Continuous Integration**: Automated testing on every push/PR
- **Code Quality**: Linting, formatting, and security checks  
- **Automated Building**: Conda and wheel package building
- **Automated Deployment**: Package uploads to Anaconda.org
- **Fast Feedback**: Quick test runs for rapid development

## 🏗️ Workflow Files

### 1. Main CI/CD Pipeline (`.github/workflows/ci-cd.yml`)

**Triggers**:

- Push to `main`/`develop` branches
- Pull requests
- Version tags (`v*`)

**Jobs**:

#### **Test Job**

- Runs on Python 3.8-3.12 matrix
- Uses conda environment from `environment.yml`
- Generates coverage reports (uploads to Codecov)
- Tests explicit submodule imports

#### **Quality Job**

- Code formatting check (black)
- Import sorting check (isort)
- Linting (flake8)
- Type checking (mypy)
- Documentation linting (markdownlint)

#### **Security Job**

- Bandit security scanning
- Uploads security reports as artifacts

#### **Build Job**

- Builds conda packages using `scripts/build_conda.sh`
- Builds Python wheels
- Uploads packages as artifacts
- Only runs after tests and quality checks pass

#### **Documentation Job** (main branch only)

- Builds documentation if Sphinx config exists
- Uploads docs as artifacts

#### **Release Job** (tagged releases only)

- Downloads built packages
- Uploads conda packages to Anaconda.org main channel
- Creates GitHub releases with package attachments
- Requires `ANACONDA_USER` and `ANACONDA_API_TOKEN` secrets

#### **Upload Job** (main branch only)

- Uploads conda packages to Anaconda.org dev channel
- For development/pre-release testing

### 2. Simplified Tests (`.github/workflows/tests.yml`)

**Purpose**: Faster feedback for development
**Triggers**: Push/PR to main/develop

**Jobs**:

- **test**: Full test suite with coverage (Python 3.8-3.12)
- **quick-test**: Fast test run without coverage (Python 3.11 only)

## ✅ What's Working

### **Automatic Triggers**

```yaml
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
  release:
    types: [ published ]
```

### **Test Matrix**

```yaml
strategy:
  matrix:
    python-version: ['3.8', '3.9', '3.10', '3.11', '3.12']
```

### **Conda Environment Setup**

```yaml
- name: Set up Miniconda
  uses: conda-incubator/setup-miniconda@v3
  with:
    channels: conda-forge,opensim-org,defaults
    activate-environment: test-env
```

## 🔧 Required Secrets

Configure these in your GitHub repository settings:

| Secret | Purpose | Required For |
|--------|---------|--------------|
| `ANACONDA_USER` | Your Anaconda.org username | Package uploads |
| `ANACONDA_API_TOKEN` | Anaconda.org API token | Package uploads |
| `CODECOV_TOKEN` | Codecov integration token | Coverage reports (optional) |

### Setting Up Anaconda.org Integration

Use the setup script:

```bash
./scripts/setup_anaconda_integration.sh
```

Or manually:

1. Create API token at [anaconda.org](https://anaconda.org) → Account Settings → Access → API tokens
2. Add secrets in GitHub: Settings → Secrets and variables → Actions

## 🚀 Workflow Features

### **Smart Caching**

- Conda environments cached for faster builds
- pip cache for Python packages

### **Matrix Testing**

- Tests across Python 3.8-3.12
- Conda environments for reproducible testing

### **Artifact Management**

- 30-day retention for build artifacts
- Coverage reports and security scans
- Built packages available for download

### **Release Automation**

- Automatic package upload on version tags
- GitHub releases with changelog generation
- Both main and dev channel support

## Local Testing

Test your workflows locally:

```bash
# Run the same checks locally
make ci-check

# Build packages locally  
make build

# Test upload process
make build-upload-dev
```

## Monitoring

Monitor your workflows:

- **GitHub Actions tab**: Build status and logs
- **Codecov**: Coverage trends and reports
- **Anaconda.org**: Package downloads and versions

## Troubleshooting

### Common Issues

**Build Failures**:

- Check conda environment compatibility
- Verify all dependencies in `environment.yml`
- Test conda recipe locally: `make build`

**Upload Failures**:

- Verify Anaconda.org secrets are set correctly
- Check API token permissions
- Ensure package name matches Anaconda.org expectations

**Test Failures**:

- Run tests locally: `make test`
- Check for environment-specific issues
- Verify all imports work correctly

**Conda Environment Setup Failures**:

- Check that `environment.yml` is valid
- Ensure all channels are accessible
- Check for conflicting dependencies

**Tests Fail in CI but Pass Locally**:

- Check Python version differences
- Verify environment variables
- Check for missing dependencies

**Coverage Upload Failures**:

- Codecov token may be required for private repos
- Check that coverage.xml is generated

### Debugging

Enable workflow debugging:

1. Go to repository Settings → Secrets and variables → Actions
2. Add secret: `ACTIONS_STEP_DEBUG` = `true`
3. Re-run failed workflow for detailed logs

**Additional Debug Steps**:

- Check the Actions tab in your GitHub repository for detailed logs
- Look at the raw logs for each step
- Use `conda list` step to verify environment setup
- Add temporary debug steps to workflows for troubleshooting

## Setting Up in Your Repository

### 1. Repository Secrets (Optional)

For full functionality, you may want to set up these secrets in your GitHub repository:

- `CODECOV_TOKEN`: For coverage reporting (optional, public repos work without it)
- `PYPI_TOKEN`: For automatic PyPI publishing (if you plan to publish to PyPI)

### 2. Branch Protection

Consider setting up branch protection rules for `main`:

- Require status checks to pass before merging
- Require branches to be up to date before merging
- Require review from code owners

### 3. Codecov Integration

If you want detailed coverage reports:

1. Sign up at [codecov.io](https://codecov.io)
2. Connect your GitHub repository
3. The workflow will automatically upload coverage reports

## Local Testing Before Push

Before pushing code, you can run the same checks locally:

```bash
# Run all tests
make test

# Run code quality checks
make format-check
make lint

# Run specific test patterns
make test-pattern PATTERN=imports

# Quick test run
make test-quick
```

## Workflow Status

You can monitor workflow status:

- In the GitHub Actions tab of your repository
- Via status badges in the README
- Through email notifications (if enabled)

## Customization

### Modifying Test Matrix

Edit the `matrix.python-version` in the workflow files to test different Python versions:

```yaml
strategy:
  matrix:
    python-version: ['3.8', '3.9', '3.10', '3.11', '3.12']
```

### Adding New Checks

Add new jobs to the workflows or modify existing ones. For example, to add a new linting tool:

```yaml
- name: Lint with new-tool
  shell: bash -l {0}
  run: |
    conda activate test-env
    new-tool src/
```

### Conditional Jobs

Jobs can be made conditional based on events:

```yaml
# Only run on main branch
if: github.ref == 'refs/heads/main'

# Only run on pull requests
if: github.event_name == 'pull_request'

# Only run on version tags
if: startsWith(github.ref, 'refs/tags/v')
```

## Best Practices

1. **Test locally first**: Always run tests locally before pushing
2. **Keep workflows fast**: Use caching and minimize redundant steps
3. **Monitor resource usage**: GitHub Actions has usage limits
4. **Use appropriate triggers**: Don't run expensive workflows on every commit
5. **Document changes**: Update this file when modifying workflows

## Integration with Development Workflow

The GitHub Actions workflows integrate seamlessly with the development tools:

- Uses the same `environment.yml` as local development
- Runs the same `make` commands available locally
- Follows the same code quality standards
- Supports the same Python versions

### **Local Commands Mirror CI**

```bash
# Same commands work locally and in CI
make test-quick     # Fast tests
make test           # Full test suite with coverage
make test-pattern PATTERN=imports  # Pattern-based testing
make lint           # Code quality checks
make format         # Code formatting
```

### **Status Monitoring**

Your README includes status badges:

- ![Tests](https://github.com/SOMA-Bionics/movedb-core/actions/workflows/tests.yml/badge.svg)
- ![CI/CD](https://github.com/SOMA-Bionics/movedb-core/actions/workflows/ci-cd.yml/badge.svg)

## Key Benefits

### ✅ **Automatic Quality Assurance**

- Every push and PR is automatically tested
- Code quality is checked before merging
- Security vulnerabilities are detected early

### ✅ **Multi-Environment Testing**

- Tests run on Python 3.8-3.12
- Conda environment ensures consistency
- Same tools used locally and in CI

### ✅ **Fast Feedback**

- Quick test job provides rapid feedback
- Full test suite provides comprehensive coverage
- Failed tests prevent problematic merges

### ✅ **Professional Development**

- Status badges show project health
- Automated releases from version tags
- Documentation builds automatically

## API Integration Support

The workflows fully support the explicit submodule import strategy:

```python
# These imports are tested in CI
from movedb.core import Trial, Event, Points, Analogs
from movedb.file_io import C3DLoader, OpenSimExporter
```

The CI setup is designed to grow with your project and support future API expansions like `from movedb.api import TrialDB`.

## Summary

Your development workflow is now fully automated:

- **Write code** → **Push to GitHub** → **Tests run automatically** → **Get feedback** → **Merge with confidence**

This ensures consistency between local development and CI/CD environments, providing the foundation for reliable, high-quality software development with minimal manual intervention.

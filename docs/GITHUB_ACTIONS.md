# GitHub Actions CI/CD Setup

## Overview

The `movedb-core` repository now includes comprehensive GitHub Actions workflows for continuous integration and deployment. Tests will run automatically on every push and pull request.

## Workflows

### 1. Tests Workflow (`.github/workflows/tests.yml`)
**Triggers:** Push to main/develop, Pull requests

**What it does:**
- Runs tests on Python 3.8-3.12
- Generates coverage reports
- Uploads coverage to Codecov
- Includes a quick test job without coverage for faster feedback

**Jobs:**
- `test`: Full test suite with coverage across Python versions
- `quick-test`: Fast test run on Python 3.11 without coverage

### 2. CI/CD Workflow (`.github/workflows/ci-cd.yml`)
**Triggers:** Push to main/develop, Pull requests, Tags

**What it does:**
- Comprehensive testing across Python versions
- Code quality checks (black, flake8, mypy, isort)
- Security scanning with bandit
- Package building (conda + wheel)
- Documentation building
- Automatic releases on version tags

**Jobs:**
- `test`: Test suite with coverage
- `quality`: Code formatting, linting, and type checking
- `security`: Security vulnerability scanning
- `build`: Package building and artifact upload
- `docs`: Documentation building (main branch only)
- `release`: Automatic releases on version tags

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

## Troubleshooting

### Common Issues

1. **Conda environment setup fails**
   - Check that `environment.yml` is valid
   - Ensure all channels are accessible
   - Check for conflicting dependencies

2. **Tests fail in CI but pass locally**
   - Check Python version differences
   - Verify environment variables
   - Check for missing dependencies

3. **Coverage upload fails**
   - Codecov token may be required for private repos
   - Check that coverage.xml is generated

### Debug Actions

To debug workflow issues:
1. Check the Actions tab in your GitHub repository
2. Look at the raw logs for each step
3. Use `conda list` step to verify environment setup
4. Add debug steps to workflows temporarily

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

This ensures consistency between local development and CI/CD environments.

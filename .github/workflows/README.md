# GitHub Actions Status Badges

Add these badges to your README.md to show the status of your CI/CD pipelines:

## Test Status
```markdown
![Tests](https://github.com/SOMA-Bionics/movedb-core/actions/workflows/tests.yml/badge.svg)
```

## Full CI/CD Status
```markdown
![CI/CD](https://github.com/SOMA-Bionics/movedb-core/actions/workflows/ci-cd.yml/badge.svg)
```

## Coverage Status (if using Codecov)
```markdown
![Coverage](https://codecov.io/gh/SOMA-Bionics/movedb-core/branch/main/graph/badge.svg)
```

## Example Usage in README
```markdown
# MoveDB Core

![Tests](https://github.com/SOMA-Bionics/movedb-core/actions/workflows/tests.yml/badge.svg)
![CI/CD](https://github.com/SOMA-Bionics/movedb-core/actions/workflows/ci-cd.yml/badge.svg)
![Coverage](https://codecov.io/gh/SOMA-Bionics/movedb-core/branch/main/graph/badge.svg)

Your package description here...
```

## Workflow Details

### tests.yml
- Runs on: push to main/develop, pull requests
- Tests: Python 3.8-3.12
- Coverage: Uploaded to Codecov (Python 3.11 only)
- Quick test: Fast test run without coverage

### ci-cd.yml
- Comprehensive CI/CD pipeline
- Code quality checks (black, flake8, mypy)
- Security scanning (bandit)
- Package building (conda + wheel)
- Documentation building
- Automatic releases on tags

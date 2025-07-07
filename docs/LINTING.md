# Code Quality and Linting Guide

## Overview

This project uses several automated tools to maintain consistent code quality and style. All linting checks are enforced in the CI/CD pipeline.

## Linting Tools

### 1. Black (Code Formatter)
- **Purpose**: Automatically formats Python code
- **Configuration**: 127 character line length
- **Usage**: 
  ```bash
  black src/ tests/           # Format code
  black --check src/ tests/   # Check formatting
  make format                 # Via Makefile
  ```

### 2. isort (Import Sorter)
- **Purpose**: Sorts and organizes import statements
- **Configuration**: Black-compatible profile
- **Usage**: 
  ```bash
  isort src/ tests/              # Sort imports
  isort --check-only src/ tests/ # Check sorting
  make isort                     # Via Makefile
  ```

### 3. flake8 (Style Linter)
- **Purpose**: Checks code style and finds potential issues
- **Configuration**: Ignores E203 (conflicts with Black)
- **Usage**: 
  ```bash
  flake8 src/ tests/   # Run linting
  make flake8         # Via Makefile
  ```

### 4. mypy (Type Checker)
- **Purpose**: Static type checking
- **Configuration**: Ignores missing imports for external libraries
- **Usage**: 
  ```bash
  mypy src/movedb/   # Type check
  make mypy         # Via Makefile
  ```

## Development Workflow

### Before Committing
```bash
# Auto-fix formatting and import issues
make lint-fix

# Run all linting checks
make lint

# Quick test run
make test-quick

# Or run everything at once
make pre-commit
```

### Quick Fix Workflow
```bash
# If CI fails due to linting:
make lint-fix    # Auto-fix most issues
make lint        # Check remaining issues
git add -A && git commit -m "Fix linting issues"
```

### CI Check Locally
```bash
# Run the same checks as CI
make ci-check
```

## Configuration Files

### setup.cfg
```ini
[flake8]
max-line-length = 127
extend-ignore = E203,W503
exclude = .git,__pycache__,docs,build,dist
per-file-ignores = __init__.py:F401
```

### pyproject.toml
```toml
[tool.black]
line-length = 127

[tool.isort]
profile = "black"
line_length = 127

[tool.mypy]
python_version = "3.8"
ignore_missing_imports = true
```

## Common Issues

### Import Errors (F401)
- **Issue**: Unused imports in `__init__.py` files
- **Fix**: These are often intentional for API design (allowed in config)

### Line Length (E501)
- **Issue**: Lines longer than 127 characters
- **Fix**: Break long lines or let Black handle it

### Whitespace in Slices (E203)
- **Issue**: Black and flake8 disagree on slice spacing
- **Fix**: Ignored in config (E203 is disabled)

### Type Hints
- **Issue**: Missing type hints for external libraries
- **Fix**: Added to mypy ignore list in config

## Editor Integration

### VS Code
Install these extensions:
- Python (Microsoft)
- Black Formatter
- isort
- Pylance

### Settings (`.vscode/settings.json`):
```json
{
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.sortImports.provider": "isort",
    "editor.formatOnSave": true
}
```

### Pre-commit Hooks (Optional)
```yaml
# .pre-commit-config.yaml
repos:
- repo: https://github.com/psf/black
  rev: 23.3.0
  hooks:
  - id: black
- repo: https://github.com/pycqa/isort
  rev: 5.12.0
  hooks:
  - id: isort
- repo: https://github.com/pycqa/flake8
  rev: 6.0.0
  hooks:
  - id: flake8
```

## Makefile Commands Summary

| Command | Description |
|---------|-------------|
| `make lint` | Run all linting checks |
| `make lint-fix` | Auto-fix formatting and imports |
| `make format` | Format code with Black |
| `make isort` | Sort imports |
| `make flake8` | Run style linting |
| `make mypy` | Run type checking |
| `make pre-commit` | Full pre-commit workflow |
| `make ci-check` | Run CI checks locally |

## Tips

1. **Run `make lint-fix` frequently** during development
2. **Use `make pre-commit`** before pushing changes
3. **Configure your editor** for automatic formatting
4. **Check CI logs** if builds fail - they show exact linting errors
5. **Use type hints** where possible for better code quality

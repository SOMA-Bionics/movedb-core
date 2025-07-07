# Makefile for MoveDB Core Development

.PHONY: help install test test-quick test-verbose test-coverage clean lint format build docs

help:  ## Show this help message
	@echo "MoveDB Core Development Commands:"
	@echo "================================="
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Environment Setup
install:  ## Install package in development mode
	pip install -e .

install-dev:  ## Create conda environment and install package
	conda env create -f environment.yml
	conda activate movedb-core-dev
	pip install -e .

update-env:  ## Update conda environment
	conda env update -f environment.yml

##@ Testing
test:  ## Run all tests with coverage
	python scripts/run_tests.py

test-quick:  ## Run tests without coverage (faster)
	pytest --no-cov

test-verbose:  ## Run tests with verbose output
	pytest -v

test-coverage:  ## Run tests with coverage and HTML report
	pytest --cov=src/movedb --cov-report=html --cov-report=term-missing

test-specific:  ## Run specific test file (usage: make test-specific FILE=test_basic.py)
	python scripts/run_tests.py --file $(FILE)

test-pattern:  ## Run tests matching pattern (usage: make test-pattern PATTERN=trial)
	python scripts/run_tests.py --pattern $(PATTERN)

test-parallel:  ## Run tests in parallel (requires pytest-xdist)
	pytest -n auto

##@ Code Quality
lint:  ## Run all linting checks (flake8, mypy, black, isort)
	@echo "Running flake8..."
	flake8 src/ tests/
	@echo "Running mypy..."
	mypy src/movedb/ --ignore-missing-imports || true
	@echo "Checking black formatting..."
	black --check --diff src/ tests/
	@echo "Checking import sorting..."
	isort --check-only --diff src/ tests/
	@echo "✅ All linting checks passed!"

lint-fix:  ## Auto-fix linting issues (format + sort imports)
	@echo "Formatting code with black..."
	black src/ tests/
	@echo "Sorting imports with isort..."
	isort src/ tests/
	@echo "✅ Code formatted and imports sorted!"

format:  ## Format code with black
	black src/ tests/

format-check:  ## Check code formatting
	black --check --diff src/ tests/

isort:  ## Sort imports
	isort src/ tests/

isort-check:  ## Check import sorting
	isort --check-only --diff src/ tests/

flake8:  ## Run flake8 linting
	flake8 src/ tests/

mypy:  ## Run mypy type checking
	mypy src/movedb/ --ignore-missing-imports || true

pre-commit:  ## Run pre-commit checks (like CI)
	@echo "Running pre-commit checks..."
	$(MAKE) lint
	$(MAKE) test-quick
	@echo "✅ Pre-commit checks passed!"

##@ Build and Package
build:  ## Build conda package
	./scripts/build_conda.sh

build-wheel:  ## Build Python wheel
	python -m build

build-all:  ## Build both conda and wheel packages
	$(MAKE) build
	$(MAKE) build-wheel

validate:  ## Validate package installation
	./scripts/validate_package.sh

upload-conda:  ## Upload conda package to Anaconda.org (requires authentication)
	@echo "Uploading conda package to Anaconda.org..."
	anaconda upload dist/conda/**/*.conda

upload-conda-dev:  ## Upload conda package to dev channel
	@echo "Uploading conda package to dev channel..."
	anaconda upload --label dev dist/conda/**/*.conda

build-upload:  ## Build and upload conda package
	$(MAKE) build
	$(MAKE) upload-conda

build-upload-dev:  ## Build and upload conda package to dev channel
	$(MAKE) build
	$(MAKE) upload-conda-dev

setup-anaconda:  ## Set up Anaconda.org integration (GitHub secrets)
	./scripts/setup_anaconda_integration.sh

##@ Version Management
bump-patch:  ## Bump patch version (x.y.z -> x.y.z+1)
	python scripts/bump_version.py patch

bump-minor:  ## Bump minor version (x.y.z -> x.y+1.0)
	python scripts/bump_version.py minor

bump-major:  ## Bump major version (x.y.z -> x+1.0.0)
	python scripts/bump_version.py major

bump-version:  ## Bump to specific version (usage: make bump-version VERSION=1.2.3)
	python scripts/bump_version.py $(VERSION)

release-patch:  ## Bump patch version, tag, and push
	python scripts/bump_version.py patch --tag --push

release-minor:  ## Bump minor version, tag, and push
	python scripts/bump_version.py minor --tag --push

release-major:  ## Bump major version, tag, and push
	python scripts/bump_version.py major --tag --push

##@ Documentation
docs:  ## Generate documentation
	@echo "Documentation generation not yet implemented"

##@ Cleanup
clean:  ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -name "*.pyc" -delete

clean-conda:  ## Clean conda build artifacts
	conda build purge

##@ Development Shortcuts
dev-setup: install-dev  ## Full development setup
dev-test: lint-fix test  ## Full development testing pipeline (fix + test)
dev-quick: test-quick  ## Quick test run for development
ci-check: lint test  ## Run CI checks locally

# Default target
.DEFAULT_GOAL := help

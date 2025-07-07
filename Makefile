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
	python run_tests.py

test-quick:  ## Run tests without coverage (faster)
	pytest --no-cov

test-verbose:  ## Run tests with verbose output
	pytest -v

test-coverage:  ## Run tests with coverage and HTML report
	pytest --cov=src/movedb --cov-report=html --cov-report=term-missing

test-specific:  ## Run specific test file (usage: make test-specific FILE=test_basic.py)
	pytest tests/$(FILE) -v

test-pattern:  ## Run tests matching pattern (usage: make test-pattern PATTERN=trial)
	pytest -k "$(PATTERN)" -v

test-parallel:  ## Run tests in parallel (requires pytest-xdist)
	pytest -n auto

##@ Code Quality
lint:  ## Run linting checks
	flake8 src/ tests/
	mypy src/movedb/

format:  ## Format code with black
	black src/ tests/

format-check:  ## Check code formatting
	black --check src/ tests/

##@ Build and Package
build:  ## Build conda package
	bash build_conda.sh

build-wheel:  ## Build Python wheel
	python -m build

validate:  ## Validate package installation
	bash validate_package.sh

##@ Version Management
bump-patch:  ## Bump patch version (x.y.z -> x.y.z+1)
	python bump_version.py patch

bump-minor:  ## Bump minor version (x.y.z -> x.y+1.0)
	python bump_version.py minor

bump-major:  ## Bump major version (x.y.z -> x+1.0.0)
	python bump_version.py major

bump-version:  ## Bump to specific version (usage: make bump-version VERSION=1.2.3)
	python bump_version.py $(VERSION)

release-patch:  ## Bump patch version, tag, and push
	python bump_version.py patch --tag --push

release-minor:  ## Bump minor version, tag, and push
	python bump_version.py minor --tag --push

release-major:  ## Bump major version, tag, and push
	python bump_version.py major --tag --push

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
dev-test: format lint test  ## Full development testing pipeline
dev-quick: test-quick  ## Quick test run for development

# Default target
.DEFAULT_GOAL := help

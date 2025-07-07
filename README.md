# MoveDB Core

[![Tests](https://github.com/SOMA-Bionics/movedb-core/actions/workflows/tests.yml/badge.svg)](https://github.com/SOMA-Bionics/movedb-core/actions/workflows/tests.yml)
[![CI/CD](https://github.com/SOMA-Bionics/movedb-core/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/SOMA-Bionics/movedb-core/actions/workflows/ci-cd.yml)
[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Core library for movement database operations, including C3D file I/O and OpenSim integration.

## Features

- **C3D File I/O**: Read and process C3D motion capture files
- **OpenSim Integration**: Export data to OpenSim formats (TRC, MOT, XML)
- **Time Series Processing**: Handle marker trajectories and analog data
- **Force Platform Support**: Process force platform data from C3D files
- **Data Validation**: Built-in data validation and gap detection
- **Type Safety**: Full type hints and Pydantic models for data integrity

## Installation

### From Conda (Recommended)

```bash
conda install -c conda-forge movedb-core
```

**Note**: We strongly recommend using conda, as key dependencies (`ezc3d`, `opensim`) are not available on PyPI.


### From PyPI (Limited Support)

```bash
# WARNING: This will NOT work out of the box!
# ezc3d and opensim are only available via conda
# You'll need to manually compile these dependencies
pip install movedb-core
```

### From Source

```bash
git clone https://github.com/SOMA-Bionics/movedb-core.git
cd movedb-core

# Using conda for dependencies (REQUIRED)
conda env create -f environment.yml
conda activate movedb-core-dev
pip install -e .
```

## Quick Start

```python
from movedb.core import Trial

# Load a C3D file
trial = Trial.from_c3d_file("path/to/your/file.c3d")

# Access marker data
markers = trial.points.trajectories
print(f"Loaded {len(markers)} markers")

# Access force platform data
if trial.force_platforms:
    print(f"Found {len(trial.force_platforms)} force platforms")

# Export to OpenSim TRC format
trial.to_trc("output.trc")

# Run OpenSim Inverse Kinematics
trial.run_opensim_ik("model.osim", output_dir="ik_results")
```

## API Structure

The `movedb` package is organized into logical submodules for clear separation of concerns:

- `movedb.core`: Core data structures and classes
- `movedb.file_io`: File input/output functionality
- `movedb.utils`: Utility functions

You can import classes using explicit submodule imports:
```python
from movedb.core import Trial, Event, Points, Analogs
from movedb.file_io import C3DLoader, OpenSimExporter
```

This approach provides clear API structure and supports future expansion (e.g., `from movedb.api import TrialDB`).

## Development

### Quick Development Setup
```bash
# Clone and set up environment
git clone https://github.com/SOMA-Bionics/movedb-core.git
cd movedb-core
conda env create -f environment.yml
conda activate movedb-core-dev
pip install -e .
```

### Running Tests
```bash
# Quick test run
make test-quick

# Full test suite with coverage
make test

# Run specific test file
make test-specific FILE=test_basic.py

# Run tests matching pattern
make test-pattern PATTERN=trial

# Alternative: use Python runner
python run_tests.py
```

### Code Quality
```bash
# Run all linting checks (like CI)
make lint

# Auto-fix formatting and import issues
make lint-fix

# Pre-commit checks (lint + test)
make pre-commit
```

### Available Make Commands
- `make test` - Run all tests with coverage
- `make test-quick` - Run tests without coverage (faster)
- `make lint` - Run all linting checks (black, isort, flake8, mypy)
- `make lint-fix` - Auto-fix formatting and import sorting
- `make format` - Format code with black
- `make build` - Build conda package
- `make clean` - Clean build artifacts
- `make help` - Show all available commands

See `docs/DEVELOPMENT.md` for detailed development guidelines and `docs/LINTING.md` for code quality information.

## Core Classes

- `Trial`: Main container for motion capture trial data
- `Points`: Marker trajectory data with gap detection
- `Analogs`: Analog channel data (EMG, force platforms, etc.)
- `Event`: Trial events with timing information
- `EZC3DForcePlatform`: Force platform data container based on ezc3d's force platform filter

## Requirements

- Python 3.8+
- numpy >= 1.20.0
- polars >= 0.20.0
- pydantic >= 2.0.0
- loguru >= 0.6.0
- ezc3d >= 1.5.0 *(conda-forge only)*
- opensim >= 4.0.0 *(opensim-org only)*

**Note**: This package requires conda for installation due to dependencies that are not available on PyPI.

## Development

```bash
# Clone the repository
git clone https://github.com/SOMA-Bionics/movedb-core.git
cd movedb-core

# Create conda environment with dependencies (REQUIRED)
conda env create -f environment.yml
conda activate movedb-core-dev
pip install -e ".[dev]"

# Alternative: Manual setup
conda create -n movedb-dev python=3.11
conda activate movedb-dev
conda install -c conda-forge numpy polars pydantic loguru ezc3d
pip install -e ".[dev]"
```

**Important**: Pure pip development is not supported due to conda-only dependencies.

Run tests:
```bash
pytest
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

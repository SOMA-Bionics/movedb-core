# MoveDB Core - API Design and Import Strategy

## Summary

The `movedb-core` package has been successfully configured with a clear API structure that supports both explicit submodule imports and backward-compatible flat imports.

## API Structure

### Explicit Submodule Imports (Recommended)

```python
from movedb.core import Trial, Event, Points, Analogs
from movedb.file_io import C3DLoader, OpenSimExporter
from movedb.utils import utility_functions
```

### Flat Imports (Backward Compatible)

```python
from movedb import Trial, Event, Points, Analogs
from movedb import C3DLoader, OpenSimExporter, sto_to_df, parse_enf_file
```

## Recent Changes (v0.1.3)

### File I/O Module Reorganization

OpenSim file reading functions have been moved to the appropriate module:

**New Location (Recommended):**

```python
from movedb.file_io import sto_to_df, parse_enf_file
```

**Old Location (Deprecated):**

```python
from movedb.utils import sto_to_df, parse_enf_file  # Will show deprecation warning
```

**Benefits:**

- Logical organization: File I/O functions are now in the `file_io` module
- Clearer API structure: Separates utilities from file operations
- Better maintainability: Related functionality is grouped together

## Benefits of Explicit Submodule Imports

1. **Clear API Structure**: Makes it obvious which functionality belongs to which module
2. **Future Extensibility**: Supports planned expansion like `from movedb.api import TrialDB`
3. **Namespace Management**: Reduces potential naming conflicts
4. **Better Documentation**: API structure is self-documenting

## Implementation Details

### Package Structure

```
src/movedb/
├── __init__.py          # Re-exports main classes for flat imports
├── core/                # Core data structures and business logic
│   ├── __init__.py
│   ├── trial.py
│   ├── events.py
│   ├── time_series.py
│   └── ...
├── file_io/             # File I/O operations
│   ├── __init__.py
│   ├── c3d_io.py
│   ├── opensim_exporters.py
│   └── ...
└── utils/               # Utility functions
    ├── __init__.py
    └── utils.py
```

### Main Package `__init__.py`

The main `__init__.py` file:

- Re-exports main classes from submodules for backward compatibility
- Provides version information
- Supports both import styles without breaking existing code

### Test Coverage

All import patterns are tested:

- Explicit submodule imports: `from movedb.core import Trial`
- Flat imports: `from movedb import Trial`
- Basic functionality verification
- Conda package building and installation

## Migration Path

For existing code using flat imports:

- No changes required - backward compatibility maintained
- Gradual migration to explicit imports can be done when convenient

For new code:

- Use explicit submodule imports for clarity
- Follow the documented API structure

## Future API Expansion

The structure is designed to support planned features like:

```python
from movedb.api import TrialDB        # Database operations
from movedb.analysis import analyze   # Analysis functions
from movedb.visualization import plot # Plotting functions
```

This approach provides a clean, extensible, and user-friendly API that grows with the project's needs.

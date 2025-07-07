"""
MoveDB Core - Movement Database Core Library

A Python library for handling movement/biomechanics data including:
- C3D file I/O operations
- OpenSim integration
- Time series data processing
- Motion capture data management
"""

__version__ = "0.1.1"
__author__ = "Hudson Burke"
__email__ = "hudsonburke01@gmail.com"

# Import main classes for easy access
from .core import (
    MISSING,
    MISSING_LIST,
    UNSET,
    AnalogChannel,
    Analogs,
    Event,
    EZC3DForcePlatform,
    ImportMethod,
    MarkerTrajectory,
    OpenSimOutput,
    Points,
    Sentinel,
    TimeSeriesGroup,
    Trial,
)
from .file_io import C3DLoader, OpenSimExporter
from .utils import snake_to_pascal, sto_to_df

__all__ = [
    # Core classes
    "Trial",
    "Event",
    "Points",
    "Analogs",
    "MarkerTrajectory",
    "AnalogChannel",
    "EZC3DForcePlatform",
    "TimeSeriesGroup",
    # Enums
    "ImportMethod",
    "OpenSimOutput",
    # Sentinels
    "Sentinel",
    "MISSING",
    "MISSING_LIST",
    "UNSET",
    # File I/O
    "C3DLoader",
    "OpenSimExporter",
    # Utilities
    "sto_to_df",
    "snake_to_pascal",
]

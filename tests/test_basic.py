"""Basic tests for movedb-core package."""

import pytest

from movedb.core import Event, ImportMethod, Trial


def test_imports():
    """Test that main classes can be imported."""
    from movedb.core import Analogs, Event, ImportMethod, Points, Trial
    from movedb.file_io import C3DLoader, OpenSimExporter

    # Test that classes are available
    assert Event is not None
    assert Trial is not None
    assert Points is not None
    assert Analogs is not None
    assert ImportMethod is not None
    assert C3DLoader is not None
    assert OpenSimExporter is not None


def test_version():
    """Test that version is accessible."""
    import movedb

    assert hasattr(movedb, "__version__")
    assert isinstance(movedb.__version__, str)


def test_event_creation():
    """Test basic Event creation."""
    event = Event(label="heel_strike", frame=100, context="left")
    assert event.label == "heel_strike"
    assert event.frame == 100
    assert event.context == "left"


def test_trial_creation():
    """Test basic Trial creation with minimal data."""
    import polars as pl

    from movedb import AnalogChannel, Analogs, MarkerTrajectory, Points

    # Create minimal marker data
    marker_data = pl.DataFrame(
        {
            "x": [1.0, 2.0, 3.0],
            "y": [1.0, 2.0, 3.0],
            "z": [1.0, 2.0, 3.0],
            "residual": [0.0, 0.0, 0.0],
        }
    )

    marker_traj = MarkerTrajectory(data=marker_data, description="test_marker")

    points = Points(
        trajectories={"test_marker": marker_traj},
        first_frame=0,
        last_frame=2,
        rate=100.0,
        units="mm",
    )

    # Create minimal analog data
    analog_channel = AnalogChannel(
        data=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6], units="V", description="test_analog"
    )

    analogs = Analogs(
        channels={"test_analog": analog_channel},
        first_frame=0,
        last_frame=5,
        rate=1000.0,
    )

    # Create trial
    trial = Trial(
        name="test_trial",
        import_method=ImportMethod.C3D,
        points=points,
        analogs=analogs,
    )

    assert trial.name == "test_trial"
    assert trial.import_method == ImportMethod.C3D
    assert "test_marker" in trial.points.trajectories
    assert "test_analog" in trial.analogs.channels


if __name__ == "__main__":
    pytest.main([__file__])

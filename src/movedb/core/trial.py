"""
Refactored Trial class with improved separation of concerns.
"""

import os
import pickle
from typing import Any, Type, TypeVar

import polars as pl
from pydantic import BaseModel, model_validator

from .enums import ImportMethod
from .events import Event
from .force_platforms import EZC3DForcePlatform
from .time_series import Analogs, Points

# Define a TypeVar that is bound by the Trial class itself
_T = TypeVar("_T", bound="Trial")


class Trial(BaseModel):
    """
    Main trial data container with improved separation of concerns.
    File I/O and OpenSim operations are handled by separate classes.
    """

    # Trial Metadata
    name: str
    session_name: str | None = None
    subject_names: list[str] | str | None = None
    classification: str = ""
    trial_type: str | None = None
    import_method: ImportMethod
    linked_files: dict[str, str] = (
        {}
    )  # Map of associated files, e.g. C3D file path, etc.
    parameters: dict[str, Any] = {}

    events: list[Event] = []  # Should be in ascending order by frame or time

    points: Points
    point_gaps: dict[str, list[tuple[int, int]]] = {}

    analogs: Analogs
    force_platforms: list[EZC3DForcePlatform] = []  # List of force platforms, if any

    def get_events(self, label: str = "", context: str = "") -> list[Event]:
        """
        Return a copy of the events list filtered by label and context.
        If label or context is empty, it will not filter by that parameter.
        """
        return [
            event
            for event in self.events
            if (not label or event.label == label)
            and (not context or event.context == context)
        ]

    @model_validator(mode="after")
    def order_events(self) -> "Trial":
        """
        Ensure events are in ascending order by frame or time.
        """
        self.events = sorted(
            self.events,
            key=lambda e: (e.get_frame(self.points.rate), e.get_time(self.points.rate)),
        )
        return self

    def link_file(self, file_key: str, file_path: str):
        """Link a file to this trial by storing its absolute path."""
        self.linked_files[file_key] = os.path.abspath(file_path)

    def get_linked_file(self, file_key: str) -> str:
        """
        Get the absolute path of an associated file by its key.
        Returns an empty string if the file is not associated.
        """
        return self.linked_files.get(file_key, "")

    def check_point_gaps(
        self,
        marker_names: list[str] | None = None,
        regions: list[tuple[int, int] | tuple[float, float]] | None = None,
    ) -> dict[str, list[tuple[int, int]]]:
        """
        Check for gaps in point data for specified markers and regions.
        A gap is defined as any frame in the region where the marker data is missing (NaN).
        Returns a dictionary with marker names as keys and lists of (start, end) tuples indicating integer frame gaps.

        If no markers or regions are specified, checks all markers and the entire trial duration.
        If already computed, return the cached result.
        """

        if self.point_gaps:
            # Check for markers and regions already computed
            relevant_gaps = {}
            for marker, gap_list in self.point_gaps.items():
                if marker not in relevant_gaps:
                    relevant_gaps[marker] = []
                relevant_gaps[marker].extend(gap_list)
            return relevant_gaps

        gaps = {}
        if marker_names is None:
            marker_names = list(self.points.trajectories.keys())
        if regions is None:
            regions = [(self.points.first_frame, self.points.last_frame)]

        for region in regions:
            start, end = region
            if isinstance(start, float):
                start = int(start * self.points.rate)
            if isinstance(end, float):
                end = int(end * self.points.rate)
            for marker in marker_names:
                if marker not in self.points.trajectories:
                    gaps[marker] = [(start, end)]
                    continue
                marker_data = self.points.trajectories[marker].data
                # Check if marker data exists in every frame in the region
                region_data = marker_data[start : end + 1]
                for coord in ["x", "y", "z"]:
                    missing_data = region_data.filter(pl.col(coord).is_null())
                    if not missing_data.is_empty():
                        if marker not in gaps:
                            gaps[marker] = []
                        gaps[marker].append((start, end))
                        break
        return gaps

    @model_validator(mode="after")
    def _cache_point_gaps(self) -> "Trial":
        """Cache point gaps on initialization."""
        self.point_gaps = self.check_point_gaps()
        return self

    def find_full_frames(self, marker_names: list[str] | None = None) -> list[int]:
        """
        Find all frames where all specified markers have data.
        If no markers are specified, checks all markers.
        Returns a list of frame indices.
        """
        if marker_names is None:
            marker_names = list(self.points.trajectories.keys())
        full_frames = set(range(self.points.first_frame, self.points.last_frame + 1))
        for marker in marker_names:
            if marker not in self.points.trajectories:
                return []
            marker_data = self.points.trajectories[marker].data
            marker_full_frames = set(
                marker_data.filter(
                    (pl.col("x").is_not_null())
                    & (pl.col("y").is_not_null())
                    & (pl.col("z").is_not_null())
                )
                .select(pl.arange(0, marker_data.height))
                .to_series()
                .to_list()
            )
            full_frames &= marker_full_frames
        return sorted(full_frames)

    # Factory methods for creating Trial instances
    @classmethod
    def from_c3d(
        cls: Type[_T],
        c3d_object,
        trial_name: str = "",
        session_name: str = "",
        classification: str = "",
    ) -> _T:
        """
        Create a Trial instance from a C3D object.
        """
        from ..file_io import C3DLoader

        trial_data = C3DLoader.load_from_c3d_object(
            c3d_object, trial_name, session_name, classification
        )
        return cls(**trial_data)

    @classmethod
    def from_c3d_file(cls: Type[_T], file_path: str) -> _T:
        """
        Create a Trial instance from a C3D file.
        """
        from ..file_io import C3DLoader

        trial_data = C3DLoader.load_from_file(file_path)
        return cls(**trial_data)

    @classmethod
    def from_pkl(cls: Type[_T], path: str) -> _T:
        """
        Load a Trial from a pickle file.
        Args:
            path (str): Path to the pickle file.
        Returns:
            Trial: The loaded Trial object.
        """
        with open(path, "rb") as f:
            data = pickle.load(f)
        if not isinstance(data, cls):
            raise ValueError(f"Loaded data is not an instance of {cls}: {type(data)}")
        return data

    @classmethod
    def from_vicon_nexus(cls) -> "Trial":
        """
        Create a Trial instance from an open trial in Vicon Nexus.
        This method requires the Vicon Nexus API to be installed and configured.
        https://pycgm2.readthedocs.io/en/latest/Pages/thirdParty/NexusAPI.html
        """
        raise NotImplementedError("Vicon Nexus API integration is not implemented yet.")

    # Export functionality
    def get_opensim_exporter(self):
        """Get an OpenSim exporter for this trial."""
        from ..file_io import OpenSimExporter

        return OpenSimExporter(self)

    def to_trc(self, filepath: str, **kwargs):
        """Export marker data to TRC format. Convenience method."""
        exporter = self.get_opensim_exporter()
        exporter.to_trc(filepath, **kwargs)

    def export_force_platforms(
        self, output_dir: str, applied_bodies: dict[int, str], **kwargs
    ):
        """Export force platforms to OpenSim format. Convenience method."""
        exporter = self.get_opensim_exporter()
        exporter.export_force_platforms(output_dir, applied_bodies, **kwargs)

    def run_opensim_ik(self, model_path: str, **kwargs):
        """Run OpenSim Inverse Kinematics. Convenience method."""
        exporter = self.get_opensim_exporter()
        exporter.run_inverse_kinematics(model_path, **kwargs)

    def run_opensim_id(self, model_path: str, **kwargs):
        """Run OpenSim Inverse Dynamics. Convenience method."""
        exporter = self.get_opensim_exporter()
        exporter.run_inverse_dynamics(model_path, **kwargs)

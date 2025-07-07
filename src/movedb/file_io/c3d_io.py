"""C3D file I/O operations."""

import os
from typing import TypeVar

import ezc3d
import numpy as np
import polars as pl
from loguru import logger

from ..core import (
    AnalogChannel,
    Analogs,
    Event,
    EZC3DForcePlatform,
    ImportMethod,
    MarkerTrajectory,
    Points,
)

# Define a TypeVar that is bound by any class that has the required structure
_T = TypeVar("_T")


class C3DLoader:
    """Handles loading trial data from C3D files."""

    @staticmethod
    def _get_c3d_param(c3d_object: ezc3d.c3d, *keys, default=None):
        """
        Helper function to get nested parameters from a C3D object.
        """
        param = c3d_object.parameters
        for key in keys:
            param = param.get(key, {})
        return param.get("value", default)

    @classmethod
    def load_from_c3d_object(
        cls,
        c3d_object: ezc3d.c3d,
        trial_name: str = "",
        session_name: str = "",
        classification: str = "",
    ) -> dict:
        """
        Extract trial data from a C3D object and return as a dictionary.
        This returns the raw data that can be used to construct a Trial object.
        """
        c3d_header = c3d_object.header
        c3d_parameters = c3d_object.parameters
        c3d_data = c3d_object.data

        # Header
        points_rate = c3d_header["points"]["frame_rate"]
        points_first_frame = c3d_header["points"]["first_frame"]
        points_last_frame = c3d_header["points"]["last_frame"]

        analogs_rate = c3d_header["analogs"]["frame_rate"]
        analogs_first_frame = c3d_header["analogs"]["first_frame"]
        analogs_last_frame = c3d_header["analogs"]["last_frame"]

        # Parameters
        # TRIAL
        camera_rate = cls._get_c3d_param(
            c3d_object, "TRIAL", "CAMERA_RATE", default=None
        )
        if camera_rate != points_rate:
            logger.warning(
                f"Camera rate {camera_rate} does not match points rate {points_rate} in header"
            )

        subject_names = cls._get_c3d_param(c3d_object, "SUBJECTS", "NAMES", default=[])

        # FORCE_PLATFORM - Using ezc3d's force platform filter
        c3d_force_platforms = c3d_data["platform"]
        force_platforms = []  # Reset force platforms
        for fp in c3d_force_platforms:
            # Convert to EZC3DForcePlatform
            force = fp.get("force", [[]])
            moment = fp.get("moment", [[]])
            position = fp.get("center_of_pressure", [[]])
            free_moment = fp.get("Tz", [])
            ezc3d_fp = EZC3DForcePlatform(
                unit_force=fp.get("unit_force", "N"),
                unit_moment=fp.get("unit_moment", "Nm"),
                unit_position=fp.get("unit_position", "m"),
                cal_matrix=np.array(fp.get("cal_matrix", np.eye(6))),
                corners=np.array(fp.get("corners", np.zeros((4, 3)))),
                origin=np.array(fp.get("origin", np.zeros(3))),
                data=pl.DataFrame(
                    {
                        "force_x": force[0, :],
                        "force_y": force[1, :],
                        "force_z": force[2, :],
                        "moment_x": moment[0, :],
                        "moment_y": moment[1, :],
                        "moment_z": moment[2, :],
                        "center_of_pressure_x": position[0, :],
                        "center_of_pressure_y": position[1, :],
                        "center_of_pressure_z": position[2, :],
                        "free_moment_x": free_moment[0, :],
                        "free_moment_y": free_moment[1, :],
                        "free_moment_z": free_moment[2, :],
                    }
                ),
            )
            force_platforms.append(ezc3d_fp)

        # EVENT_CONTEXT - not currently using
        # EVENT
        events = []
        if "EVENT" in c3d_parameters:
            event_params: dict = c3d_parameters["EVENT"]
            num_events = event_params.get("USED", {}).get("value", [0])[0]
            event_contexts = event_params.get("CONTEXTS", {}).get("value", [])
            event_labels = event_params.get("LABELS", {}).get("value", [])
            event_descriptions = event_params.get("DESCRIPTIONS", {}).get("value", [])
            # event_subjects = event_params.get('SUBJECTS', {}).get('value', [])
            event_times = event_params.get("TIMES", {}).get("value", [])
            for i in range(num_events):
                events.append(
                    Event(
                        label=event_labels[i],
                        context=event_contexts[i],
                        time=event_times[0][i] * 60
                        + event_times[1][i],  # Convert from (min, sec) to sec
                        description=event_descriptions[i],
                    )
                )

        # MANUFACTURER - not currently using
        # ANALYSIS - These are mainly STPs from Vicon Nexus, so I think I'll just compute myself
        # also because they don't really follow the convention of the c3d format

        # PROCESSING
        parameters = {}
        if "PROCESSING" in c3d_parameters:
            for key, value in c3d_parameters["PROCESSING"].items():
                arr = value.get("value", None)
                if arr is not None and len(arr) == 1:
                    parameters[key] = arr[0]
                else:
                    parameters[key] = arr

        # Data
        # Points
        trajectories = {}
        point_rate_param = cls._get_c3d_param(c3d_object, "POINT", "RATE", default=None)
        if point_rate_param != points_rate:
            logger.warning(
                f"Point rate {point_rate_param} does not match header rate {points_rate}"
            )
        point_data = c3d_data["points"]  # 4xNxM (XYZ1, labels, num_frames)
        residuals = c3d_data["meta_points"]["residuals"]  # 1xNxM
        point_labels = cls._get_c3d_param(c3d_object, "POINT", "LABELS", default=[])
        point_descriptions = cls._get_c3d_param(
            c3d_object, "POINT", "DESCRIPTIONS", default=[]
        )
        point_units = cls._get_c3d_param(c3d_object, "POINT", "UNITS", default=["mm"])[
            0
        ]

        # if point_scale != 1: # TODO: Figure out what to do with this
        #     logger.warning(f"Point scale {point_scale} is not 1. Scaling point data accordingly.")
        #     point_data = point_data * point_scale
        for i, label in enumerate(point_labels):
            # Create MarkerTrajectory from the data
            trajectory = MarkerTrajectory(
                x=point_data[0, i, :].tolist(),
                y=point_data[1, i, :].tolist(),
                z=point_data[2, i, :].tolist(),
                residual=residuals[0, i, :].tolist(),
                description=(
                    point_descriptions[i] if i < len(point_descriptions) else ""
                ),
            )
            trajectories[label] = trajectory

        # Analogs
        channels = {}
        analog_rate_param = cls._get_c3d_param(
            c3d_object, "ANALOG", "RATE", default=None
        )
        if analog_rate_param != analogs_rate:
            logger.warning(
                f"Analog rate {analog_rate_param} does not match header rate {analogs_rate}"
            )
        analog_data = c3d_data["analogs"]  # 1xMxP (data, labels, num_frames)
        analog_units = cls._get_c3d_param(c3d_object, "ANALOG", "UNITS", default=[])
        analog_descriptions = cls._get_c3d_param(
            c3d_object, "ANALOG", "DESCRIPTIONS", default=[]
        )
        analog_labels = cls._get_c3d_param(c3d_object, "ANALOG", "LABELS", default=[])
        analog_offsets = cls._get_c3d_param(
            c3d_object, "ANALOG", "OFFSET", default=np.zeros(len(analog_labels))
        )
        analog_scales = cls._get_c3d_param(
            c3d_object, "ANALOG", "SCALE", default=np.ones(len(analog_labels))
        )
        analog_gen_scale = cls._get_c3d_param(
            c3d_object, "ANALOG", "GEN_SCALE", default=[1.0]
        )[0]

        for i, label in enumerate(analog_labels):
            channels[label] = AnalogChannel(
                data=analog_data[0, i, :].tolist(),  # Convert to list for compatibility
                units=analog_units[i] if i < len(analog_units) else "",
                description=(
                    analog_descriptions[i] if i < len(analog_descriptions) else ""
                ),
                scale=analog_scales[i] if i < len(analog_scales) else 1.0,
                offset=analog_offsets[i] if i < len(analog_offsets) else 0.0,
            )

        return {
            "name": trial_name,
            "session_name": session_name,
            "subject_names": subject_names,
            "classification": classification,
            "import_method": ImportMethod.C3D,
            "parameters": parameters,
            "events": events,
            "points": Points(
                first_frame=points_first_frame,
                last_frame=points_last_frame,
                rate=points_rate,
                units=point_units,
                trajectories=trajectories,
            ),
            "analogs": Analogs(
                first_frame=analogs_first_frame,
                last_frame=analogs_last_frame,
                rate=analogs_rate,
                channels=channels,
                gen_scale=analog_gen_scale,
            ),
            "force_platforms": force_platforms,
        }

    @classmethod
    def load_from_file(cls, file_path: str) -> dict:
        """
        Load trial data from a C3D file and return as a dictionary.
        """
        # Check that the file exists and is a valid C3D file
        file_path = os.path.normpath(file_path)
        if not file_path.endswith(".c3d"):
            raise ValueError("File must be a C3D file.")
        try:
            c3d_object = ezc3d.c3d(file_path, extract_forceplat_data=True)
        except Exception as e:
            logger.error(f"Failed to read C3D file {file_path}: {e}")
            c3d_object = ezc3d.c3d()
            # raise ValueError(f"Invalid C3D file: {file_path}") from e
        split_path = file_path.split(os.sep)
        trial_name = split_path[-1].replace(".c3d", "")
        session_name = split_path[-2] if len(split_path) > 1 else ""
        classification = split_path[-4] if len(split_path) > 3 else ""

        trial_data = cls.load_from_c3d_object(
            c3d_object,
            trial_name=trial_name,
            session_name=session_name,
            classification=classification,
        )
        # Add the file path to linked files
        trial_data["linked_files"] = {"c3d": file_path}
        return trial_data

"""Enums for biomechanical trial data."""

from enum import Enum


class ImportMethod(str, Enum):
    C3D = "C3D"
    VICON_NEXUS = "Vicon Nexus"
    CUSTOM = "Custom"


class OpenSimOutput(str, Enum):
    """
    Enum for OpenSim output types.
    """

    SCALED_MODEL = "scaled_model"
    MARKER_MODEL = "marker_model"
    TRC = "trc"
    IK_SETUP = "ik_setup"
    IK = "ik_results"
    ID_SETUP = "id_setup"
    ID = "id_results"
    FP_MOT = "fp_mot"
    FP_SETUP = "fp_setup"

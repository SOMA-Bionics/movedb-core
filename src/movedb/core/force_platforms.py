"""Force platform data structures."""

import numpy as np
import polars as pl
from pydantic import BaseModel, field_validator


class EZC3DForcePlatform(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    unit_force: str = "N"  # Default force unit
    unit_moment: str = "Nm"  # Default moment unit
    unit_position: str = "m"  # Default position unit
    cal_matrix: np.ndarray = np.eye(6)  # Calibration matrix for force platform
    corners: np.ndarray = np.zeros((3, 4))  # 4 corners in 3D space
    origin: np.ndarray = np.zeros(3)  # Origin of the force platform
    data: pl.DataFrame = pl.DataFrame()  # Data for the force platform
    # Moments and center of pressure are expressed in global

    @field_validator("cal_matrix")
    @classmethod
    def validate_cal_matrix(cls, v: np.ndarray) -> np.ndarray:
        """Validate that the calibration matrix is 6x6"""
        if v.shape != (6, 6):
            raise ValueError("Calibration matrix must be 6x6")
        return v

    @field_validator("corners")
    @classmethod
    def validate_corners(cls, v: np.ndarray) -> np.ndarray:
        """Validate that the corners are a 3x4 array"""
        if v.shape != (3, 4):
            raise ValueError("Corners must be a 3x4 array")
        return v

    @field_validator("origin")
    @classmethod
    def validate_origin(cls, v: np.ndarray) -> np.ndarray:
        """Validate that the origin is a 3D vector"""
        if v.shape != (3,):
            raise ValueError("Origin must be a 3D vector")
        return v

    @field_validator("data")
    @classmethod
    def validate_data_structure(cls, v: pl.DataFrame) -> pl.DataFrame:
        """Validate that the DataFrame has the required columns"""
        required_columns = [
            "force_x",
            "force_y",
            "force_z",
            "moment_x",
            "moment_y",
            "moment_z",
            "center_of_pressure_x",
            "center_of_pressure_y",
            "center_of_pressure_z",
            "free_moment_x",
            "free_moment_y",
            "free_moment_z",
        ]

        if not all(col in v.columns for col in required_columns):
            missing = [col for col in required_columns if col not in v.columns]
            raise ValueError(f"Missing required columns: {missing}")

        # Ensure correct data types
        try:
            v = v.with_columns(
                [
                    pl.col("force_x").cast(pl.Float64),
                    pl.col("force_y").cast(pl.Float64),
                    pl.col("force_z").cast(pl.Float64),
                    pl.col("moment_x").cast(pl.Float64),
                    pl.col("moment_y").cast(pl.Float64),
                    pl.col("moment_z").cast(pl.Float64),
                    pl.col("center_of_pressure_x").cast(pl.Float64),
                    pl.col("center_of_pressure_y").cast(pl.Float64),
                    pl.col("center_of_pressure_z").cast(pl.Float64),
                    pl.col("free_moment_x").cast(pl.Float64),
                    pl.col("free_moment_y").cast(pl.Float64),
                    pl.col("free_moment_z").cast(pl.Float64),
                ]
            )
        except Exception as e:
            raise ValueError(f"Error casting columns to correct types: {e}")
        return v

    @property
    def force(self) -> np.ndarray:
        """Return force as a numpy array (n_frames, 3)"""
        return self.data.select(["force_x", "force_y", "force_z"]).to_numpy()

    @property
    def moment(self) -> np.ndarray:
        """Return moment as a numpy array (n_frames, 3)"""
        return self.data.select(["moment_x", "moment_y", "moment_z"]).to_numpy()

    @property
    def center_of_pressure(self) -> np.ndarray:
        """Return center of pressure as a numpy array (n_frames, 3)"""
        return self.data.select(
            ["center_of_pressure_x", "center_of_pressure_y", "center_of_pressure_z"]
        ).to_numpy()

    @property
    def free_moment(self) -> np.ndarray:
        """Return free moment as a numpy array (n_frames, 3)"""
        return self.data.select(
            ["free_moment_x", "free_moment_y", "free_moment_z"]
        ).to_numpy()

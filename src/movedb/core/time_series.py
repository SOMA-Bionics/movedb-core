"""Time series data structures for biomechanical trials."""

from pydantic import BaseModel, model_validator, field_validator
import polars as pl
import numpy as np

class TimeSeriesGroup(BaseModel):
    first_frame: int
    last_frame: int
    rate: float
    
    @model_validator(mode='after')
    def validate_frames_and_rate(self):
        """
        Validate that first_frame is non-zero and less than last_frame and rate is positive.
        """
        assert self.first_frame >= 0, "first_frame must be non-negative"
        assert self.first_frame < self.last_frame, "first_frame must be less than last_frame"
        assert self.rate > 0, "rate must be positive"
        return self
    
    @property
    def total_frames(self):
        return self.last_frame - self.first_frame + 1
    
    def time_from_frame(self, frame: int) -> float:
        if frame < self.first_frame or frame > self.last_frame:
            raise ValueError("Frame out of bounds")
        return frame / self.rate
    
    @property 
    def time(self) -> np.ndarray:
        """
        Return a time vector for the time series group.
        """
        return np.arange(self.first_frame, self.last_frame + 1) / self.rate

class MarkerTrajectory(BaseModel):
    """
    A marker trajectory represented as a Polars DataFrame with columns:
    x, y, z, residual, description
    """
    class Config:
        arbitrary_types_allowed = True
    data: pl.DataFrame
    description: str = ''
    
    def __init__(self, **kwargs):
        if 'data' in kwargs:
            data = kwargs['data']
        else:
            data = pl.DataFrame({
                'x': kwargs.get('x', []),
                'y': kwargs.get('y', []),
                'z': kwargs.get('z', []),
                'residual': kwargs.get('residual', []),
            })
        description = kwargs.get('description', '')
        super().__init__(data=data, description=description)
            
    
    @field_validator('data')
    @classmethod
    def validate_dataframe_structure(cls, v: pl.DataFrame) -> pl.DataFrame:
        """Validate that the DataFrame has the required columns"""
        required_columns = ['x', 'y', 'z', 'residual']

        missing = [col for col in required_columns if col not in v.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
        
        # Ensure correct data types
        try:
            v = v.with_columns([
                pl.col('x').cast(pl.Float64),
                pl.col('y').cast(pl.Float64),
                pl.col('z').cast(pl.Float64),
                pl.col('residual').cast(pl.Float64),
            ])
        except Exception as e:
            raise ValueError(f"Error casting columns to correct types: {e}")
        return v
    
    @property
    def coords(self) -> np.ndarray:
        """Return coordinates as numpy array (n_frames, 3)"""
        return self.data.select(['x', 'y', 'z']).to_numpy()
    
    @property
    def residual(self) -> np.ndarray:
        """Return residuals as numpy array (n_frames,)"""
        return self.data.select(['residual']).to_numpy().flatten()

    def __len__(self) -> int:
        return len(self.data)
    
    def prefix_columns(self, prefix: str) -> pl.DataFrame:
        """Rename columns with a prefix for concatenation"""
        return self.data.rename({
            'x': f'{prefix}_x',
            'y': f'{prefix}_y', 
            'z': f'{prefix}_z',
            'residual': f'{prefix}_residual',
        })
    
class Points(TimeSeriesGroup):
    units: str
    trajectories: dict[str, MarkerTrajectory]
    
    @model_validator(mode='after')
    def validate_trajectory_lengths(self) -> 'Points':
        """Ensure all trajectories have the same length matching total_frames"""
        expected_length = self.total_frames
        
        for marker_name, trajectory in self.trajectories.items():
            if len(trajectory) != expected_length:
                raise ValueError(
                    f"Marker '{marker_name}' has {len(trajectory)} frames, "
                    f"expected {expected_length} frames"
                )
        return self
    
    def to_df(self) -> pl.DataFrame:
        """
        Convert the Points object to a Polars DataFrame.
        Each marker's coordinates will be separate columns (marker_x, marker_y, marker_z, marker_residual).
        """
        if not self.trajectories:
            return pl.DataFrame()
        
        dfs = []
        for name, trajectory in self.trajectories.items():
            marker_df = trajectory.prefix_columns(name)
            dfs.append(marker_df)
        
        # Add time column
        time_df = pl.DataFrame({
            'time': self.time
        })
        
        # Concatenate horizontally
        all_dfs = [time_df] + dfs
        return pl.concat(all_dfs, how='horizontal')
    
    def from_df(self, df: pl.DataFrame):
        """
        Populate the Points object from a Polars DataFrame.
        The DataFrame can only have columns: time, marker_x, marker_y, marker_z, marker_residual.
        This will overwrite existing trajectories.
        """
        for col in df.columns:
            if col.startswith('marker_'):
                marker_name = col[7:]  # Remove 'marker_' prefix
                self.trajectories[marker_name] = MarkerTrajectory(
                    data=df[[col, f'{col}_y', f'{col}_z', f'{col}_residual']],
                    description=marker_name
                )

    def get_marker_coords(self, marker_name: str, frame: int | None = None) -> np.ndarray:
        """Get marker coordinates, optionally at a specific frame"""
        if marker_name not in self.trajectories:
            raise ValueError(f"Marker '{marker_name}' not found in trajectories")        
        marker = self.trajectories[marker_name]
        
        if frame is None:
            return marker.coords
        
        if frame < self.first_frame or frame > self.last_frame:
            raise IndexError(f"Frame {frame} out of bounds")

        # Convert absolute frame to relative index
        frame_idx = frame - self.first_frame
        return marker.coords[frame_idx]
    
    def add_marker(self, name: str, x: list, y: list, z: list, 
                   residual: list | None = None, description: str = ''):
        """Add a new marker trajectory"""
        n_frames = self.total_frames
        
        # Validate lengths
        if len(x) != n_frames or len(y) != n_frames or len(z) != n_frames:
            raise ValueError(f"Coordinate arrays must have length {n_frames}")
        
        if residual is None:
            residual = [0.0] * n_frames
            
        trajectory = MarkerTrajectory(
            data = pl.DataFrame({
                'x': x,
                'y': y,
                'z': z,
                'residual': residual
            }),
            description=description
        )
        self.trajectories[name] = trajectory

class AnalogChannel(BaseModel):
    """Each analog channel can have different units"""
    units: str
    data: list[float]
    description: str = ''
    scale: float = 1.0
    offset: float = 0.0

class Analogs(TimeSeriesGroup):
    # Analogs store different channels each of which could have different units
    channels: dict[str, AnalogChannel]
    gen_scale: float = 1.0 # General scale factor for all channels
    
    def to_df(self) -> pl.DataFrame:
        """
        Convert the Analogs object to a Polars DataFrame.
        Each channel will be a column in the DataFrame.
        WARNING: This decouples the channels from their original units.
        """
        if not self.channels:
            return pl.DataFrame()
        dfs = []
        for name, channel in self.channels.items():
            channel_df = pl.DataFrame({
                name: channel.data
            })
            dfs.append(channel_df)
        
        # Concatenate horizontally
        return pl.concat(dfs, how='horizontal')

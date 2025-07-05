"""Event data structures for biomechanical trials."""

from pydantic import BaseModel, model_validator

class Event(BaseModel): 
    """
    Times will default to being stored in seconds.
    See c3d event specification for details.
    """
    label: str
    context: str
    frame: int | None = None
    time: float | None = None
    description: str | None = None
    
    @model_validator(mode='after')
    def validate_frames_or_times(self):
        assert self.frame is not None or self.time is not None, "Either frames or times must be provided."
        assert self.frame is None or self.time is None, "Only one of frames or times should be provided."
        return self

    def get_frame(self, point_rate: float | None) -> int:
        if self.frame is not None:
            return self.frame
        if self.time is not None and point_rate is not None and point_rate > 0:
            return int(self.time * point_rate)
        # This should not happen if validate_frames_or_times is called first
        raise ValueError("Cannot compute frame without point rate or time.")
        
    def get_time(self, point_rate: float | None) -> float:
        if self.time is not None:
            return self.time
        if self.frame is not None and point_rate is not None and point_rate > 0:
            return self.frame / point_rate
        # This should not happen if validate_frames_or_times is called first
        raise ValueError("Cannot compute time without point rate or frame.")

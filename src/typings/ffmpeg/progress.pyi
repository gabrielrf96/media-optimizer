from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from ffmpeg.protocol import FFmpegProtocol

@dataclass(frozen=True)
class Progress:
    frame: int
    fps: float
    size: int
    time: timedelta
    bitrate: float
    speed: float

class Tracker:
    def __init__(self, ffmpeg: FFmpegProtocol) -> None: ...
    def _on_stderr(self, line: str) -> None: ...

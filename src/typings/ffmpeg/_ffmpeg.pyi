from __future__ import annotations

from typing import Any

from ffmpeg.nodes import Stream

from src.components.ffmpeg_types import Probe

def probe(filename: str, cmd: str = "ffprobe", **kwargs: dict[str, str]) -> Probe: ...
def input(filename: str, **kwargs: Any) -> Stream: ...  # pylint: disable=redefined-builtin
def run(
    stream_spec: Any,
    cmd: str = "ffmpeg",
    capture_stdout: bool = False,
    capture_stderr: bool = False,
    input: Any = None,  # pylint: disable=redefined-builtin,redefined-outer-name
    quiet: bool = False,
    overwrite_output: bool = False,
) -> tuple[bytes, bytes]: ...

import os
from typing import IO, Optional, Self, Union

from ffmpeg.types import Option
from pyee import EventEmitter

class FFmpeg(EventEmitter):
    def __init__(self, executable: str = "ffmpeg") -> None: ...
    @property
    def arguments(self) -> list[str]: ...
    def option(self, key: str, value: Optional[Option] = None) -> Self: ...
    def input(
        self,
        url: Union[str, os.PathLike[str]],
        options: Optional[dict[str, Optional[Option]]] = None,
        **kwargs: Optional[Option],
    ) -> Self: ...
    def output(
        self,
        url: Union[str, os.PathLike[str]],
        options: Optional[dict[str, Optional[Option]]] = None,
        **kwargs: Optional[Option],
    ) -> Self: ...
    def execute(self, stream: Optional[Union[bytes, IO[bytes]]] = None, timeout: Optional[float] = None) -> bytes: ...
    def terminate(self) -> None: ...

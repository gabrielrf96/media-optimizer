"""
A series of typed representations of the data handled and returned by the `ffmpeg` package.
"""

from enum import StrEnum
from typing import TypedDict


class ProbeKey(StrEnum):
    STREAMS = "streams"


class StreamKey(StrEnum):
    CODEC_TYPE = "codec_type"
    WIDTH = "width"
    HEIGHT = "height"


class CodecType(StrEnum):
    VIDEO = "video"


class Stream(TypedDict):
    codec_type: CodecType
    width: str
    height: str


class Probe(TypedDict):
    streams: list[Stream]

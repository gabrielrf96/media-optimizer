"""
An optimizer for videos contained in a folder. The optimizer will prompt the user with a series of
questions to determine the behavior of the optimization process.

The optimization is done in two ways:

- Converting to H.265 (HEVC) with a chosen quality level. This conversion with optimized encoding settings can
keep quality almost intact (for viewing purposes) while saving anywhere from 10 to 75% space (compression level
depends on the source video and chosen encoding quality and preset).

- Optionally, limiting the output resolution.
"""

from pathlib import Path
from typing import override

import ffmpeg

from src.components.ffmpeg_types import CodecType, ProbeKey, StreamKey
from src.components.files import File, Files, get_media_info
from src.components.media_optimizer import MediaOptimizer
from src.components.options import MenuOption, Resolution, ask_for_overwrite_permission, ask_for_short_side_limit


class EncodingQuality(int, MenuOption):
    HIGHEST = 18, "Highest (CRF=18)"
    HIGH = 20, "High (CRF=20)"
    MEDIUM = 22, "Medium (CRF=22)"
    LOW = 24, "Low (CRF=24)"
    LOWEST = 26, "Lowest (CRF=26)"

    def __new__(cls, value: int, _: str):
        member = int.__new__(cls, value)
        member._value_ = value

        return member

    def __init__(self, value: int, name: str):
        super().__init__()
        self._value_ = value
        self._name_ = name


class EncodingPreset(str, MenuOption):
    FAST = "fast", "Fast (faster encoding, worse quality per file size rate)"
    MEDIUM = "medium", "Medium (balanced encoding speed / quality per file size rate)"
    SLOW = "slow", "Medium (slower encoding, better quality per file size rate)"

    def __new__(cls, value: str, _: str):
        member = str.__new__(cls, value)
        member._value_ = value

        return member

    def __init__(self, value: str, name: str):
        super().__init__()
        self._value_ = value
        self._name_ = name


class VideoError(Exception):
    pass


class VideoOptimizer(MediaOptimizer):
    @override
    def is_valid_file(self, path: Path) -> bool:
        info = get_media_info(path)

        return len(info.video_tracks) > 0

    @override
    def run(self, files: Files):
        # Report sample of source video dimensions
        w, h = self._get_video_dimensions(files[0])
        print(f"Source video dimensions are {w}x{h} (sampled first)")

        # Ask for output resolution limit
        target_max_short_side = ask_for_short_side_limit(Resolution.lteq(Resolution.R_1440P))

        # Ask for encoding quality
        quality = EncodingQuality.choose(
            "Choose an encoding quality (consider CRF based on output resolution and framerate):",
            default=EncodingQuality.MEDIUM,
        )

        # Ask for encoding preset
        preset = EncodingPreset.choose(
            "Choose an encoding preset:",
            default=EncodingPreset.MEDIUM,
        )

        # Ask if existing optimized videos should be overwritten
        should_overwrite_existing: bool = ask_for_overwrite_permission(files)

        # Process the list of files
        for file in files:
            self._convert_video(file, target_max_short_side, quality, preset, should_overwrite_existing)

    def _get_video_dimensions(self, file: File) -> tuple[int, int]:
        probe = ffmpeg.probe(str(file.source))
        video_stream = next(
            (stream for stream in probe.get(ProbeKey.STREAMS) if stream.get(StreamKey.CODEC_TYPE) == CodecType.VIDEO),
            None,
        )

        if video_stream is None:
            raise VideoError(f"No stream found in source file {file.source}")

        return (
            int(video_stream.get(StreamKey.WIDTH)),
            int(video_stream.get(StreamKey.HEIGHT)),
        )

    def _convert_video(
        self,
        file: File,
        target_max_short_side: int,
        quality: EncodingQuality,
        preset: EncodingPreset,
        should_overwrite_existing: bool = True,
    ):
        if file.target.is_file() and not should_overwrite_existing:
            return

        source_short_side = min(self._get_video_dimensions(file))
        size_divider = (source_short_side / target_max_short_side) if source_short_side > target_max_short_side else 1

        stream = (
            ffmpeg.input(str(file.source))
            .filter("scale", f"iw/{size_divider}", f"ih/{size_divider}")
            .output(
                str(file.target),
                vcodec="libx265",
                crf=quality.value,
                preset=preset.value,
                acodec="copy",
                map="0:a",
                map_metadata="0",
                movflags="use_metadata_tags",
            )
            .overwrite_output()
        )

        ffmpeg.run(stream)

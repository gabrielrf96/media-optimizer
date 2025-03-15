"""
An optimizer for videos contained in a folder. The optimizer will prompt the user with a series of
questions to determine the behavior of the optimization process.

The optimization is done in two ways:

- Converting to H.265 (HEVC) with a chosen quality level. This conversion with optimized encoding settings can
keep quality almost intact (for viewing purposes) while saving anywhere from 10 to 75% space (compression level
depends on the source video and chosen encoding quality and preset).

- Optionally, limiting the output resolution.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable, override

from ffmpeg import Progress
from pymediainfo import MediaInfo
from tqdm import tqdm

from src.components.ffmpeg import FFmpeg
from src.components.files import File, Files, get_file_size_as_str
from src.components.media_optimizer import MediaOptimizer
from src.components.options import MenuOption, Resolution, ask_for_overwrite_permission, ask_for_short_side_limit
from src.components.stdout import cli_unprint


class VideoError(Exception):
    pass


class EncodingQuality(int, MenuOption):
    HIGHEST = 18, "Highest (CRF=18)"
    HIGH = 20, "High (CRF=20)"
    MEDIUM = 22, "Medium (CRF=22) (your eyes won't notice any difference with the source)"
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
    SLOW = "slow", "Slow (slower encoding, better quality per file size rate)"

    def __new__(cls, value: str, _: str):
        member = str.__new__(cls, value)
        member._value_ = value

        return member

    def __init__(self, value: str, name: str):
        super().__init__()
        self._value_ = value
        self._name_ = name


class VideoFile(File):
    def __init__(self, source: Path, target: Path, media_info: MediaInfo):
        super().__init__(source, target)

        track = media_info.video_tracks[0]

        self.width = int(track.width)
        self.height = int(track.height)
        self.duration = float(track.duration) / 1000.0


class VideoOptimizer(MediaOptimizer[VideoFile]):
    total_duration: float = 0.0
    progress_tracker: tqdm[VideoFile]

    @override
    def is_valid_file(self, path: Path) -> bool:
        info = self.media_info_service.get(path)

        return info is not None and len(info.video_tracks) > 0

    @override
    def create_file(self, source: Path, target: Path) -> VideoFile:
        media_info = self.media_info_service.get(source)
        assert isinstance(media_info, MediaInfo)

        file = VideoFile(source, target, media_info)

        self.total_duration += file.duration

        return file

    @override
    def run(self, files: Files[VideoFile]):
        # Ask for output resolution limit
        short_side_limit = ask_for_short_side_limit(Resolution.lteq(Resolution.R_1440P))

        # Ask for encoding quality
        quality = EncodingQuality.choose(
            "Choose an encoding quality (consider CRF based on output resolution and frame rate):",
            default=EncodingQuality.MEDIUM,
        )

        # Ask for encoding preset
        preset = EncodingPreset.choose(
            "Choose an encoding preset:",
            default=EncodingPreset.MEDIUM,
        )

        # Ask if existing optimized videos should be overwritten
        should_overwrite: bool = ask_for_overwrite_permission(files)

        # Process the list of files
        print("\nOptimizing videos...\n")

        total_count = len(files)

        self.progress_tracker = tqdm(
            files,
            total=self.total_duration,
            unit="vsec",  # <- unit = seconds of video
            bar_format=self.__get_progress_bar_format(0, total_count),
            leave=False,  # <- necessary to avoid issues, as we're manually handling final display of the progress bar
        )

        for idx, file in enumerate(files):
            self._convert_video(
                file,
                short_side_limit,
                quality,
                preset,
                should_overwrite,
            )
            self.progress_tracker.bar_format = self.__get_progress_bar_format(idx + 1, total_count)

        self.progress_tracker.update(self.total_duration - self.progress_tracker.n)
        cli_unprint(2, force_final_clear=True)
        self.progress_tracker.display()

    def _convert_video(
        self,
        file: VideoFile,
        short_side_limit: int,
        quality: EncodingQuality,
        preset: EncodingPreset,
        should_overwrite: bool = True,
    ):
        if file.target.is_file() and not should_overwrite:
            return

        source_short_side = min(file.width, file.height)
        size_divider = (source_short_side / short_side_limit) if source_short_side > short_side_limit else 1

        ffmpeg_job = (
            FFmpeg()
            .option("y")
            .input(str(file.source))
            .output(
                str(file.target),
                vf=f"scale=iw/{size_divider}:ih/{size_divider}",
                vcodec="libx265",
                acodec="copy",
                crf=quality.value,
                preset=preset.value,
                map=["0:v", "0:a?"],
                map_metadata="0",
                movflags="use_metadata_tags",
            )
        )

        ffmpeg_job.on("progress", self.__get_progress_handler(file))  # type: ignore

        ffmpeg_job.execute()

    def __get_progress_handler(self, file: VideoFile) -> Callable[[Progress], None]:
        fname = file.source.name
        last_progress = 0.0

        def on_progress(progress: Progress):
            nonlocal fname, last_progress

            frame = str(progress.frame).rjust(5)
            fps = str(round(progress.fps)).rjust(3)
            size = get_file_size_as_str(progress.size, ".2f").rjust(11)
            time = progress.time
            bitrate = str(round(progress.bitrate, 1)).rjust(7) + "kbits/s"

            if time.total_seconds() < 0:
                # For some reason, this happens at the end of each video encoding. We can just skip those cases.
                return

            delta = time.total_seconds() - last_progress
            last_progress += delta

            self.progress_tracker.write(f'Encoding "{fname}"')
            self.progress_tracker.write(f"frame={frame} | fps={fps} | size={size} | time={time} | bitrate={bitrate}")
            self.progress_tracker.update(delta)

            cli_unprint(3)

        return on_progress

    def __get_progress_bar_format(self, completed: int, total: int) -> str:
        return f"{{l_bar}}{{bar}}| {completed}/{total} [{{elapsed}}<{{remaining}}, {{rate_fmt}}{{postfix}}]"

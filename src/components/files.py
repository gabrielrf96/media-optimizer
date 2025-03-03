import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

from pymediainfo import MediaInfo

DEFAULT_TARGET_DIR = "optimized"


@dataclass
class File:
    """A file to optimize, whose definition includes both the source and target paths."""

    source: Path
    target: Path


class Files:
    """A representation of the entire directory of source files, along with the target directory."""

    def __init__(
        self,
        source_dir: str,
        target_dir: Optional[str] = None,
        filter_lambda: Callable[[Path], bool] | None = None,
    ):
        self.source_dir: Path = Path(source_dir)
        self.target_dir: Path = Path(target_dir) if target_dir is not None else Path(source_dir, DEFAULT_TARGET_DIR)
        self.__files: list[File] = []
        self.__extensions: set[str] = set()

        self.__load_files(filter_lambda)

        if len(self.__files) == 0:
            print(f"[ERROR] No valid files found for selected optimizer in source directory {self.source_dir}")

            sys.exit(1)

        self.__init_target_dir()

    def __getitem__(self, index: int):
        return self.__files[index]

    def __iter__(self):
        for file in self.__files:
            yield file

    def __len__(self):
        return len(self.__files)

    def __load_files(self, filter_lambda: Callable[[Path], bool] | None = None):
        for fname in os.listdir(self.source_dir):
            source = Path(self.source_dir, fname)

            if source.is_dir() or (filter_lambda is not None and not filter_lambda(source)):
                continue

            self.__files.append(File(source=source, target=Path(self.target_dir, fname)))
            self.__extensions.add(Path(fname).suffix)

    def __init_target_dir(self):
        os.umask(0)
        Path(self.target_dir).mkdir(mode=self.source_dir.stat().st_mode, parents=True, exist_ok=True)

    def is_extension_present(self, extension: str) -> bool:
        extension = extension if extension.startswith(".") else f".{extension}"

        return extension in self.__extensions


def get_media_info(path: Path) -> MediaInfo:
    return MediaInfo.parse(path, mediainfo_options={"File_TestContinuousFileNames": "0"})

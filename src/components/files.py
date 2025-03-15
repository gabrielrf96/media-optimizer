from __future__ import annotations

import math
import os
import sys
from pathlib import Path
from typing import Callable, Generic, TypeVar

from pymediainfo import MediaInfo

from src.components.stdout import CLEAR_LINE

DEFAULT_TARGET_DIR = "optimized"
FILE_SIZE_UNITS = ("B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB")


class File:
    """A file to optimize, whose definition includes both the source and target paths."""

    def __init__(self, source: Path, target: Path):
        self.source = source
        self.target = target


GenericFile = TypeVar("GenericFile", bound=File, covariant=True, default=File)


class Files(Generic[GenericFile]):
    """A representation of the entire directory of source files, along with the target directory."""

    def __init__(
        self,
        source_dir: str,
        target_dir: str | None = None,
        filter_lambda: Callable[[Path], bool] | None = None,
        create_file_lambda: Callable[[Path, Path], GenericFile] | None = None,
    ):
        self.source_dir = Path(source_dir)
        if not self.source_dir.is_dir():
            print("[ERROR] The provided source path is not a directory or does not exist")

            sys.exit(1)

        self.target_dir = Path(target_dir) if target_dir is not None else Path(source_dir, DEFAULT_TARGET_DIR)
        self.initial_size = 0
        self.final_size = 0
        self.__files: list[GenericFile] = []
        self.__extensions: set[str] = set()

        self.__load_files(filter_lambda, create_file_lambda)

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

    def __load_files(
        self,
        filter_lambda: Callable[[Path], bool] | None = None,
        create_file_lambda: Callable[[Path, Path], GenericFile] | None = None,
    ):
        for fname in os.listdir(self.source_dir):
            source = Path(self.source_dir, fname)
            target = Path(self.target_dir, fname)

            if source.is_dir() or (filter_lambda is not None and not filter_lambda(source)):
                continue

            self.__files.append(
                create_file_lambda(source, target)
                if create_file_lambda is not None
                else File(source, target)  # type: ignore
            )  # fmt: skip
            self.__extensions.add(Path(fname).suffix)
            self.initial_size += source.stat().st_size

    def __init_target_dir(self):
        os.umask(0)
        Path(self.target_dir).mkdir(mode=self.source_dir.stat().st_mode, parents=True, exist_ok=True)

    def is_extension_present(self, extension: str) -> bool:
        extension = extension if extension.startswith(".") else f".{extension}"

        return extension in self.__extensions

    def calculate_final_size(self):
        for file in self:
            self.final_size += file.target.stat().st_size


class MediaInfoService:
    def __init__(self):
        self.__cache: dict[Path, MediaInfo | None] = {}

    def get(self, path: Path) -> MediaInfo | None:
        if path not in self.__cache:
            try:
                info = MediaInfo.parse(path, mediainfo_options={"File_TestContinuousFileNames": "0"})
            except RuntimeError:
                info = None

            self.__cache[path] = info

        return self.__cache[path]


def get_file_size_as_str(size_bytes: int, number_format: str | None = None) -> str:
    if size_bytes == 0:
        return "0 B"

    # Calculate which multiple of 1024 the provided size falls within
    i = int(math.floor(math.log(size_bytes, 1024)))

    # Get the correct divisor based on the calculated multiple of 1024,
    # then use that to convert the original size in bytes to the correct unit
    divisor = math.pow(1024, i)
    converted_size = round(size_bytes / divisor, 2)

    if converted_size >= 1000:
        # Keep output values below 1000 (e.g. 1000 B => 0.98 KiB) by jumping to the next multiple when necessary
        i += 1
        converted_size /= 1024

    if number_format is not None:
        converted_size = f"%{number_format}" % converted_size

    return f"{converted_size} {FILE_SIZE_UNITS[i]}"


def print_size_reduction_info(files: Files[GenericFile]):
    initial = get_file_size_as_str(files.initial_size)
    final = get_file_size_as_str(files.final_size)

    reduction_percent = round(
        (1 - files.final_size / files.initial_size) * 100,
        1,
    )

    print(f"\n{CLEAR_LINE}\n{CLEAR_LINE}Finished!")
    print(f"{CLEAR_LINE}- Total initial size: {initial}")
    print(f"{CLEAR_LINE}- Total final size: {final}")
    print(f"\n{CLEAR_LINE}Size reduction: {reduction_percent}%\n")

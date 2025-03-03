"""
An optimizer for pictures contained in a folder. The optimizer will prompt the user with a series of
questions to determine the behavior of the optimization process, including options for resizing the pictures and
changing the output quality.
"""

from __future__ import annotations

from enum import Enum, auto
from pathlib import Path
from typing import override

import PIL
from PIL import Image
from tqdm import tqdm

from src.components.files import File, Files, get_media_info
from src.components.media_optimizer import MediaOptimizer
from src.components.options import MenuOption, Resolution, ask_for_overwrite_permission, ask_for_short_side_limit


class ImageFormat(str, MenuOption):
    KEEP = "keep", "Keep original format"
    JPEG = "jpg", "JPEG"
    PNG = "png", "PNG"

    def __new__(cls, value: str, _: str):
        member = str.__new__(cls, value)
        member._value_ = value

        return member

    def __init__(self, value: str, name: str):
        super().__init__()
        self._value_ = value
        self._name_ = name

    @property
    def extension(self):
        return f".{self.value}"


class JpegQuality(int, MenuOption):
    HIGHEST = 100, "100 (Minimal compression)"
    HIGH = 90, "90 (Low compression)"
    MEDIUM = 80, "80 (Standard compression)"
    LOW = 70, "70 (Higher compression)"
    LOWEST = 60, "60 (Aggressive compression)"

    def __new__(cls, value: int, _: str):
        member = int.__new__(cls, value)
        member._value_ = value

        return member

    def __init__(self, value: int, name: str):
        super().__init__()
        self._value_ = value
        self._name_ = name


class Orientation(Enum):
    HORIZONTAL = auto()
    VERTICAL = auto()

    @classmethod
    def from_dimensions(cls, w: int, h: int) -> Orientation:
        return cls.HORIZONTAL if w > h else cls.VERTICAL


class PictureOptimizer(MediaOptimizer):
    @override
    def is_valid_file(self, path: Path) -> bool:
        info = get_media_info(path)

        return len(info.image_tracks) > 0

    @override
    def run(self, files: Files):
        # Ask for output resolution limit
        target_max_short_side = ask_for_short_side_limit()

        # Ask for output format
        output_format = ImageFormat.choose("What output format would you like to use?")

        # Ask for JPEG quality
        jpeg_quality = JpegQuality.HIGHEST

        if output_format == ImageFormat.JPEG or (
            output_format == ImageFormat.KEEP and files.is_extension_present(ImageFormat.JPEG.extension)
        ):
            jpeg_quality = JpegQuality.choose(
                "What quality level would you like to set for JPEG output files?",
                default=JpegQuality.MEDIUM,
            )

        # Ask if existing optimized pictures should be overwritten
        should_overwrite_existing = ask_for_overwrite_permission(files)

        # Process the list of files
        print("\nOptimizing pictures...")

        for file in tqdm(files):
            try:
                self._optimize_image(
                    file, target_max_short_side, output_format, jpeg_quality, should_overwrite_existing
                )
            except PIL.UnidentifiedImageError:
                # Skip non-image files
                continue

    def _optimize_image(
        self,
        file: File,
        target_max_short_side: int,
        output_format: ImageFormat,
        jpeg_quality: int,
        should_overwrite_existing: bool = True,
    ):
        if file.target.is_file() and not should_overwrite_existing:
            return

        image = Image.open(file.source)

        if target_max_short_side != Resolution.KEEP:
            image = self._resize_image(image, target_max_short_side)

        image.save(
            file.target if output_format == ImageFormat.KEEP else file.target.with_suffix(output_format.extension),
            exif=image.info.get("exif"),
            xmp=image.info.get("xmp"),
            quality=jpeg_quality,
        )

    def _resize_image(self, image: Image.Image, target_max_short_side: int) -> Image.Image:
        w, h = image.size

        if min(w, h) <= target_max_short_side:
            return image

        aspect_ratio = w / h
        orientation = Orientation.from_dimensions(w, h)

        if orientation == Orientation.HORIZONTAL:
            h = target_max_short_side
            w = int(h * aspect_ratio)
        else:
            w = target_max_short_side
            h = int(w / aspect_ratio)

        return image.resize((w, h), Image.Resampling.LANCZOS)

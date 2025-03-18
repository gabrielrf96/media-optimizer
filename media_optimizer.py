"""
Entry point script that lets you choose which optimization tool you want to use.
"""

import argparse
import sys
from functools import cached_property
from typing import Any

from src._version import __VERSION__
from src.components.files import Files, print_size_reduction_info
from src.components.media_optimizer import MediaOptimizer
from src.components.options import MenuOption, ask_for_source_dir
from src.optimizers.pictures import PictureOptimizer
from src.optimizers.videos import VideoOptimizer


class MediaOptimizerOption(MenuOption):
    PICTURES = PictureOptimizer, "Picture optimizer", "pictures"
    VIDEOS = VideoOptimizer, "Video optimizer", "videos"

    def __init__(self, optimizer_class: type[MediaOptimizer[Any]], name: str, resource_label: str):
        super().__init__()
        self._value_: type[MediaOptimizer[Any]] = optimizer_class
        self._name_ = name
        self.resource_label = resource_label

    @cached_property
    def optimizer(self) -> MediaOptimizer[Any]:
        return self._value_()

    def run(self):
        files = Files(
            source_dir=ask_for_source_dir(self.resource_label),
            filter_lambda=self.optimizer.is_valid_file,
            create_file_lambda=self.optimizer.create_file,
        )

        self.optimizer.run(files)

        files.calculate_final_size()
        print_size_reduction_info(files)
        print(f"You can find the optimized files in {files.target_dir}\n")


def main():
    args = __parse_args()
    if args.version:
        __version()

    try:
        MediaOptimizerOption.choose("Choose an optimization tool:").run()
    except KeyboardInterrupt:
        print("Cancelled")

        sys.exit(0)


def __parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=f"Media Optimizer v{__VERSION__}. Run without arguments for regular usage.",
    )
    parser.add_argument("-v", "--version", action="store_true", help="show Media Optimizer version")

    return parser.parse_args()


def __version():
    print(f"Media Optimizer v{__VERSION__}")

    sys.exit(0)


if __name__ == "__main__":
    main()

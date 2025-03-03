"""
Entry point script that lets you choose which optimization tool you want to use.

If you have manually installed the necessary dependencies (pyproject.toml) in your system, you can just run the script
normally:
`python media_optimizer.py`

Otherwise, the recommended way to run it is by using `uv` (https://github.com/astral-sh/uv):
`uv run media_optimizer.py`
"""

import sys

from src.components.files import Files
from src.components.media_optimizer import MediaOptimizer
from src.components.options import MenuOption, ask_for_source_dir
from src.pictures import PictureOptimizer
from src.videos import VideoOptimizer


class MediaOptimizerOption(MenuOption):
    PICTURES = PictureOptimizer(), "Picture optimizer", "pictures"
    VIDEOS = VideoOptimizer(), "Video optimizer", "videos"

    def __init__(self, optimizer: MediaOptimizer, name: str, file_type: str):
        super().__init__()
        self._value_ = optimizer
        self._name_ = name
        self.file_type = file_type

    @property
    def optimizer(self) -> MediaOptimizer:
        return self._value_

    def run(self):
        self.optimizer.run(
            Files(
                source_dir=ask_for_source_dir(self.file_type),
                filter_lambda=self.optimizer.is_valid_file,
            )
        )


def main():
    try:
        MediaOptimizerOption.choose("Choose an optimization tool:").run()
    except KeyboardInterrupt:
        print("Cancelled")
        sys.exit(0)


if __name__ == "__main__":
    main()

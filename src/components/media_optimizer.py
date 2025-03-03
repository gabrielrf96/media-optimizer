from abc import ABC, abstractmethod
from pathlib import Path

from src.components.files import Files


class MediaOptimizer(ABC):
    """
    Abstract class that describes the basic interface that an optimizer class must have.
    """

    @abstractmethod
    def is_valid_file(self, path: Path) -> bool:
        raise NotImplementedError

    @abstractmethod
    def run(self, files: Files) -> None:
        raise NotImplementedError

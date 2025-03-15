from abc import ABC, abstractmethod
from functools import cached_property
from pathlib import Path
from typing import Generic

from src.components.files import Files, GenericFile, MediaInfoService


class MediaOptimizer(ABC, Generic[GenericFile]):
    """
    Abstract class that describes the basic interface that an optimizer class must have.
    """

    @cached_property
    def media_info_service(self) -> MediaInfoService:
        return MediaInfoService()

    @abstractmethod
    def is_valid_file(self, path: Path) -> bool:
        raise NotImplementedError

    @abstractmethod
    def create_file(self, source: Path, target: Path) -> GenericFile:
        raise NotImplementedError

    @abstractmethod
    def run(self, files: Files[GenericFile]) -> None:
        raise NotImplementedError

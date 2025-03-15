from __future__ import annotations

import os
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Self, Sequence

import questionary
from questionary import Choice

from src.components.files import Files, GenericFile


class MenuOption(Enum):
    @classmethod
    def all(cls, filter_lambda: Callable[[Self], bool] | None = None) -> list[Self]:
        return (
            list(cls)
            if filter_lambda is None
            else [menu_option for menu_option in cls if filter_lambda(menu_option)]
        )  # fmt: skip

    @classmethod
    def all_as_choices(cls, filter_lambda: Callable[[Self], bool] | None = None) -> list[Choice]:
        return (
            [menu_option.as_choice() for menu_option in cls]
            if filter_lambda is None
            else [menu_option.as_choice() for menu_option in cls if filter_lambda(menu_option)]
        )

    @classmethod
    def choose(
        cls,
        message: str,
        filter_lambda_or_options: Callable[[Self], bool] | Sequence[Self | Choice] | None = None,
        default: Self | None = None,
    ) -> Self:
        choices: list[Choice] = []

        # Load choices
        if isinstance(filter_lambda_or_options, (list, Sequence)):
            for option in filter_lambda_or_options:
                if not cls.is_valid_option(option):
                    raise TypeError(
                        f"One or more of the provided options is not an instance of either Choice or {cls.__name__}"
                    )

                choices.append(option if isinstance(option, Choice) else option.as_choice())
        else:
            choices = cls.all_as_choices(filter_lambda_or_options)

        # Select the correct default, if provided
        default_choice = None if default is None else next(choice for choice in choices if choice.value == default)

        # Ask the question
        return questionary.select(message, choices=choices, default=default_choice).unsafe_ask()

    @classmethod
    def is_valid_option(cls, option: Any):
        if isinstance(option, Choice):
            option = option.value

        return isinstance(option, cls)

    def as_choice(self) -> Choice:
        return Choice(self.name, self)


class Resolution(int, MenuOption):
    KEEP = -1, "Keep original size"
    R_2880P = 2880, "2880p (5K UHD)"
    R_2160P = 2160, "2160p (4K UHD)"
    R_1440P = 1440, "1440p (QHD)"
    R_1080P = 1080, "1080p (FHD)"
    R_720P = 720, "720p (HD)"

    def __new__(cls, value: int, _: str):
        member = int.__new__(cls, value)
        member._value_ = value

        return member

    def __init__(self, value: int, name: str):
        super().__init__()
        self._value_ = value
        self._name_ = name

    @classmethod
    def __by_condition(
        cls,
        filter_lambda: Callable[[Resolution], bool],
        include_keep_original: bool = True,
    ) -> list[Self]:
        return cls.all(
            lambda res: (
                (res != Resolution.KEEP and filter_lambda(res)) or (res == Resolution.KEEP and include_keep_original)
            )
        )

    @classmethod
    def lteq(
        cls,
        limit: int,
        include_keep_original: bool = True,
    ) -> list[Self]:
        """Returns all resolutions lower than or equal to the provided limit."""

        return cls.__by_condition(
            lambda resolution: resolution <= limit,
            include_keep_original,
        )

    @classmethod
    def gteq(
        cls,
        limit: int,
        include_keep_original: bool = True,
    ) -> list[Self]:
        """Returns all resolutions greater than or equal to the provided limit."""

        return cls.__by_condition(
            lambda resolution: resolution >= limit,
            include_keep_original,
        )

    @classmethod
    def between(
        cls,
        lower_limit: int,
        upper_limit: int,
        include_keep_original: bool = True,
    ) -> list[Self]:
        """Returns all resolutions between the provided limits, both range edges included."""

        return cls.__by_condition(
            lambda resolution: lower_limit <= resolution <= upper_limit,
            include_keep_original,
        )


def ask_for_source_dir(file_type: str) -> str:
    return questionary.path(
        f"Where are the {file_type} you want to optimize?",
        os.path.join(Path.home(), ""),
        only_directories=True,
    ).unsafe_ask()


def ask_for_short_side_limit(resolution_options: Sequence[Resolution | Choice] | None = None) -> int:
    return Resolution.choose(
        "Would you like to limit output resolution? Choose max length of shortest side:",
        resolution_options,
    )


def ask_for_overwrite_permission(files: Files[GenericFile]) -> bool:
    return questionary.confirm(
        f"Overwrite existing files in target directory {files.target_dir}?",
    ).unsafe_ask()

# pyright: reportUnknownParameterType=false
# pyright: reportUnknownArgumentType=false
# pyright: reportUnknownLambdaType=false
# pyright: reportUnknownVariableType=false
# pyright: reportUnknownMemberType=false

import argparse
import fileinput
import re
import subprocess
import sys
from pathlib import Path

from src._version import __VERSION__, __VERSION_INFO__


def valid_version(version: str) -> tuple[int, int, int]:
    if re.match(r"^[0-9]+\.[0-9]+\.[0-9]+$", version) is not None:
        return tuple(map(int, version.split(".")))  # type: ignore

    raise argparse.ArgumentTypeError("The version must be in the format MAJOR.MINOR.PATCH")


def set_version(major: int, minor: int, patch: int):
    old_version = __VERSION__
    new_version = f"{major}.{minor}.{patch}"

    __set_version_in_py_module(major, minor, patch)
    __set_version_in_toml_file(major, minor, patch)
    __set_version_in_readme(major, minor, patch)
    __set_version_in_dist_readme(major, minor, patch)

    subprocess.run(["uv", "lock"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print(f"Updated project version from {old_version} to {new_version}")


def bump_major_version():
    set_version(__VERSION_INFO__[0] + 1, 0, 0)


def bump_minor_version():
    set_version(__VERSION_INFO__[0], __VERSION_INFO__[1] + 1, 0)


def bump_patch_version():
    set_version(__VERSION_INFO__[0], __VERSION_INFO__[1], __VERSION_INFO__[2] + 1)


def __set_version_in_py_module(major: int, minor: int, patch: int):
    path = Path(__file__).parent.parent.joinpath("_version.py")
    py_str = f"__VERSION_INFO__ = ({major}, {minor}, {patch})"

    for line in fileinput.input(path, inplace=True):
        sys.stdout.write(re.sub(r"^__VERSION_INFO__ = \([0-9]+, [0-9]+, [0-9]+\)", py_str, line))


def __set_version_in_toml_file(major: int, minor: int, patch: int):
    path = Path(__file__).parent.parent.parent.joinpath("pyproject.toml")
    toml_str = f'version = "{major}.{minor}.{patch}"'

    for line in fileinput.input(path, inplace=True):
        sys.stdout.write(re.sub(r"^version = \"[0-9]+\.[0-9]+\.[0-9]+\"", toml_str, line))


def __set_version_in_readme(major: int, minor: int, patch: int):
    path = Path(__file__).parent.parent.parent.joinpath("README.md")
    readme_str = f"# Media Optimizer v{major}.{minor}.{patch}"

    for line in fileinput.input(path, inplace=True):
        sys.stdout.write(re.sub(r"^# Media Optimizer v[0-9]+\.[0-9]+\.[0-9]+", readme_str, line))


def __set_version_in_dist_readme(major: int, minor: int, patch: int):
    path = Path(__file__).parent.parent.parent.joinpath("build", "release_files", "README.txt")
    readme_str = f"Media Optimizer v{major}.{minor}.{patch}"

    for line in fileinput.input(path, inplace=True):
        sys.stdout.write(re.sub(r"^Media Optimizer v[0-9]+\.[0-9]+\.[0-9]+", readme_str, line))

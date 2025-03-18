# pyright: reportUnknownParameterType=false
# pyright: reportUnknownArgumentType=false
# pyright: reportUnknownLambdaType=false
# pyright: reportUnknownVariableType=false
# pyright: reportUnknownMemberType=false

import platform
import zipfile
from dataclasses import dataclass
from pathlib import Path

import PyInstaller.__main__
import pymediainfo

import media_optimizer
from src._version import __VERSION__

ROOT = Path(media_optimizer.__file__).parent

RELEASE_SUFFIXES = {
    "Windows": "windows-x64",
    "Linux": "linux-x64",
    "Darwin": {
        "x86_64": "macos-x64",
        "arm64": "macos-arm64",
    },
}


@dataclass
class PackedFile:
    location: Path
    destination: Path


RELEASE_PACKED_FILES = [
    PackedFile(
        location=ROOT.joinpath("LICENSE"),
        destination=Path("LICENSE.txt"),
    ),
    PackedFile(
        location=ROOT.joinpath("build", "release_files", "README.TXT"),
        destination=Path("README.TXT"),
    ),
    PackedFile(
        location=Path(pymediainfo.__path__[0], "License.html"),
        destination=Path("third-party", "licenses", "MediaInfo.html"),
    ),
]


class BuildError(Exception):
    pass


def build(is_for_release: bool = False):
    PyInstaller.__main__.run([str(ROOT.joinpath("build", "build.spec"))])

    if is_for_release:
        pack_for_release()


def pack_for_release():
    print("Packing for release...")

    system = platform.system()
    suffix_data = RELEASE_SUFFIXES.get(system)
    if suffix_data is None:
        raise BuildError(f"Not prepared to build a release for the current system: {system}")

    arch = platform.machine()
    suffix = suffix_data if isinstance(suffix_data, str) else suffix_data.get(arch)
    if suffix is None:
        raise BuildError(f"Not prepared to build a release for the current architecture: {arch}")

    zip_name = f"media-optimizer-{__VERSION__}-{suffix}.zip"
    exe_name = "media_optimizer"
    if system == "Windows":
        exe_name += ".exe"

    print(f"Creating {zip_name}...")

    zf = zipfile.ZipFile(ROOT.joinpath("dist", zip_name), "w", zipfile.ZIP_DEFLATED)

    zf.write(ROOT.joinpath("dist", exe_name), exe_name)

    for packed_file in RELEASE_PACKED_FILES:
        zf.write(packed_file.location, packed_file.destination)

    zf.close()

    print("Done!")

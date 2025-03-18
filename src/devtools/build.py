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
    skip_if_not_found: bool = False


RELEASE_PACKED_FILES = [
    # Media Optimizer license
    PackedFile(
        location=ROOT.joinpath("LICENSE"),
        destination=Path("LICENSE.txt"),
    ),
    # Basic README file
    PackedFile(
        location=ROOT.joinpath("build", "release_files", "README.txt"),
        destination=Path("README.txt"),
    ),
    # Third-party licenses
    PackedFile(
        location=Path(pymediainfo.__path__[0], "License.html"),  # type: ignore
        destination=Path("third-party", "licenses", "MediaInfo.html"),
        skip_if_not_found=True,
    ),
    PackedFile(
        location=Path(pymediainfo.__path__[0], "LICENSE"),  # type: ignore
        destination=Path("third-party", "licenses", "MediaInfo.txt"),
        skip_if_not_found=True,
    ),
]


class BuildError(Exception):
    pass


def build(is_for_release: bool = False):
    system = platform.system()

    os_spec_file = ROOT.joinpath("build", f"media_optimizer--{system.lower()}.spec")
    default_spec_file = ROOT.joinpath("build", "media_optimizer.spec")
    spec_file_path = os_spec_file if os_spec_file.exists() else default_spec_file

    PyInstaller.__main__.run([str(spec_file_path)])

    if is_for_release:
        __pack_for_release(system)


def __pack_for_release(system: str):
    print("Packing for release...")

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
        try:
            zf.write(packed_file.location, packed_file.destination)
        except FileNotFoundError as err:
            if packed_file.skip_if_not_found:
                continue
            else:
                raise err

    zf.close()

    print("Done!")

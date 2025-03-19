# pyright: reportUnknownParameterType=false
# pyright: reportUnknownArgumentType=false
# pyright: reportUnknownLambdaType=false
# pyright: reportUnknownVariableType=false
# pyright: reportUnknownMemberType=false

import platform
import subprocess
import zipfile
from dataclasses import dataclass
from pathlib import Path

import PyInstaller.__main__
import pymediainfo

import media_optimizer
from src._version import __VERSION__

ROOT = Path(media_optimizer.__file__).parent

EXE_NAME = "media_optimizer"

ARCH_X86_64 = "x86_64"
ARCH_ARM64 = "arm64"

OS_WINDOWS = "Windows"
OS_LINUX = "Linux"
OS_MACOS = "Darwin"

RELEASE_SUFFIXES = {
    OS_WINDOWS: "windows-x64",
    OS_LINUX: "linux-x64",
    OS_MACOS: {
        ARCH_X86_64: "macos-x86_64",
        ARCH_ARM64: "macos-arm64",
    },
}

PYTHON_VERSION = ROOT.joinpath(".python-version").read_text("utf-8").strip()
MACOS_CPYTHON_X64 = f"cpython-{PYTHON_VERSION}-macos-x86_64-none"
MACOS_CPYTHON_ARM64 = f"cpython-{PYTHON_VERSION}-macos-aarch64-none"


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


def build(is_for_release: bool = False, is_building_for_macos: bool = False):
    system = platform.system()
    arch = platform.machine()

    if system == OS_MACOS and not is_building_for_macos:
        # If system is MacOS but the build command is not already running in MacOS build mode,
        # then re-run it in MacOS build mode to build both x86_64 and arm64 at once.
        __macos_build(arch, is_for_release)

        return

    os_spec_file = ROOT.joinpath("build", f"{EXE_NAME}--{system.lower()}.spec")
    default_spec_file = ROOT.joinpath("build", f"{EXE_NAME}.spec")
    spec_file_path = os_spec_file if os_spec_file.exists() else default_spec_file

    pyinstaller_args = ["-y", str(spec_file_path)]
    if is_building_for_macos:
        pyinstaller_args = [
            "--workpath",
            f"./build/{arch}",
            "--distpath",
            f"./dist/{arch}",
            *pyinstaller_args,
        ]

    PyInstaller.__main__.run(pyinstaller_args)

    if is_for_release:
        __pack_for_release(system, arch)


def __macos_build(arch: str, is_for_release: bool = False):
    subprocess.run(__macos_get_build_command(MACOS_CPYTHON_X64, is_for_release), check=True)

    if arch == ARCH_ARM64:
        subprocess.run(__macos_get_build_command(MACOS_CPYTHON_ARM64, is_for_release), check=True)


def __macos_get_build_command(python: str, is_for_release: bool):
    args = ["uv", "run", "--python", python, "devtools.py", "build", "--macos"]
    if is_for_release:
        args.append("-r")

    return args


def __pack_for_release(system: str, arch: str):
    print("Packing for release...")

    suffix_data = RELEASE_SUFFIXES.get(system)
    if suffix_data is None:
        raise BuildError(f"Not prepared to build a release for the current system: {system}")

    suffix = suffix_data if isinstance(suffix_data, str) else suffix_data.get(arch)
    if suffix is None:
        raise BuildError(f"Not prepared to build a release for the current architecture: {arch}")

    zip_name = f"media-optimizer-{__VERSION__}-{suffix}.zip"
    exe_source_name = EXE_NAME
    exe_target_name = EXE_NAME
    if system == OS_MACOS:
        exe_source_name = f"{arch}/{exe_source_name}"
    elif system == OS_WINDOWS:
        exe_source_name += ".exe"
        exe_target_name += ".exe"

    print(f"Creating {zip_name}...")

    zf = zipfile.ZipFile(ROOT.joinpath("dist", zip_name), "w", zipfile.ZIP_DEFLATED)

    zf.write(ROOT.joinpath("dist", exe_source_name), exe_target_name)

    for packed_file in RELEASE_PACKED_FILES:
        try:
            zf.write(packed_file.location, packed_file.destination)
        except FileNotFoundError as err:
            if packed_file.skip_if_not_found:
                continue

            raise err

    zf.close()

    print("Done!")

import subprocess
import sys

from src.components.app import get_app_path

LICENSES_INFO_FILE_NAME = "licenses-info.json"
LICENSES_INFO_PATH = get_app_path().joinpath("build", LICENSES_INFO_FILE_NAME)


def list_python_dependencies_licenses(save: bool = False):
    args = [
        "uv",
        "run",
        "pip-licenses",
        "--with-system",
        "--with-urls",
        "--no-version",
    ]

    stdout = sys.stdout
    if save:
        args.append("--with-license-file")
        args.append("--with-notice-file")
        args.append("--format=json")
        stdout = open(LICENSES_INFO_PATH, "w", encoding="utf-8")

    subprocess.run(args, check=True, stdout=stdout)

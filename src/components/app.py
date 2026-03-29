import os
import sys
from pathlib import Path


def get_app_path() -> Path:
    if is_running_in_bundled_mode():
        return Path(sys.executable).parent

    return Path(sys.path[0])


def is_running_in_bundled_mode() -> bool:
    return getattr(sys, "frozen", False)


def is_running_in_app_path() -> bool:
    return str(get_app_path()) == os.getcwd()

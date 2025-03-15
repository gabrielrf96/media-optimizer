"""
Utility commands for Media Optimizer development.
"""

import argparse

from src.devhelpers import bump_major_version, bump_minor_version, bump_patch_version, set_version, valid_version


def main():
    parser = get_arg_parser()
    args = parser.parse_args()

    if args.set_version is not None:
        set_version(*args.set_version)
    elif args.bump_major:
        bump_major_version()
    elif args.bump_minor:
        bump_minor_version()
    elif args.bump_patch:
        bump_patch_version()
    else:
        parser.print_help()


def get_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Utility commands for Media Optimizer development")

    parser.add_argument(
        "-sv",
        "--set-version",
        type=valid_version,
        metavar="MAJOR.MINOR.PATCH",
        help="set full version",
    )
    parser.add_argument("-bv", "--bump-major", action="store_true", help="bump major version")
    parser.add_argument("-bm", "--bump-minor", action="store_true", help="bump minor version")
    parser.add_argument("-bp", "--bump-patch", action="store_true", help="bump patch version")

    return parser


if __name__ == "__main__":
    main()

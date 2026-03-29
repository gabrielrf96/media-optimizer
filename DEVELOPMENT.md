# Setting up the project
1. **Install** the **project manager**, `uv`: [astral-sh/uv](https://github.com/astral-sh/uv)

2. **Clone** the repository and install the necessary dependencies.
    ```sh
    git clone https://github.com/gabrielrf96/media-optimizer.git
    cd media-optimizer
    uv sync
    ```

3. **Set your IDE's Python interpreter** to the one inside the project's venv: `.venv/bin/python` or `.venv/Scripts/python` *(on Windows)*

    If you're using Visual Studio Code, you can just use the included example settings file, which also provide some other useful default settings for the workspace:

    ```sh
    cd .vscode
    cp settings.example.json settings.json

    # If you're on Windows, use the Windows example JSON settings file instead:
    copy settings.example.win.json settings.json
    ```

## Recommended Visual Studio Code extensions
- **Python** *(Microsoft)*
- **Pylint** *(Microsoft)*
- **Black Formatter** *(Microsoft)*
- **isort** *(Microsoft)*

# General guidelines
- Changes should always be worked on in **feature branches**, and merged to master only when they are stable or prepared for a new release.
- Commit history in feature branches should be kept when it is deemed valuable. Therefore, an effort should be made to keep commit history clean in feature branches.
- For minor features or hotfixes, commits may be squashed if keeping the entire history does not seem valuable.

# Bumping version
1. Bump the version using the project's devtools command:
    ```sh
    # Bump MAJOR version
    uv run devtools.py version -b  # or --bump-major

    # Bump MINOR version
    uv run devtools.py version -m  # or --bump-minor

    # Bump PATCH version
    uv run devtools.py version -p  # or --bump-patch
    ```

2. Create a new git tag with the corresponding version, following the format `vX.Y.Z`, where:
    - `X` = major
    - `Y` = minor
    - `Z` = patch

3. Push the changes and the new tag.

# Releasing a new version
1. **Bump the version** by following the instructions from the previous section. Choose the correct bump type *(major, minor or patch)* depending on the nature of the changes you are introducing.

2. **Merge the changes into master and push them**, making sure you first update your branch with any changes that may have been developed there *(by either merging master into your branch, or rebasing onto main if your branch is not public yet)*.

    If your branch is for a hotfix or minor feature, consider squashing your commits if keeping the full history does not seem valuable.

3. **Build the executables** in release mode, for all supported platforms:
    ```sh
    uv run devtools.py build -r  # or --release

    # Repeat for Windows, Linux, Mac OS (Intel and Apple Silicon)
    ```

    3.1. When building release-ready distributables on an Apple Silicon Mac, both the x86_64 and arm64 versions should be built. If that is not happening, check out [step 2.1.](#build-from-source-macos) of the ["Building from source"](#building-from-source) section.

4. **Create a new release on GitHub** and attach the zip files generated in the previous step. Include a reasonably detailed changelog in the release description.

## Third-party license management

Building for release will generally handle third-party licenses in the bundled archive, but you need to take this into account:

- The Python dependencies will be handled automatically, including transitive dependencies. In some cases, like Pillow, the underlying necessary image handling libraries' licenses are also handled automatically (provided the Python dependency correctly handles their own third-party licenses).
- For some dependencies like MediaInfo, licenses have to be handled manually. This is, of course, already done for MediaInfo itself, but new cases might appear in the future. This also applies to the Python license itself, which is also handled manually.
- When building on each platform, some extra system libraries and third-party dependencies might be included, and they might also differ between systems. These also need to be taken into account. This is the case for things like OpenSSL and `libffi` libraries, or the Microsoft runtime DLLs on Windows.

Therefore, it is highly recommended that you re-check the bundled executable by extracting it and reviewing that no new unhandled third-party licensed dependencies have been introduced. If new ones have been included, and their licenses haven't been handled automatically, you will need to manually include them in the `build/release_files/` directory, and declare them as `PackedFile`s in `src/devtools/build.py` if a new file has been added.

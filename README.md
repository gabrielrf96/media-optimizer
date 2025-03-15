# Media Optimizer v0.2.0
A simple **CLI tool** designed to **optimize different media files** *(pictures and videos)* through a user-friendly interface, with keyboard-navigable menus, progress bars and extensive options to tweak its behavior and output quality.

**For pictures:**<br/>
<img width="80%" src="graphic/usage_pictures.gif">

**For videos:**<br/>
<img width="80%" src="graphic/usage_videos.gif">

## Result examples

**For pictures:**
- **Input**: 55 high-quality, 6240x4160 JPEG pictures taken with a DSLR camera, totalling **1.17 GiB**.
- **Options**: size=original, format=original, quality=80
- **Output**: **256.57 MiB** *(78.5% less)*

![images](graphic/result_pictures.png)

**For videos:**<br/>
- **Input**: 2 high-quality, 3840x2160 MPEG-4/H.264 videos recorded with a smartphone, totalling **460.37 MiB**
- **Options**: size=original, quality=22 *(no noticeable difference)*, preset=medium
- **Output**: **100.47 MiB** *(78.2% less)*

![images](graphic/result_videos.png)

# Dependencies
Python dependencies are managed by the project, so you just need to follow the instructions below to use the tool.

However, there are some external dependencies that you will need to install manually for your system:
- Global:
    - [**MediaInfo**](https://mediaarea.net/en/MediaInfo)
- Required only for video optimization:
    - [**ffmpeg**](https://www.ffmpeg.org) *(>= 6.0)*
    - **libx265**

# Instructions

> [!WARNING]
> I created this tool to reduce the size of pictures and videos, saving space for **storage in cloud services** and **regular display usage**, where high-accuracy data and ultrafine detail are not necessary.
>
> Therefore, in most cases, **lossy compression** is used for these kinds of files.
>
> If you want to optimize your pictures and videos for the same reason as I do, go ahead and use this tool. If, on the contrary, you need to retain high-detail data for editing, publishing or similar usages, using this tool to reduce the size of the source material is highly discouraged.

## For regular usage
1. **Install** the **project manager**, `uv`: [astral-sh/uv](https://github.com/astral-sh/uv)

    If you don't want to install this tool, you can use your own machine's Python *(>= 3.13)*. You will need to manually install the project's Python dependencies listed in the `pyproject.toml` file.

2. **Clone** the repository, or download it as a zip file.

3. **Go into** the tool's directory: `cd media-optimizer`

4. **Install Python dependencies** and init the project: `uv sync --no-dev`

    Done! Now you can just run the tool using `uv`:

    ```sh
    uv run media_optimizer.py
    ```

    You will be presented with an interactive menu where you can easily choose which tool you want to use, where the files you want to optimize are located, and which optimization options to use.

    Note that if you run the script using your own machine's Python, it will fail unless you have the project's dependencies installed locally. `uv` is the recommended and most convenient way to run the tool.

## For development

### Setting up the project
1. **Install** the **project manager**, `uv`: [astral-sh/uv](https://github.com/astral-sh/uv)
2. **Clone** the repository and install the necessary dependencies.
    ```sh
    git clone https://github.com/gabrielrf96/media-optimizer.git
    cd media-optimizer
    uv sync
    ```
5. **Set your IDE's Python interpreter** to the one inside the project's venv: `.venv/bin/python` or `.venv/Scripts/python` *(in Windows)*

    If you're using Visual Studio Code, you can just use the included example settings file, which also provide some other useful default settings for the workspace:

    ```sh
    cd .vscode
    cp settings.example.json settings.json

    # If you're on Windows, use the Windows example JSON settings file instead:
    cp settings.example.win.json settings.json
    ```

### Bumping version
1. Bump the version using the project's devtools command:
    ```sh
    # Bump MAJOR version
    uv run devtools.py -bv # or --bump-major

    # Bump MINOR version
    uv run devtools.py -bm # or --bump-minor

    # Bump PATCH version
    uv run devtools.py -bp # or --bump-patch
    ```
2. Create a new git tag with the corresponding version, following the format `vX.Y.Z`, where:
    - `X` = major
    - `Y` = minor
    - `Z` = patch
3. Push the changes and the new tag.

### Recommended Visual Studio Code extensions
- **Python** *(Microsoft)*
- **Pylint** *(Microsoft)*
- **Black Formatter** *(Microsoft)*
- **isort** *(Microsoft)*

# Bug reporting and contact
If you experience any kind of trouble while using this tool, please feel free to contact me to report any bugs or problems.

You can contact me by:

- Opening an <a href="https://github.com/gabrielrf96/media-optimizer/issues">**issue on GitHub**</a>
- Sending me an e-mail at <a href="mailto:contact@gabrielrf.dev">**contact@gabrielrf.dev**</a>

<br/>
<br/>
<p align="center">
    Made by Gabriel Rodríguez
    <br/>
    <a href="https://www.gabrielrf.dev">www.gabrielrf.dev</a>
</p>

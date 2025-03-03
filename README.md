# Media Optimizer
A series of utility scripts I've created over time to reduce the size of different media files *(pictures and videos)*, packed together in a single repository and tool.

The scripts are usable from the terminal from a single entry point, `media_optimizer.py`, and provide a keyboard-navigable menu to easily choose tools and set options.

# Dependencies
Python dependencies are managed by the project, so you just need to follow the instructions below to use the optimizer.

However, there are 3 external dependencies that you will need to install manually for your system:
- [**MediaInfo**](https://mediaarea.net/en/MediaInfo)
- [**ffmpeg**](https://www.ffmpeg.org) *(>= 6.0) (only necessary for video optimization)*
- **libx265** *(only necessary for video optimization)*

# Instructions

## For regular usage
1. **Install** the **project manager**, `uv`: [astral-sh/uv](https://github.com/astral-sh/uv)

    If you don't want to install this tool, you can use your own machine's Python *(>= 3.13)*. You will need to manually install the project's Python dependencies listed in the `pyproject.toml` file.

2. **Clone** the repository, or download it as a zip file.

3. **Go into** the tool's directory: `cd media-optimizer`

4. **Install Python dependencies** and init the project: `uv sync --no-dev`

    Done! Now you can just run the tool using `uv`:

    ```console
    uv run media_optimizer.py
    ```

    You will be presented with an interactive menu where you can easily choose which tool you want to use, where the files you want to optimize are located, and which optimization options to use.

    Note that if you run the script using your own machine's Python, it will fail unless you have the project's dependencies installed locally. `uv` is the recommended and most convenient way to run the tool.

## For development
1. **Install** the **project manager**, `uv`: [astral-sh/uv](https://github.com/astral-sh/uv)
2. **Clone** the repository, or download it as a zip file.
3. **Go into** the tool's directory: `cd media-optimizer`
4. **Install Python dependencies** and init the project: `uv sync`
5. **Set your IDE's Python interpreter** to the one in the project's venv: `.venv/Scripts/python`

    If you're using Visual Studio Code, you can just use the included example settings file:

    ```console
    cd .vscode
    cp settings.example.json settings.json
    ```

Recommended Visual Studio Code extensions:
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

# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

import pymediainfo

mediainfo_bin_location = Path(pymediainfo.__path__[0]).joinpath("libmediainfo.so.0")

a = Analysis(
    ["../media_optimizer.py"],
    pathex=[],
    binaries=[
        (str(mediainfo_bin_location), "."),
    ],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="media_optimizer",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

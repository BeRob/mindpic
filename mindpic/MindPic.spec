# -*- mode: python ; coding: utf-8 -*-

import os
import sys

# =============================================================================
# USER CONFIG (hier anpassen)
# =============================================================================
APP_NAME    = "MindPic"
APP_VERSION = "1.1.0"

# PyInstaller stellt SPECPATH bereit: Ordner, in dem die .spec liegt
PROJECT_DIR  = SPECPATH

ENTRY_SCRIPT = os.path.join(PROJECT_DIR, "run_mindpic.py")

ASSETS_DIR   = os.path.join(PROJECT_DIR, "assets")
ICON_PATH    = os.path.join(ASSETS_DIR, "mindpic.ico")

ASSET_FILES = [
    ("mindpic.ico", "assets"),
    ("mindpic_tray.png", "assets"),
    ("Mindpic_Manual.pdf", "assets"),
]

# Some Python distributions (for example uv-managed CPython builds) keep Tcl/Tk
# shared libraries next to the interpreter instead of in a system library path.
# PyInstaller collects the Tcl/Tk data files automatically but can miss these
# two shared libraries, which makes the bundled app fail at tkinter import time.
TCL_TK_LIBS = [
    os.path.join(sys.base_prefix, "lib", "libtcl9.0.so"),
    os.path.join(sys.base_prefix, "lib", "libtcl9tk9.0.so"),
]
# =============================================================================

block_cipher = None

datas = [(os.path.join(ASSETS_DIR, fname), dest) for fname, dest in ASSET_FILES]
binaries = [(os.path.abspath(path), ".") for path in TCL_TK_LIBS if os.path.exists(path)]

a = Analysis(
    [ENTRY_SCRIPT],
    pathex=[PROJECT_DIR],
    binaries=binaries,
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon=ICON_PATH,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    name=APP_NAME,
)

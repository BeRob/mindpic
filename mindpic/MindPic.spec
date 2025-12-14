# -*- mode: python ; coding: utf-8 -*-

import os

# =============================================================================
# USER CONFIG (hier anpassen)
# =============================================================================
APP_NAME    = "MindPic"
APP_VERSION = "1.0.0"

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
# =============================================================================

block_cipher = None

datas = [(os.path.join(ASSETS_DIR, fname), dest) for fname, dest in ASSET_FILES]

a = Analysis(
    [ENTRY_SCRIPT],
    pathex=[PROJECT_DIR],
    binaries=[],
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

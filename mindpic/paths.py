# File: mindpic/paths.py
# -*- coding: utf-8 -*-
"""
MindPic – Pfade & Ressourcen-Auflösung.

Ziele:
- In DEV: Assets aus DEV_PROJECT_DIR laden, Daten dort speichern (oder Override).
- In EXE (PyInstaller): Assets aus _MEIPASS laden, Daten im EXE-Ordner speichern.
"""

from __future__ import annotations

import sys
from pathlib import Path

from . import settings


# =============================================================================
# USER OPTION (optional hier überschreiben, sonst settings.py nutzen)
# =============================================================================
# lokal override setzen – normal reicht settings.SAVE_DIR_OVERRIDE
SAVE_DIR_OVERRIDE: str | None = None  # z.B. r"D:\Coding\Projekte\MindPic\data"


def _is_frozen() -> bool:
    """True, wenn als PyInstaller-EXE läuft."""
    return bool(getattr(sys, "frozen", False))


def get_exe_dir() -> Path:
    """Ordner, in dem die EXE liegt (oder beim DEV: der Script-Ordner)."""
    if _is_frozen():
        return Path(sys.executable).resolve().parent
    # DEV: __main__.py liegt im Package; wir nutzen settings.DEV_PROJECT_PATH als Basispunkt
    return settings.DEV_PROJECT_PATH.resolve()


def get_data_dir() -> Path:
    """
    Verzeichnis für schreibbare Daten (config/content/logs).
    - Priorität: lokaler Override in dieser Datei -> settings.SAVE_DIR_OVERRIDE -> EXE-Dir / DEV-Dir
    """
    override = SAVE_DIR_OVERRIDE or settings.SAVE_DIR_OVERRIDE
    if override:
        return Path(override).expanduser().resolve()

    return get_exe_dir()


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_meipass_dir() -> Path | None:
    """
    PyInstaller extrahiert bei onefile nach _MEIPASS.
    Dort liegen zur Laufzeit die gebundelten Assets.
    """
    mp = getattr(sys, "_MEIPASS", None)
    return Path(mp).resolve() if mp else None


def resource_path(relative_path: str | Path) -> Path:
    """
    Asset-Pfad auflösen:
    - PyInstaller: _MEIPASS/<relative_path>
    - DEV: DEV_PROJECT_DIR/<relative_path>
    """
    rel = Path(relative_path)

    if _is_frozen():
        meipass = get_meipass_dir()
        if meipass:
            return (meipass / rel).resolve()

    return (settings.DEV_PROJECT_PATH / rel).resolve()


# =============================================================================
# Convenience: Standard-Dateipfade
# =============================================================================

def get_assets_dir() -> Path:
    return resource_path(settings.ASSETS_DIR_REL)


def get_app_icon_path() -> Path:
    return resource_path(settings.ICON_APP_REL)


def get_tray_icon_path() -> Path:
    return resource_path(settings.ICON_TRAY_REL)


def get_manual_path() -> Path:
    return resource_path(settings.MANUAL_REL)


def get_config_path() -> Path:
    return (get_data_dir() / settings.CONFIG_FILE_NAME).resolve()


def get_content_path() -> Path:
    return (get_data_dir() / settings.CONTENT_FILE_NAME).resolve()


def get_geometry_path() -> Path:
    return (get_data_dir() / settings.GEOMETRY_FILE_NAME).resolve()


def get_log_path() -> Path:
    return (get_data_dir() / settings.LOG_FILE_NAME).resolve()

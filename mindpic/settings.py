# File: mindpic/settings.py
# -*- coding: utf-8 -*-
"""
MindPic – zentrale, editierbare Einstellungen.

Wichtig:
- Pfade/Hotkeys/Defaults NUR hier ändern
- Alle anderen Module importieren diese Werte.
"""

from __future__ import annotations

from pathlib import Path

# =============================================================================
# USER CONFIG (hier anpassen)
# =============================================================================

APP_NAME: str = "MindPic"

# Projektbasis (nur für DEV; in der EXE wird automatisch der EXE-Ordner genutzt)
DEV_PROJECT_DIR: str = r"D:\Coding\Projekte\MindPic"

# Optional: Speicherort hart überschreiben (z.B. Netzlaufwerk).
# Wenn None: in EXE -> Ordner der EXE, in DEV -> DEV_PROJECT_DIR
SAVE_DIR_OVERRIDE: str | None = None

# Hotkeys
# - LOCAL_TOGGLE_KEY: bind auf Tk-Fenster (funktioniert nur wenn fokussiert)
# - GLOBAL_TOGGLE_HOTKEY: systemweit (benötigt "keyboard"; falls nicht vorhanden, wird es deaktiviert)
LOCAL_TOGGLE_KEY: str = "<F9>"
GLOBAL_TOGGLE_HOTKEY: str = "f9"

# Tray aktivieren (pystray + pillow nötig)
ENABLE_TRAY: bool = True

# Auto-Hide bei Fokusverlust (wenn True: Fenster verschwindet nach kurzer Zeit, sobald es Fokus verliert)
DEFAULT_AUTO_HIDE_ON_FOCUS_LOST: bool = False
AUTO_HIDE_DELAY_MS: int = 650  # Verzögerung bevor ausgeblendet wird

# Fenster / Verhalten
DEFAULT_ALWAYS_ON_TOP: bool = True
DEFAULT_BORDERLESS: bool = False
DEFAULT_WINDOW_ALPHA: float = 0.92  # 0.2 .. 1.0
DEFAULT_SNAP_DISTANCE: int = 16
DEFAULT_MIN_WIDTH: int = 420
DEFAULT_MIN_HEIGHT: int = 220

# Text/Optik
DEFAULT_FONT_FAMILY: str = "Dosis"     # fällt zurück, wenn nicht installiert
DEFAULT_FONT_SIZE: int = 12
DEFAULT_TEXT_FG: str = "#F2F2F2"
DEFAULT_TEXT_BG: str = "#151515"

# Eintragsfarben (für farbige Blöcke, falls du so ein Feature nutzt)
DEFAULT_NOTE_COLORS: list[str] = [
    "#1e1e1e",
    "#222034",
    "#1f2a1f",
    "#2b1f1f",
    "#1f2b2b",
]

# Autosave
AUTOSAVE_INTERVAL_MS: int = 1500  # Inhalt/State regelmäßig speichern

# Hotkeys
ENABLE_GLOBAL_HOTKEYS: bool = True  # Global hotkeys aktivieren/deaktivieren

# Logging
LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FILE_NAME: str = "mindpic.log"

# =============================================================================
# UI / STYLING (aus ui.py verschoben für zentrale Konfiguration)
# =============================================================================

# Theme
UI_THEME_NAME: str = "clam"  # ttk Theme ("clam" funktioniert gut für Dark-Styles)

# Transparenz-Presets für UI-Menü
UI_ALPHA_PRESETS: list[tuple[float, str]] = [
    (0.50, "50%"),
    (0.70, "70%"),
    (0.85, "85%"),
    (0.95, "95%"),
    (1.00, "100%"),
]

# Button & Layout Padding
UI_BUTTON_PAD_XY: tuple[int, int] = (8, 2)   # padding=(x,y) für Toolbar-Button
UI_MAIN_PADDING: tuple[int, int, int, int] = (6, 6, 6, 4)  # left, top, right, bottom

# Borderless-Mode Einstellungen
UI_BORDERLESS_GRIP_SYMBOL: str = "⋰"
UI_BORDERLESS_GRIP_OFFSET_PX: int = 2
UI_BORDERLESS_MIN_WIDTH: int = 260
UI_BORDERLESS_MIN_HEIGHT: int = 180

# =============================================================================
# Assets / Dateinamen (normalerweise nicht anfassen)
# =============================================================================

# Relativ zu DEV_PROJECT_DIR bzw. in der EXE relativ zu _MEIPASS
ASSETS_DIR_REL: str = "assets"
ICON_APP_REL: str = r"assets\mindpic.ico"
ICON_TRAY_REL: str = r"assets\mindpic_tray.png"
MANUAL_REL: str = r"assets\Mindpic_Manual.pdf"

CONFIG_FILE_NAME: str = "config.json"
CONTENT_FILE_NAME: str = "content.txt"
GEOMETRY_FILE_NAME: str = "window_geometry.json"

# =============================================================================
# DEFAULT CONFIG (wird in config.json gespeichert/geladen)
# =============================================================================

DEFAULT_CONFIG: dict = {
    "window_alpha": DEFAULT_WINDOW_ALPHA,
    "always_on_top": DEFAULT_ALWAYS_ON_TOP,
    "borderless": DEFAULT_BORDERLESS,
    "min_width": DEFAULT_MIN_WIDTH,
    "min_height": DEFAULT_MIN_HEIGHT,
    "snap_distance": DEFAULT_SNAP_DISTANCE,
    "text_fg": DEFAULT_TEXT_FG,
    "text_bg": DEFAULT_TEXT_BG,
    "font_family": DEFAULT_FONT_FAMILY,
    "font_size": DEFAULT_FONT_SIZE,
    "note_colors": DEFAULT_NOTE_COLORS,
    "auto_hide_on_focus": DEFAULT_AUTO_HIDE_ON_FOCUS_LOST,
}

# =============================================================================
# Convenience (nur intern)
# =============================================================================

DEV_PROJECT_PATH: Path = Path(DEV_PROJECT_DIR)

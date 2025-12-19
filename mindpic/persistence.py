# File: mindpic/persistence.py
# -*- coding: utf-8 -*-
"""
MindPic – Persistenz für Inhalt (content.txt) und Fenstergeometrie (window_geometry.json).
"""

from __future__ import annotations
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from .paths import ensure_dir, get_content_path, get_geometry_path

logger = logging.getLogger(__name__)


def load_content() -> str:
    """
    Lädt gespeicherten Text. Gibt '' zurück, wenn nicht vorhanden.
    """
    p: Path = get_content_path()
    if not p.exists():
        logger.debug(f"Content file does not exist: {p}")
        return ""
    try:
        content = p.read_text(encoding="utf-8")
        logger.debug(f"Loaded content ({len(content)} chars) from {p}")
        return content
    except (OSError, IOError, UnicodeDecodeError) as e:
        logger.error(f"Failed to load content from {p}: {e}")
        return ""

def save_content(text: str) -> None:
    """
    Speichert Text.
    """
    p: Path = get_content_path()
    try:
        ensure_dir(p.parent)
        p.write_text(text or "", encoding="utf-8")
        logger.debug(f"Saved content ({len(text)} chars) to {p}")
    except (OSError, IOError) as e:
        logger.error(f"Failed to save content to {p}: {e}")

@dataclass
class WindowGeometry:
    width: int | None = None
    height: int | None = None
    x: int | None = None
    y: int | None = None

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "WindowGeometry":
        return cls(
            width=_to_int_or_none(d.get("width")),
            height=_to_int_or_none(d.get("height")),
            x=_to_int_or_none(d.get("x")),
            y=_to_int_or_none(d.get("y")),
        )

    def to_dict(self) -> dict[str, Any]:
        return {"width": self.width, "height": self.height, "x": self.x, "y": self.y}

def _to_int_or_none(v: Any) -> int | None:
    try:
        if v is None:
            return None
        return int(v)
    except Exception:
        return None

def load_window_geometry() -> WindowGeometry:
    """
    Lädt window_geometry.json, falls vorhanden.
    """
    p: Path = get_geometry_path()
    if not p.exists():
        logger.debug(f"Geometry file does not exist: {p}")
        return WindowGeometry()

    try:
        raw = p.read_text(encoding="utf-8")
        data = json.loads(raw) if raw.strip() else {}
        if not isinstance(data, dict):
            logger.warning(f"Invalid geometry data type in {p}: {type(data)}")
            return WindowGeometry()
        geom = WindowGeometry.from_dict(data)
        logger.debug(f"Loaded geometry from {p}: {geom}")
        return geom
    except (OSError, IOError) as e:
        logger.error(f"Failed to read geometry file {p}: {e}")
        return WindowGeometry()
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in geometry file {p}: {e}")
        return WindowGeometry()


def save_window_geometry(geom: WindowGeometry) -> None:
    """
    Speichert window_geometry.json.
    """
    p: Path = get_geometry_path()
    try:
        ensure_dir(p.parent)
        p.write_text(
            json.dumps(geom.to_dict(), ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        logger.debug(f"Saved geometry to {p}: {geom}")
    except (OSError, IOError) as e:
        logger.error(f"Failed to save geometry to {p}: {e}")

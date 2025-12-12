# File: mindpic/persistence.py
# -*- coding: utf-8 -*-
"""
MindPic – Persistenz für Inhalt (content.txt) und Fenstergeometrie (window_geometry.json).
"""

from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from .paths import ensure_dir, get_content_path, get_geometry_path


def load_content() -> str:
    """
    Lädt gespeicherten Text. Gibt '' zurück, wenn nicht vorhanden.
    """
    p: Path = get_content_path()
    if not p.exists():
        return ""
    try:
        return p.read_text(encoding="utf-8")
    except Exception:
        return ""

def save_content(text: str) -> None:
    """
    Speichert Text.
    """
    p: Path = get_content_path()
    ensure_dir(p.parent)
    p.write_text(text or "", encoding="utf-8")

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
        return WindowGeometry()

    try:
        raw = p.read_text(encoding="utf-8")
        data = json.loads(raw) if raw.strip() else {}
        if not isinstance(data, dict):
            return WindowGeometry()
        return WindowGeometry.from_dict(data)
    except Exception:
        return WindowGeometry()


def save_window_geometry(geom: WindowGeometry) -> None:
    """
    Speichert window_geometry.json.
    """
    p: Path = get_geometry_path()
    ensure_dir(p.parent)
    p.write_text(
        json.dumps(geom.to_dict(), ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )

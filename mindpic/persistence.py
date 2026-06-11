# File: mindpic/persistence.py
# -*- coding: utf-8 -*-
"""
MindPic – Persistenz für Notizinhalte, Backups und Fenstergeometrie.
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from . import settings
from .note_store import get_topic_path, normalize_topic_name
from .paths import ensure_dir, get_backups_dir, get_content_path, get_geometry_path, get_notes_dir

logger = logging.getLogger(__name__)


def atomic_write_text(path: Path, text: str) -> None:
    """Write text atomically by replacing the target with a temporary file."""
    ensure_dir(path.parent)
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def atomic_write_json(path: Path, data: dict[str, Any]) -> None:
    atomic_write_text(path, json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True))


def _backup_stem(path: Path, topic: str | None = None) -> str:
    if topic:
        safe = get_topic_path(topic).stem
        return f"{safe}"
    return path.stem


def create_backup(path: Path, *, topic: str | None = None) -> Path | None:
    """Create a timestamped backup of an existing file."""
    if not path.exists():
        return None
    try:
        ensure_dir(get_backups_dir())
        stamp = time.strftime("%Y%m%d_%H%M%S")
        backup_name = f"{_backup_stem(path, topic)}_{stamp}{path.suffix or '.txt'}"
        backup_path = get_backups_dir() / backup_name
        counter = 2
        while backup_path.exists():
            backup_path = get_backups_dir() / f"{_backup_stem(path, topic)}_{stamp}_{counter}{path.suffix or '.txt'}"
            counter += 1
        shutil.copy2(path, backup_path)
        _rotate_backups(_backup_stem(path, topic), path.suffix or ".txt")
        logger.debug("Created backup %s", backup_path)
        return backup_path
    except OSError as e:
        logger.error("Failed to create backup for %s: %s", path, e)
        return None


def _rotate_backups(stem: str, suffix: str) -> None:
    max_count = int(settings.MAX_BACKUPS_PER_NOTE)
    if max_count <= 0:
        return
    backups = sorted(
        get_backups_dir().glob(f"{stem}_*{suffix}"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    for old in backups[max_count:]:
        try:
            old.unlink()
            logger.debug("Removed old backup %s", old)
        except OSError as e:
            logger.warning("Could not remove old backup %s: %s", old, e)


def _path_for_topic(topic: str | None = None) -> Path:
    if topic:
        return get_topic_path(normalize_topic_name(topic))
    return get_content_path()


def load_content(topic: str | None = None) -> str:
    """Load saved text. For the default topic, migrates legacy content.txt on first use."""
    p = _path_for_topic(topic)
    if topic and normalize_topic_name(topic) == settings.DEFAULT_ACTIVE_TOPIC and not p.exists():
        legacy = get_content_path()
        if legacy.exists():
            p = legacy
    if not p.exists():
        logger.debug("Content file does not exist: %s", p)
        return ""
    try:
        content = p.read_text(encoding="utf-8")
        logger.debug("Loaded content (%s chars) from %s", len(content), p)
        return content
    except (OSError, UnicodeDecodeError) as e:
        logger.error("Failed to load content from %s: %s", p, e)
        return ""


def save_content(text: str, topic: str | None = None) -> None:
    """Save text atomically and keep a short backup rotation."""
    p = _path_for_topic(topic)
    try:
        ensure_dir(p.parent)
        old_text = p.read_text(encoding="utf-8") if p.exists() else None
        new_text = text or ""
        if old_text == new_text:
            return
        create_backup(p, topic=topic)
        atomic_write_text(p, new_text)
        logger.debug("Saved content (%s chars) to %s", len(new_text), p)
    except OSError as e:
        logger.error("Failed to save content to %s: %s", p, e)


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
    p = get_geometry_path()
    if not p.exists():
        logger.debug("Geometry file does not exist: %s", p)
        return WindowGeometry()

    try:
        raw = p.read_text(encoding="utf-8")
        data = json.loads(raw) if raw.strip() else {}
        if not isinstance(data, dict):
            logger.warning("Invalid geometry data type in %s: %s", p, type(data))
            return WindowGeometry()
        geom = WindowGeometry.from_dict(data)
        logger.debug("Loaded geometry from %s: %s", p, geom)
        return geom
    except OSError as e:
        logger.error("Failed to read geometry file %s: %s", p, e)
        return WindowGeometry()
    except json.JSONDecodeError as e:
        logger.error("Invalid JSON in geometry file %s: %s", p, e)
        return WindowGeometry()


def save_window_geometry(geom: WindowGeometry) -> None:
    p = get_geometry_path()
    try:
        atomic_write_json(p, geom.to_dict())
        logger.debug("Saved geometry to %s: %s", p, geom)
    except OSError as e:
        logger.error("Failed to save geometry to %s: %s", p, e)

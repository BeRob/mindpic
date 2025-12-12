# File: mindpic/colorize.py
# -*- coding: utf-8 -*-
"""
MindPic – Einfärben / Tagging von Einträgen.

Hinweis:
- Tkinter Text-Widget Tags werden im UI gesetzt.
- Dieses Modul liefert nur Logik: welche Zeilen/Blöcke sind "Timestamp-Start".
"""

from __future__ import annotations

import re
from typing import Iterable


# Typische Timestamp-Formate (du kannst das erweitern)
# Beispiel: "2025-12-12 18:44" oder "12.12.2025 18:44" oder "18:44"
_TS_PATTERNS = [
    r"^\s*\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}(\:\d{2})?\s*",
    r"^\s*\d{2}\.\d{2}\.\d{4}\s+\d{2}:\d{2}(\:\d{2})?\s*",
    r"^\s*\d{2}:\d{2}(\:\d{2})?\s*",
]
_TS_RE = re.compile("|".join(f"(?:{p})" for p in _TS_PATTERNS))


def is_timestamp_line(line: str) -> bool:
    """True, wenn Zeile wie ein neuer Eintrag/Blockanfang aussieht."""
    return bool(_TS_RE.match(line or ""))


def iter_blocks(lines: Iterable[str]) -> list[tuple[int, int]]:
    """
    Erkennt Blöcke: Start bei Timestamp-Zeile, Ende vor nächstem Timestamp oder EOF.
    Gibt Liste von (start_index, end_index) zurück + end_index
    """
    lines = list(lines)
    starts: list[int] = [i for i, ln in enumerate(lines) if is_timestamp_line(ln)]

    if not starts:
        return [(0, len(lines))] if lines else []

    blocks: list[tuple[int, int]] = []
    for idx, s in enumerate(starts):
        e = starts[idx + 1] if idx + 1 < len(starts) else len(lines)
        blocks.append((s, e))
    return blocks


def pick_color_index(block_index: int, color_count: int) -> int:
    """Deterministisch zyklisch."""
    if color_count <= 0:
        return 0
    return block_index % color_count

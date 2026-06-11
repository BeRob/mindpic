# File: mindpic/note_store.py
# -*- coding: utf-8 -*-
"""MindPic – topic/note helpers for tabbed note files."""

from __future__ import annotations

import re
from pathlib import Path

from . import settings
from .paths import ensure_dir, get_notes_dir

_SAFE_RE = re.compile(r"[^A-Za-z0-9._ -]+")


def normalize_topic_name(name: str) -> str:
    """Return a display-safe topic name, falling back to the default topic."""
    cleaned = " ".join((name or "").strip().split())
    return cleaned or settings.DEFAULT_ACTIVE_TOPIC


def unique_topic_name(name: str, existing: list[str]) -> str:
    base = normalize_topic_name(name)
    if base not in existing:
        return base
    i = 2
    while f"{base} {i}" in existing:
        i += 1
    return f"{base} {i}"


def topic_to_filename(topic: str) -> str:
    """Map a topic name to a stable, readable text filename."""
    cleaned = normalize_topic_name(topic).replace(" ", "_")
    cleaned = _SAFE_RE.sub("_", cleaned).strip("._ ")
    return f"{cleaned or 'Allgemein'}.txt"


def get_topic_path(topic: str) -> Path:
    return (get_notes_dir() / topic_to_filename(topic)).resolve()


def ensure_topics(topics: list[str] | None) -> list[str]:
    """Normalize, deduplicate and ensure at least one topic exists."""
    result: list[str] = []
    for raw in topics or []:
        name = normalize_topic_name(str(raw))
        if name not in result:
            result.append(name)
    if not result:
        result = list(settings.DEFAULT_TOPICS)
    if settings.DEFAULT_ACTIVE_TOPIC not in result:
        result.insert(0, settings.DEFAULT_ACTIVE_TOPIC)
    ensure_dir(get_notes_dir())
    return result

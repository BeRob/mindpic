# File: mindpic/config_io.py
# -*- coding: utf-8 -*-
"""
MindPic – Konfigurations laden/speichern (config.json).

- Robust gegen kaputte JSONs
- Merge mit DEFAULT_CONFIG (fehlende Keys werden ergänzt)
"""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from . import settings
from .paths import ensure_dir, get_config_path


def _deep_merge(base: dict, overlay: dict) -> dict:
   
    result = deepcopy(base)
    for k, v in (overlay or {}).items():
        if isinstance(v, dict) and isinstance(result.get(k), dict):
            result[k] = _deep_merge(result[k], v)
        else:
            result[k] = v
    return result


def load_config() -> dict[str, Any]:
    """
    Lädt config.json, merged mit DEFAULT_CONFIG.
    """
    cfg_path: Path = get_config_path()

    merged = deepcopy(settings.DEFAULT_CONFIG)

    if not cfg_path.exists():
        return merged

    try:
        raw = cfg_path.read_text(encoding="utf-8")
        data = json.loads(raw) if raw.strip() else {}
        if not isinstance(data, dict):
            return merged
        merged = _deep_merge(merged, data)
        return merged
    except Exception:
        # Wenn JSON kaputt ist: Defaults nutzen
        return merged


def save_config(config: dict[str, Any]) -> None:
    """
    Speichert config.json pretty-printed.
    """
    cfg_path: Path = get_config_path()
    ensure_dir(cfg_path.parent)

    # Nur Dinge speichern, die in DEFAULT_CONFIG existieren
    out: dict[str, Any] = {}
    for k in settings.DEFAULT_CONFIG.keys():
        if k in config:
            out[k] = config[k]

    cfg_path.write_text(
        json.dumps(out, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )

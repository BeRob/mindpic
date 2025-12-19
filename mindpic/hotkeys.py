# File: mindpic/hotkeys.py
# -*- coding: utf-8 -*-
"""
MindPic – Global Hotkeys (optional via 'keyboard').

- Wenn das Modul 'keyboard' fehlt oder keine Rechte hat, wird global hotkey still deaktiviert.
- UI kann immer noch LOCAL_TOGGLE_KEY via Tk-.bind nutzen.
"""

from __future__ import annotations

import logging
from typing import Callable, Optional

from . import settings

logger = logging.getLogger(__name__)


class HotkeyManager:
    def __init__(self) -> None:
        self._keyboard = _try_import_keyboard()
        self._registered: list[int] = []

    @property
    def available(self) -> bool:
        return bool(self._keyboard) and settings.ENABLE_GLOBAL_HOTKEYS

    def register_global_hotkey(self, hotkey: str, callback: Callable[[], None]) -> bool:
        """
        Registriert einen systemweiten Hotkey.
        Rückgabe: True wenn aktiv, sonst False.
        """
        if not self.available:
            logger.debug("Global hotkeys not available (disabled or keyboard module missing)")
            return False

        hotkey = (hotkey or "").strip()
        if not hotkey:
            logger.warning("Empty hotkey string provided")
            return False

        try:
            handle = self._keyboard.add_hotkey(hotkey, callback)
            # keyboard.add_hotkey gibt je nach Version int/str/obj zurück
            if isinstance(handle, int):
                self._registered.append(handle)
            logger.info(f"Registered global hotkey: {hotkey}")
            return True
        except Exception as e:
            logger.error(f"Failed to register hotkey '{hotkey}': {e}")
            return False

    def unregister_all(self) -> None:
        if not self._keyboard:
            return
        try:
            # Entfernt ALLE Hotkeys, die keyboard kennt (robust)
            self._keyboard.clear_all_hotkeys()
            logger.debug("All hotkeys unregistered")
        except Exception as e:
            logger.error(f"Failed to unregister hotkeys: {e}")
        self._registered.clear()


def _try_import_keyboard():
    """
    keyboard ist optional:
    - kann unter Windows ohne Admin funktionieren, aber nicht immer (Hooks / Security-Policies).
    """
    try:
        import keyboard  # type: ignore
        logger.debug("keyboard module imported successfully")
        return keyboard
    except ImportError:
        logger.info("keyboard module not available (not installed)")
        return None
    except Exception as e:
        logger.warning(f"Failed to import keyboard module: {e}")
        return None

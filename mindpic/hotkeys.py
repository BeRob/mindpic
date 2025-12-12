# File: mindpic/hotkeys.py
# -*- coding: utf-8 -*-
"""
MindPic – Global Hotkeys (optional via 'keyboard').

- Wenn das Modul 'keyboard' fehlt oder keine Rechte hat, wird global hotkey still deaktiviert.
- UI kann immer noch LOCAL_TOGGLE_KEY via Tk-.bind nutzen.
"""

from __future__ import annotations

from typing import Callable, Optional

# =============================================================================
# USER OPTION (optional hier überschreiben)
# =============================================================================
ENABLE_GLOBAL_HOTKEYS: bool = True  # global hotkeys testweise abschalten


class HotkeyManager:
    def __init__(self) -> None:
        self._keyboard = _try_import_keyboard()
        self._registered: list[int] = []

    @property
    def available(self) -> bool:
        return bool(self._keyboard) and ENABLE_GLOBAL_HOTKEYS

    def register_global_hotkey(self, hotkey: str, callback: Callable[[], None]) -> bool:
        """
        Registriert einen systemweiten Hotkey.
        Rückgabe: True wenn aktiv, sonst False.
        """
        if not self.available:
            return False

        hotkey = (hotkey or "").strip()
        if not hotkey:
            return False

        try:
            handle = self._keyboard.add_hotkey(hotkey, callback)
            # keyboard.add_hotkey gibt je nach Version int/str/obj zurück
            if isinstance(handle, int):
                self._registered.append(handle)
            return True
        except Exception:
            return False

    def unregister_all(self) -> None:
        if not self._keyboard:
            return
        try:
            # Entfernt ALLE Hotkeys, die keyboard kennt (robust)
            self._keyboard.clear_all_hotkeys()
        except Exception:
            pass
        self._registered.clear()


def _try_import_keyboard():
    """
    keyboard ist optional:
    - kann unter Windows ohne Admin funktionieren, aber nicht immer (Hooks / Security-Policies).
    """
    try:
        import keyboard  # type: ignore
        return keyboard
    except Exception:
        return None

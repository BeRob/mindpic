# File: mindpic/tray.py
# -*- coding: utf-8 -*-
"""
MindPic – Tray Icon (optional via pystray + Pillow).

Dieses Modul ist absichtlich entkoppelt:
- Es kennt keine Tk-Widgets.
- Es ruft nur Callbacks auf, die du aus app.py übergibst.

Wenn pystray/Pillow fehlen oder blockiert sind, passiert einfach nichts.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import Callable, Optional

from .paths import get_tray_icon_path, get_manual_path


def _try_import_tray():
    try:
        import pystray  # type: ignore
        from PIL import Image  # type: ignore
        return pystray, Image
    except Exception:
        return None, None


@dataclass
class TrayCallbacks:
    # required
    toggle_visibility: Callable[[], None]
    quit_app: Callable[[], None]

    # optional features (werden nur angezeigt, wenn gesetzt)
    open_manual: Optional[Callable[[], None]] = None
    toggle_always_on_top: Optional[Callable[[], None]] = None
    toggle_borderless: Optional[Callable[[], None]] = None
    toggle_auto_hide: Optional[Callable[[], None]] = None

    # state getter (für Checkbox-Menüpunkte)
    get_always_on_top: Optional[Callable[[], bool]] = None
    get_borderless: Optional[Callable[[], bool]] = None
    get_auto_hide: Optional[Callable[[], bool]] = None


class TrayController:
    def __init__(self, callbacks: TrayCallbacks, tooltip: str = "MindPic") -> None:
        self.callbacks = callbacks
        self.tooltip = tooltip

        self._pystray, self._Image = _try_import_tray()
        self._icon = None
        self._thread: Optional[threading.Thread] = None

    @property
    def available(self) -> bool:
        return bool(self._pystray and self._Image)

    def start(self) -> bool:
        """Startet den Tray in einem Hintergrund-Thread. Rückgabe True wenn gestartet."""
        if not self.available:
            return False
        if self._thread and self._thread.is_alive():
            return True

        try:
            image = self._load_image_fallback()
            menu = self._build_menu()
            self._icon = self._pystray.Icon("mindpic", image, self.tooltip, menu)

            self._thread = threading.Thread(target=self._icon.run, daemon=True)
            self._thread.start()
            return True
        except Exception:
            self._icon = None
            self._thread = None
            return False

    def stop(self) -> None:
        """Stoppt den Tray (falls aktiv)."""
        try:
            if self._icon:
                self._icon.stop()
        except Exception:
            pass
        self._icon = None

    # -------------------------------------------------------------------------

    def _load_image_fallback(self):
        """
        Lädt PNG aus assets, fallback: 64x64 leeres Bild.
        """
        try:
            p = get_tray_icon_path()
            return self._Image.open(p)
        except Exception:
            try:
                return self._Image.new("RGBA", (64, 64), (0, 0, 0, 0))
            except Exception:
                # super fallback
                return None

    def _build_menu(self):
        """
        Erzeugt pystray.Menu mit optionalen Checkbox-Items.
        """
        MenuItem = self._pystray.MenuItem
        Menu = self._pystray.Menu

        items = []

        items.append(MenuItem("Show / Hide", lambda _icon, _item: self.callbacks.toggle_visibility()))

        # Optional: Manual
        if self.callbacks.open_manual:
            items.append(MenuItem("Open Manual", lambda _i, _it: self.callbacks.open_manual()))

        # Optional: toggles
        if self.callbacks.toggle_always_on_top:
            items.append(
                MenuItem(
                    "Always on Top",
                    lambda _i, _it: self.callbacks.toggle_always_on_top(),
                    checked=(lambda _i: bool(self.callbacks.get_always_on_top() if self.callbacks.get_always_on_top else False)),
                )
            )

        if self.callbacks.toggle_borderless:
            items.append(
                MenuItem(
                    "Borderless",
                    lambda _i, _it: self.callbacks.toggle_borderless(),
                    checked=(lambda _i: bool(self.callbacks.get_borderless() if self.callbacks.get_borderless else False)),
                )
            )

        if self.callbacks.toggle_auto_hide:
            items.append(
                MenuItem(
                    "Auto-hide on focus lost",
                    lambda _i, _it: self.callbacks.toggle_auto_hide(),
                    checked=(lambda _i: bool(self.callbacks.get_auto_hide() if self.callbacks.get_auto_hide else False)),
                )
            )

        items.append(MenuItem("Quit", lambda _icon, _item: self.callbacks.quit_app()))

        return Menu(*items)


# Convenience helper (wenn du keinen Controller managen willst)
def start_tray(callbacks: TrayCallbacks, tooltip: str = "MindPic") -> TrayController:
    ctl = TrayController(callbacks, tooltip=tooltip)
    ctl.start()
    return ctl

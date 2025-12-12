# File: mindpic/app.py
# -*- coding: utf-8 -*-
"""
MindPic – App-Orchestrator (State + Zusammenspiel der Module)

Dieses Modul:
- lädt Config + Content
- baut UI
- kümmert sich um Save/Autosave, Fensterzustand, Auto-Hide, Snap, Hotkeys, Tray

Hinweis: User-Editierbares gehört in settings.py (und optional die USER OPTIONS hier).
"""

from __future__ import annotations

import os
import sys
import time
import webbrowser
from dataclasses import asdict
from pathlib import Path
from typing import Optional

import tkinter as tk

from . import settings
from .config_io import load_config, save_config
from .persistence import load_content, save_content, load_window_geometry, save_window_geometry, WindowGeometry
from .paths import get_log_path, get_manual_path
from .colorize import iter_blocks, pick_color_index
from .hotkeys import HotkeyManager
from .tray import TrayCallbacks, TrayController
from . import ui as ui_mod


# =============================================================================
# USER OPTIONS (optional – defaults in settings.py)
# =============================================================================
ENABLE_SNAP: bool = True


class MindPicApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root

        # --- runtime state
        self.config = load_config()
        self._visible = True
        self._last_user_edit_ts = 0.0
        self._autosave_job: Optional[str] = None
        self._autohide_job: Optional[str] = None

        # helpers
        self._dragger = ui_mod.BorderlessDragger()
        self._hotkeys = HotkeyManager()
        self._tray = None  # type: Optional[TrayController]

        # --- basic window
        self.root.title(settings.APP_NAME)
        self.root.minsize(
            int(self.config.get("min_width", settings.DEFAULT_MIN_WIDTH)),
            int(self.config.get("min_height", settings.DEFAULT_MIN_HEIGHT)),
        )

        # icon + styles + widgets
        ui_mod.setup_styles(self.root, self.config)
        self._icon_ref = ui_mod.apply_app_icon(self.root)
        self.ui = ui_mod.create_widgets(self.root, self.config, on_save_clicked=self.save_all)

        ui_mod.apply_colors(self.ui, self.config)
        ui_mod.apply_font(self.ui, self.config)

        # window attributes
        self._apply_alpha(float(self.config.get("window_alpha", settings.DEFAULT_WINDOW_ALPHA)))
        self._apply_topmost(bool(self.config.get("always_on_top", settings.DEFAULT_ALWAYS_ON_TOP)))

        # geometry restore
        self._restore_geometry()

        # borderless (must be after geometry restore)
        ui_mod.apply_borderless(
            self.root,
            enabled=bool(self.config.get("borderless", False)),
            dragger=self._dragger,
        )

        # load content into Text
        self.ui.text.insert("1.0", load_content())
        self._recolorize()

        # binds
        self.ui.text.bind("<<Modified>>", self._on_text_modified)
        self.ui.text.bind("<KeyRelease>", lambda _e: self._recolorize_debounced())
        self.root.bind(settings.LOCAL_TOGGLE_KEY, lambda _e: self.toggle_visibility())

        self.root.bind("<FocusOut>", self._on_focus_out)
        self.root.bind("<FocusIn>", self._on_focus_in)
        self.root.bind("<Configure>", self._on_configure)

        # context menu
        ui_mod.create_context_menu(
            root=self.root,
            ui=self.ui,
            config=self.config,
            callbacks=ui_mod.MenuCallbacks(
                toggle_visibility=self.toggle_visibility,
                toggle_topmost=self.toggle_topmost,
                toggle_borderless=self._menu_set_borderless,
                toggle_autohide=self._menu_set_autohide,
                set_alpha=self._menu_set_alpha,
                change_text_color=self._menu_set_text_color,
                change_background_color=self._menu_set_bg_color,
                change_note_color=self._menu_set_note_color,
                set_font=self._menu_set_font,
                open_manual=self.open_manual,
                quit_app=self.quit_app,
            ),
        )

        # tray
        if settings.ENABLE_TRAY:
            self._start_tray()

        # global hotkey (optional)
        self._hotkeys.register_global_hotkey(
            settings.GLOBAL_TOGGLE_HOTKEY,
            lambda: self._call_on_ui_thread(self.toggle_visibility),
        )

        # autosave timer
        self._schedule_autosave()

        # window close
        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)

    # -------------------------------------------------------------------------
    # Public actions
    # -------------------------------------------------------------------------

    def toggle_visibility(self) -> None:
        if self._visible:
            self.root.withdraw()
            self._visible = False
        else:
            self.root.deiconify()
            self.root.lift()
            try:
                self.root.focus_force()
            except Exception:
                pass
            self._visible = True

    def toggle_topmost(self) -> None:
        new_val = not bool(self.config.get("always_on_top", settings.DEFAULT_ALWAYS_ON_TOP))
        self.config["always_on_top"] = new_val
        self._apply_topmost(new_val)
        save_config(self.config)

    def save_all(self) -> None:
        # content
        text = self.ui.text.get("1.0", "end-1c")
        save_content(text)

        # config + geometry
        save_config(self.config)
        self._save_geometry()

        # recolorize (keeps things consistent)
        self._recolorize()

    def open_manual(self) -> None:
        p = get_manual_path()
        if not p.exists():
            return

        # Windows: os.startfile; fallback: browser
        try:
            if sys.platform.startswith("win"):
                os.startfile(str(p))  # type: ignore[attr-defined]
                return
        except Exception:
            pass

        try:
            webbrowser.open(p.as_uri())
        except Exception:
            pass

    def quit_app(self) -> None:
        # save before exit
        try:
            self.save_all()
        except Exception:
            pass

        # stop tray + hotkeys
        try:
            if self._tray:
                self._tray.stop()
        except Exception:
            pass
        try:
            self._hotkeys.unregister_all()
        except Exception:
            pass

        try:
            self.root.destroy()
        except Exception:
            pass

    # -------------------------------------------------------------------------
    # Menu callbacks (set values + apply)
    # -------------------------------------------------------------------------

    def _menu_set_alpha(self, value: float) -> None:
        value = float(value)
        self.config["window_alpha"] = value
        self._apply_alpha(value)
        save_config(self.config)

    def _menu_set_autohide(self, enabled: bool) -> None:
        self.config["auto_hide_on_focus"] = bool(enabled)
        save_config(self.config)

    def _menu_set_borderless(self, enabled: bool) -> None:
        self.config["borderless"] = bool(enabled)
        ui_mod.apply_borderless(self.root, enabled=bool(enabled), dragger=self._dragger)
        save_config(self.config)

    def _menu_set_text_color(self, color: str) -> None:
        self.config["text_fg"] = str(color)
        ui_mod.apply_colors(self.ui, self.config)
        save_config(self.config)

    def _menu_set_bg_color(self, color: str) -> None:
        self.config["text_bg"] = str(color)
        ui_mod.setup_styles(self.root, self.config)
        ui_mod.apply_colors(self.ui, self.config)
        save_config(self.config)

    def _menu_set_note_color(self, idx: int, color: str) -> None:
        colors = list(self.config.get("note_colors", []))
        if 0 <= idx < len(colors):
            colors[idx] = str(color)
            self.config["note_colors"] = colors
            ui_mod.apply_colors(self.ui, self.config)
            self._recolorize()
            save_config(self.config)

    def _menu_set_font(self, family: str, size: int) -> None:
        self.config["font_family"] = str(family)
        self.config["font_size"] = int(size)
        ui_mod.apply_font(self.ui, self.config)
        ui_mod.update_font_menu_label(self.ui, self.config)
        save_config(self.config)

    # -------------------------------------------------------------------------
    # Internal: attributes / geometry
    # -------------------------------------------------------------------------

    def _apply_alpha(self, alpha: float) -> None:
        # clamp
        if alpha < 0.2:
            alpha = 0.2
        if alpha > 1.0:
            alpha = 1.0
        try:
            self.root.attributes("-alpha", alpha)
        except Exception:
            pass

    def _apply_topmost(self, enabled: bool) -> None:
        try:
            self.root.attributes("-topmost", bool(enabled))
        except Exception:
            pass

    def _restore_geometry(self) -> None:
        geom = load_window_geometry()
        if geom.width and geom.height:
            w, h = int(geom.width), int(geom.height)
            if geom.x is not None and geom.y is not None:
                self.root.geometry(f"{w}x{h}+{int(geom.x)}+{int(geom.y)}")
            else:
                self.root.geometry(f"{w}x{h}")
        else:
            # fallback size (minsize is already set)
            self.root.geometry("520x320")

    def _save_geometry(self) -> None:
        try:
            g = WindowGeometry(
                width=self.root.winfo_width(),
                height=self.root.winfo_height(),
                x=self.root.winfo_x(),
                y=self.root.winfo_y(),
            )
            save_window_geometry(g)
        except Exception:
            pass

    # -------------------------------------------------------------------------
    # Internal: recolorize blocks
    # -------------------------------------------------------------------------

    def _recolorize_debounced(self) -> None:
        # debounce via after
        try:
            self.root.after_cancel(getattr(self, "_recolor_job", ""))
        except Exception:
            pass
        self._recolor_job = self.root.after(180, self._recolorize)

    def _recolorize(self) -> None:
        """
        Wendet noteX Tags blockweise an (für Hintergründe).
        """
        note_colors = list(self.config.get("note_colors", []))
        if not note_colors:
            return

        # remove tags first
        for i in range(len(note_colors)):
            self.ui.text.tag_remove(f"note{i}", "1.0", "end")

        text = self.ui.text.get("1.0", "end-1c")
        lines = text.splitlines(True)  # keep line endings
        blocks = iter_blocks(lines)

        # convert line index to tk index
        # Tk lines are 1-based, columns 0-based.
        for b_idx, (start, end) in enumerate(blocks):
            color_idx = pick_color_index(b_idx, len(note_colors))
            tag = f"note{color_idx}"

            start_line = start + 1
            end_line = end + 1

            # start at line start, end at line start of next block
            start_idx = f"{start_line}.0"
            end_idx = f"{end_line}.0"
            try:
                self.ui.text.tag_add(tag, start_idx, end_idx)
            except Exception:
                pass

    # -------------------------------------------------------------------------
    # Internal: events
    # -------------------------------------------------------------------------

    def _on_text_modified(self, _event=None) -> None:
        # Reset Tk modified flag immediately (sonst feuert es dauernd)
        try:
            self.ui.text.edit_modified(False)
        except Exception:
            pass
        self._last_user_edit_ts = time.time()

    def _on_focus_out(self, _event=None) -> None:
        if not bool(self.config.get("auto_hide_on_focus", False)):
            return
        # schedule hide after delay
        self._cancel_autohide()
        self._autohide_job = self.root.after(settings.AUTO_HIDE_DELAY_MS, self._autohide_now)

    def _on_focus_in(self, _event=None) -> None:
        self._cancel_autohide()

    def _cancel_autohide(self) -> None:
        if self._autohide_job:
            try:
                self.root.after_cancel(self._autohide_job)
            except Exception:
                pass
            self._autohide_job = None

    def _autohide_now(self) -> None:
        self._autohide_job = None
        if self._visible:
            self.toggle_visibility()

    def _on_configure(self, _event=None) -> None:
        # snap only while visible and not minimized
        if not ENABLE_SNAP:
            return
        if not self._visible:
            return
        try:
            # ignore tiny configure storms during withdraw/deiconify
            if self.root.state() == "iconic":
                return
        except Exception:
            pass
        self._snap_to_edges()

    def _snap_to_edges(self) -> None:
        """
        Snap an Bildschirmränder (links/rechts/oben/unten) innerhalb snap_distance.
        """
        try:
            snap = int(self.config.get("snap_distance", settings.DEFAULT_SNAP_DISTANCE))
            if snap <= 0:
                return

            sw = self.root.winfo_screenwidth()
            sh = self.root.winfo_screenheight()

            w = self.root.winfo_width()
            h = self.root.winfo_height()
            x = self.root.winfo_x()
            y = self.root.winfo_y()

            nx, ny = x, y

            # left / right
            if abs(x - 0) <= snap:
                nx = 0
            if abs((x + w) - sw) <= snap:
                nx = sw - w

            # top / bottom
            if abs(y - 0) <= snap:
                ny = 0
            if abs((y + h) - sh) <= snap:
                ny = sh - h

            if (nx, ny) != (x, y):
                self.root.geometry(f"+{nx}+{ny}")
        except Exception:
            pass

    # -------------------------------------------------------------------------
    # Autosave
    # -------------------------------------------------------------------------

    def _schedule_autosave(self) -> None:
        if self._autosave_job:
            try:
                self.root.after_cancel(self._autosave_job)
            except Exception:
                pass

        self._autosave_job = self.root.after(settings.AUTOSAVE_INTERVAL_MS, self._autosave_tick)

    def _autosave_tick(self) -> None:
        self._autosave_job = None

        # Nur speichern wenn kürzlich editiert wurde (reduziert unnötige Writes)
        if self._last_user_edit_ts and (time.time() - self._last_user_edit_ts) < 5.0:
            try:
                self.save_all()
            except Exception:
                pass

        self._schedule_autosave()

    # -------------------------------------------------------------------------
    # Tray
    # -------------------------------------------------------------------------

    def _start_tray(self) -> None:
        cb = TrayCallbacks(
            toggle_visibility=lambda: self._call_on_ui_thread(self.toggle_visibility),
            quit_app=lambda: self._call_on_ui_thread(self.quit_app),
            open_manual=lambda: self._call_on_ui_thread(self.open_manual),
            toggle_always_on_top=lambda: self._call_on_ui_thread(self.toggle_topmost),
            toggle_borderless=lambda: self._call_on_ui_thread(lambda: self._menu_set_borderless(not bool(self.config.get("borderless", False)))),
            toggle_auto_hide=lambda: self._call_on_ui_thread(lambda: self._menu_set_autohide(not bool(self.config.get("auto_hide_on_focus", False)))),
            get_always_on_top=lambda: bool(self.config.get("always_on_top", False)),
            get_borderless=lambda: bool(self.config.get("borderless", False)),
            get_auto_hide=lambda: bool(self.config.get("auto_hide_on_focus", False)),
        )
        self._tray = TrayController(cb, tooltip=settings.APP_NAME)
        self._tray.start()

    def _call_on_ui_thread(self, fn) -> None:
        try:
            self.root.after(0, fn)
        except Exception:
            pass

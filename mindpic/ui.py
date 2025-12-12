# File: mindpic/ui.py
# -*- coding: utf-8 -*-
"""
MindPic – UI-Bausteine (Tkinter/ttk)

Dieses Modul:
- baut Widgets
- setzt Styles
- liefert Kontextmenü + Dialoge
- verwaltet Borderless-Drag (ohne App-Logik)

App-Logik (Speichern, Tray, Hotkeys, Persistenz) kommt in app.py.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

import tkinter as tk
from tkinter import ttk, colorchooser
import tkinter.font as tkfont

from .paths import get_app_icon_path


# =============================================================================
# USER OPTIONS (hier kannst du UI-Details anpassen)
# =============================================================================

THEME_NAME: str = "clam"  # "clam" funktioniert i.d.R. gut für Dark-Styles

ALPHA_PRESETS: list[tuple[float, str]] = [
    (0.50, "50%"),
    (0.70, "70%"),
    (0.85, "85%"),
    (0.95, "95%"),
    (1.00, "100%"),
]

BUTTON_PAD_XY: tuple[int, int] = (8, 2)   # padding=(x,y) für Toolbar-Button
MAIN_PADDING: tuple[int, int, int, int] = (6, 6, 6, 4)  # l,t,r,b


# =============================================================================
# Data structures
# =============================================================================

@dataclass
class UIRefs:
    main_frame: ttk.Frame
    text: tk.Text
    scrollbar: ttk.Scrollbar
    save_button: ttk.Button

    # context menu
    menu: tk.Menu | None = None
    colors_menu: tk.Menu | None = None
    font_menu: tk.Menu | None = None
    alpha_menu: tk.Menu | None = None

    # state vars for menu indicators
    alpha_var: tk.DoubleVar | None = None
    autohide_var: tk.BooleanVar | None = None
    borderless_var: tk.BooleanVar | None = None

    # keep references alive
    _app_icon_image: tk.PhotoImage | None = None


# =============================================================================
# Styles / Icons
# =============================================================================

def setup_styles(root: tk.Tk, config: dict) -> ttk.Style:
    """
    ttk-Styles für Buttons, Frames, Scrollbar.
    """
    style = ttk.Style(root)
    try:
        style.theme_use(THEME_NAME)
    except tk.TclError:
        pass

    bg = str(config.get("text_bg", "#111111"))
    fg = str(config.get("text_fg", "#ffffff"))

    root.configure(bg=bg)

    style.configure("TFrame", background=bg)
    style.configure("Toolbar.TFrame", background=bg)

    style.configure(
        "Toolbar.TButton",
        background=bg,
        foreground=fg,
        padding=BUTTON_PAD_XY,
        borderwidth=0,
        focusthickness=0,
    )
    style.map(
        "Toolbar.TButton",
        background=[
            ("pressed", "#333333"),
            ("active", "#222222"),
        ],
    )

    style.configure(
        "Custom.Vertical.TScrollbar",
        gripcount=0,
        background="#333333",
        troughcolor=bg,
        bordercolor=bg,
        arrowcolor="#888888",
        relief="flat",
    )
    style.map(
        "Custom.Vertical.TScrollbar",
        background=[
            ("pressed", "#555555"),
            ("active", "#444444"),
        ],
    )

    return style


def apply_app_icon(root: tk.Tk) -> tk.PhotoImage | None:
    """
    Setzt Fenster-Icon. Gibt PhotoImage zurück, damit Referenz gehalten werden kann.
    """
    p = get_app_icon_path()
    try:
        if p.suffix.lower() == ".ico":
            try:
                root.iconbitmap(p)
                return None
            except Exception:
                # falls iconbitmap scheitert, versuchen wir iconphoto
                pass

        img = tk.PhotoImage(file=str(p))
        root.iconphoto(True, img)
        return img
    except Exception:
        return None


# =============================================================================
# Widget creation / appearance
# =============================================================================

def create_widgets(root: tk.Tk, config: dict, on_save_clicked: Callable[[], None]) -> UIRefs:
    """
    Baut das Hauptlayout:
    - Text (mit Scrollbar)
    - unten rechts ein "Save"-Button
    """
    main_frame = ttk.Frame(root, padding=MAIN_PADDING, style="TFrame")
    main_frame.pack(fill="both", expand=True)

    text_container = ttk.Frame(main_frame, style="TFrame")
    text_container.pack(side="top", fill="both", expand=True)

    text = tk.Text(
        text_container,
        wrap="word",
        undo=True,
        height=10,
        bd=0,
        highlightthickness=0,
    )
    text.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(
        text_container,
        orient="vertical",
        command=text.yview,
        style="Custom.Vertical.TScrollbar",
    )
    scrollbar.pack(side="right", fill="y")
    text.configure(yscrollcommand=scrollbar.set)

    button_frame = ttk.Frame(main_frame, style="Toolbar.TFrame")
    button_frame.pack(side="bottom", fill="x", pady=(6, 0))

    save_button = ttk.Button(
        button_frame,
        text="Save",
        command=on_save_clicked,
        style="Toolbar.TButton",
    )
    save_button.pack(side="right")

    ui = UIRefs(
        main_frame=main_frame,
        text=text,
        scrollbar=scrollbar,
        save_button=save_button,
    )
    return ui


def apply_colors(ui: UIRefs, config: dict) -> None:
    """
    Farben aus Config auf Textfeld + Tags anwenden.
    Erwartet config keys: text_fg, text_bg, note_colors (list).
    """
    fg = str(config.get("text_fg", "#ffffff"))
    bg = str(config.get("text_bg", "#111111"))
    note_colors = list(config.get("note_colors", []))

    ui.text.configure(
        fg=fg,
        bg=bg,
        insertbackground=fg,
    )
    for i, color in enumerate(note_colors):
        ui.text.tag_configure(f"note{i}", background=str(color))


def apply_font(ui: UIRefs, config: dict) -> None:
    fam = str(config.get("font_family", "Segoe UI"))
    size = int(config.get("font_size", 10))
    ui.text.configure(font=(fam, size))


# =============================================================================
# Borderless drag helper
# =============================================================================

class BorderlessDragger:
    def __init__(self) -> None:
        self._drag_x = 0
        self._drag_y = 0

    def start_move(self, root: tk.Tk, event: tk.Event) -> None:
        self._drag_x = int(getattr(event, "x", 0))
        self._drag_y = int(getattr(event, "y", 0))

    def on_move(self, root: tk.Tk, event: tk.Event) -> None:
        x = int(getattr(event, "x_root", 0)) - self._drag_x
        y = int(getattr(event, "y_root", 0)) - self._drag_y
        root.geometry(f"+{x}+{y}")


def apply_borderless(root: tk.Tk, enabled: bool, dragger: BorderlessDragger) -> None:
    """
    Borderless (overrideredirect) anwenden, und Drag-Binds setzen/entfernen.
    """
    geom = root.winfo_geometry()
    root.overrideredirect(bool(enabled))
    root.geometry(geom)

    if enabled:
        root.bind("<ButtonPress-1>", lambda e: dragger.start_move(root, e))
        root.bind("<B1-Motion>", lambda e: dragger.on_move(root, e))
    else:
        root.unbind("<ButtonPress-1>")
        root.unbind("<B1-Motion>")


# =============================================================================
# Context menu + dialogs
# =============================================================================

@dataclass
class MenuCallbacks:
    # toggles/actions (App kümmert sich um Config + Save)
    toggle_visibility: Callable[[], None]
    toggle_topmost: Callable[[], None]
    toggle_borderless: Callable[[bool], None]  # bekommt neuen State
    toggle_autohide: Callable[[bool], None]    # bekommt neuen State
    set_alpha: Callable[[float], None]

    change_text_color: Callable[[str], None]       # new hex color
    change_background_color: Callable[[str], None] # new hex color
    change_note_color: Callable[[int, str], None]  # idx + color

    set_font: Callable[[str, int], None]           # family, size

    open_manual: Callable[[], None]
    quit_app: Callable[[], None]


def create_context_menu(
    root: tk.Tk,
    ui: UIRefs,
    config: dict,
    callbacks: MenuCallbacks,
) -> None:
    """
    Erstellt Kontextmenü inkl. Submenüs + Indikatoren und bindet Rechtsklick.
    Speichert Referenzen in ui.*.
    """
    menu = tk.Menu(root, tearoff=0)

    # State Vars (werden von app.py initialisiert/gespiegelt)
    ui.alpha_var = tk.DoubleVar(value=float(config.get("window_alpha", 1.0)))
    ui.autohide_var = tk.BooleanVar(value=bool(config.get("auto_hide_on_focus", False)))
    ui.borderless_var = tk.BooleanVar(value=bool(config.get("borderless", False)))

    # Farben
    colors_menu = tk.Menu(menu, tearoff=0)
    colors_menu.add_command(
        label="Textfarbe…",
        command=lambda: _pick_color_and_call(
            initial=str(config.get("text_fg", "#ffffff")),
            title="Textfarbe wählen",
            on_color=callbacks.change_text_color,
        ),
    )
    colors_menu.add_command(
        label="Hintergrund…",
        command=lambda: _pick_color_and_call(
            initial=str(config.get("text_bg", "#111111")),
            title="Hintergrundfarbe wählen",
            on_color=callbacks.change_background_color,
        ),
    )
    note_colors = list(config.get("note_colors", []))
    for idx in range(len(note_colors)):
        colors_menu.add_command(
            label=f"Eintragsfarbe {idx+1}…",
            command=lambda i=idx: _pick_color_and_call(
                initial=str(note_colors[i]),
                title=f"Eintragsfarbe {i+1} wählen",
                on_color=lambda c, i=i: callbacks.change_note_color(i, c),
            ),
        )
    menu.add_cascade(label="Farben", menu=colors_menu)

    # Schrift
    font_menu = tk.Menu(menu, tearoff=0)
    current_font_label = f"Aktuell: {config.get('font_family', '')} {config.get('font_size', '')}"
    font_menu.add_command(label=current_font_label, state="disabled")
    font_menu.add_separator()
    font_menu.add_command(
        label="Schrift wählen…",
        command=lambda: show_font_dialog(
            root=root,
            current_family=str(config.get("font_family", "Segoe UI")),
            current_size=int(config.get("font_size", 10)),
            on_ok=callbacks.set_font,
        ),
    )
    menu.add_cascade(label="Schrift", menu=font_menu)

    # Transparenz (Radiobuttons)
    alpha_menu = tk.Menu(menu, tearoff=0)
    for value, label in ALPHA_PRESETS:
        alpha_menu.add_radiobutton(
            label=label,
            value=float(value),
            variable=ui.alpha_var,
            command=lambda v=float(value): callbacks.set_alpha(v),
        )
    menu.add_cascade(label="Transparenz", menu=alpha_menu)

    # Toggles
    menu.add_checkbutton(
        label="Auto-Hide bei Fokusverlust",
        variable=ui.autohide_var,
        command=lambda: callbacks.toggle_autohide(bool(ui.autohide_var.get())),
    )
    menu.add_checkbutton(
        label="Randlos (Borderless)",
        variable=ui.borderless_var,
        command=lambda: callbacks.toggle_borderless(bool(ui.borderless_var.get())),
    )

    menu.add_command(label="Immer im Vordergrund umschalten", command=callbacks.toggle_topmost)
    menu.add_command(label="Fenster ein-/ausblenden", command=callbacks.toggle_visibility)

    # Manual / Quit
    menu.add_command(label="Handbuch öffnen", command=callbacks.open_manual)
    menu.add_separator()
    menu.add_command(label="Beenden", command=callbacks.quit_app)

    # Bind right click (Fenster UND Text)
    root.bind("<Button-3>", lambda e: _show_menu_safe(menu, e))
    ui.text.bind("<Button-3>", lambda e: _show_menu_safe(menu, e))

    ui.menu = menu
    ui.colors_menu = colors_menu
    ui.font_menu = font_menu
    ui.alpha_menu = alpha_menu


def update_font_menu_label(ui: UIRefs, config: dict) -> None:
    """
    Aktualisiert "Aktuell: ..." im Schrift-Untermenü.
    """
    if not ui.font_menu:
        return
    label = f"Aktuell: {config.get('font_family', '')} {config.get('font_size', '')}"
    try:
        ui.font_menu.entryconfig(0, label=label)  # 0 ist das disabled Label
    except Exception:
        pass


def show_font_dialog(
    root: tk.Tk,
    current_family: str,
    current_size: int,
    on_ok: Callable[[str, int], None],
) -> None:
    """
    Toplevel mit Combobox (Schriftart) + Spinbox (Größe).
    """
    win = tk.Toplevel(root)
    win.title("Schrift wählen")
    win.transient(root)
    win.grab_set()

    frm = ttk.Frame(win, padding=10)
    frm.pack(fill="both", expand=True)

    ttk.Label(frm, text="Schriftart:").grid(row=0, column=0, sticky="w")
    fonts = sorted(set(tkfont.families()))
    fam_var = tk.StringVar(value=current_family if current_family in fonts else (fonts[0] if fonts else "Segoe UI"))

    combo = ttk.Combobox(frm, values=fonts, textvariable=fam_var, state="readonly", width=30)
    combo.grid(row=0, column=1, sticky="ew", padx=(5, 0))

    ttk.Label(frm, text="Größe:").grid(row=1, column=0, sticky="w", pady=(8, 0))
    size_var = tk.IntVar(value=int(current_size) if current_size else 10)
    size_spin = tk.Spinbox(frm, from_=6, to=72, textvariable=size_var, width=5)
    size_spin.grid(row=1, column=1, sticky="w", padx=(5, 0), pady=(8, 0))

    btn_frame = ttk.Frame(frm)
    btn_frame.grid(row=2, column=0, columnspan=2, pady=(12, 0), sticky="e")

    def _ok() -> None:
        fam = fam_var.get() or current_family
        try:
            size = int(size_var.get())
        except Exception:
            size = int(current_size) if current_size else 10
        on_ok(fam, size)
        win.destroy()

    def _cancel() -> None:
        win.destroy()

    ttk.Button(btn_frame, text="Abbrechen", command=_cancel).pack(side="right", padx=(5, 0))
    ttk.Button(btn_frame, text="OK", command=_ok).pack(side="right")

    frm.columnconfigure(1, weight=1)


# =============================================================================
# Internal helpers
# =============================================================================

def _show_menu_safe(menu: tk.Menu, event: tk.Event) -> None:
    try:
        menu.tk_popup(int(event.x_root), int(event.y_root))
        menu.grab_release()
    except tk.TclError:
        pass


def _pick_color_and_call(initial: str, title: str, on_color: Callable[[str], None]) -> None:
    color = colorchooser.askcolor(initialcolor=initial, title=title)[1]
    if color:
        on_color(color)

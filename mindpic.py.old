#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
======================================================================
 Datei:             <desktop_todo.py>
 Projekt:           <Desktop Notiz App>
 
 Beschreibung:      <Desktop-ToDo mit:
                    - konfigurierbaren Pfaden, Schrift, Fenstergröße, Transparenz
                    - persistentem Text und Fenstergeometrie
                    - optionalem globalen Hotkey (keyboard-Modul)
                    - lokalem Hotkey
                    - Andocken an Bildschirmränder 
                    - Zeitstempel+Speichern-Button
                    - automatische Einfärbung je Eintrag (Block bis zum Speichern) BETA
                    - Tray-Symbol mit Menü (pystray + Pillow)
                    - Auto-Hide-Option bei Fokusverlust (im Fenster-Kontextmenü + im Tray-Menü)
                    - Laufzeit-Konfiguration über Kontextmenü:
                        - Textfarbe, Hintergrundfarbe, Eintragsfarben
                        - Schriftart und -größe (Dropdown/Combobox)
                        - Transparenz 
                        - Borderless 
                    >

 Autor:             <Robert Benner>
 Firma:             <Questalpha>
 Version:           <0.6>
 Erstellt am:       <28.11.2025>
 Zuletzt geändert:  <10.12.2025>

 Python-Version:    <3.14>
 Abhängigkeiten:
                    - keyboard==0.13.5
                    - pillow==12.0.0
                    - pystray==0.19.5
                    - six==1.17.0
                    in requierements.txt

 Hinweise:
     - <n/a>
======================================================================
"""

import os
import sys
import json
import threading
from pathlib import Path
from datetime import datetime

import tkinter as tk
from tkinter import ttk, colorchooser
import tkinter.font as tkfont

# Optional: globaler Hotkey
try:
    import keyboard
except ImportError:
    keyboard = None

# Optional: Tray-Icon
try:
    import pystray
    from PIL import Image, ImageDraw
except ImportError:
    pystray = None
    Image = None
    ImageDraw = None

def resource_path(relative: str) -> Path:
    """
    Liefert einen Pfad zu Ressourcen (Icons, Manual), der sowohl
    im normalen Python-Skript als auch in der PyInstaller-EXE funktioniert.
    """
    # Wenn PyInstaller-EXE: _MEIPASS verwenden
    base = getattr(sys, "_MEIPASS", Path(__file__).resolve().parent)
    return Path(base) / relative

# ===================== BASIS-KONFIGURATION =====================

APP_NAME = "MindPic"

# Pfade Icons
APP_ICON_PATH = r"D:\Coding\Projekte\DesktopToDo\icons\Untitled-3.ico"  # z.B. r"D:\Coding\Projekte\DesktopToDo\icons\favicon-32x32.png"
TRAY_ICON_PATH = r"D:\Coding\Projekte\DesktopToDo\icons\favicon-32x32.png"  # optional; wenn None -> wird APP_ICON_PATH fürs Tray benutzt
ICON_APP_REL = "assets/Untitled-3.ico"
ICON_TRAY_REL = "assets/favicon-32x32.png"
MANUAL_REL   = "assets/MindPic_Manual.pdf"

# Beispiel-Switch für Dev vs. EXE:
IS_FROZEN = getattr(sys, "frozen", False)
if IS_FROZEN:
    SAVE_DIR = None  # EXE: %APPDATA%\mindpic
else:
    SAVE_DIR = r"D:\Coding\Projekte\DesktopTodo\data"  # Dev-Pfad

# Eigener Speicherordner für Daten (todo.txt, window_geometry.txt, config.json)
# None = automatisch unter %APPDATA%\APP_NAME
# Beispiel: SAVE_DIR = r"D:\Coding\Projekte\DesktopTodo\data"
# SAVE_DIR = r"D:\Coding\Projekte\DesktopTodo\data"
# Dateinamen
TODO_FILENAME = "inhalt.txt"
GEOM_FILENAME = "window_config.txt"
CONFIG_FILENAME = "config.json"
# Globale Tastenkombination zum Ein-/Ausblenden (systemweit), None = aus
GLOBAL_TOGGLE_KEY = "f9"
# Lokaler Hotkey innerhalb des Fensters (Tk-Syntax), None = aus
LOCAL_TOGGLE_KEY = "<F9>"
# Start-Geometrie beim ersten Start
DEFAULT_GEOMETRY = "260x400+20+80"
# Standard-Minimalgröße
DEFAULT_MIN_WIDTH = 200
DEFAULT_MIN_HEIGHT = 150
# Standard-Transparenz
DEFAULT_WINDOW_ALPHA = 0.95
# Start-Einstellung: immer im Vordergrund?
DEFAULT_ALWAYS_ON_TOP = False
# Start-Einstellung: Randlos?
DEFAULT_BORDERLESS = False
# Standard-Snap-Abstand in Pixeln (Fenster „klebt“ an Bildschirmrändern)
DEFAULT_SNAP_DISTANCE = 30
# Auto-Hide bei Fokusverlust (Startzustand)
DEFAULT_AUTO_HIDE_ON_FOCUS_LOST = False
# Schrift-Defaults
DEFAULT_FONT_FAMILY = "Iosevka"
DEFAULT_FONT_SIZE = 9
# Farben
DEFAULT_TEXT_FG = "#ffffff"
DEFAULT_TEXT_BG = "#111111"
DEFAULT_NOTE_COLORS = [
    "#252a32",
    "#273038",
    "#28343c",
    "#26363a",
]
# Zeitstempel-Format für Eintrags-Ende (eigene Zeile)
TIMESTAMP_FORMAT = "[%d-%m-%Y %H:%M]"
# Default-Config-Objekt (wird mit config.json zusammengeführt)
DEFAULT_CONFIG = {
    "font_family": DEFAULT_FONT_FAMILY,
    "font_size": DEFAULT_FONT_SIZE,
    "window_alpha": DEFAULT_WINDOW_ALPHA,
    "always_on_top": DEFAULT_ALWAYS_ON_TOP,
    "borderless": DEFAULT_BORDERLESS,
    "min_width": DEFAULT_MIN_WIDTH,
    "min_height": DEFAULT_MIN_HEIGHT,
    "snap_distance": DEFAULT_SNAP_DISTANCE,
    "text_fg": DEFAULT_TEXT_FG,
    "text_bg": DEFAULT_TEXT_BG,
    "note_colors": DEFAULT_NOTE_COLORS,
    "auto_hide_on_focus": DEFAULT_AUTO_HIDE_ON_FOCUS_LOST,
}

# ============================================================================

def get_base_dir() -> Path:
    """Ermittle den Basis-Speicherordner für Daten."""
    if SAVE_DIR:
        base = Path(SAVE_DIR)
    else:
        appdata = os.getenv("APPDATA")
        if appdata:
            base = Path(appdata) / APP_NAME
        else:
            base = Path.home() / APP_NAME
    base.mkdir(parents=True, exist_ok=True)
    return base


class DesktopTodoApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.base_dir = get_base_dir()
        self.todo_file = self.base_dir / TODO_FILENAME
        self.geom_file = self.base_dir / GEOM_FILENAME
        self.config_file = self.base_dir / CONFIG_FILENAME

        self.save_text_after_id = None
        self.save_geom_after_id = None
        self.auto_hide_after_id = None  # NEU: Timer für Auto-Hide
        # Zustände
        self.visible = True
        self._is_closing = False
        # Tray-Icon-Referenz
        self.tray_icon = None
        # App-Icon-Referenz
        self._app_icon_image = None
        # Für Dragging bei borderlosem Fenster
        self._drag_x = 0
        self._drag_y = 0
        # Konfiguration laden
        self.config = self.load_config()
        # App-/Fenster-Icon setzen, falls Pfad konfiguriert
        self.apply_app_icon()
        # State-Variablen (für Menü-Indikatoren)
        self.auto_hide_on_focus = bool(self.config.get("auto_hide_on_focus", False))
        self.alpha_var = tk.DoubleVar(value=float(self.config["window_alpha"]))
        # Styles für modernes Aussehen
        self.setup_styles()
        # Grundkonfiguration Fenster (auf Basis der Config)
        self.root.title(APP_NAME)
        self.root.geometry(DEFAULT_GEOMETRY)
        self.root.minsize(self.config["min_width"], self.config["min_height"])
        self.root.resizable(True, True)
        self.root.attributes("-alpha", self.config["window_alpha"])
        self.root.attributes("-topmost", self.config["always_on_top"])
        # Geometrie aus Datei laden (überschreibt DEFAULT_GEOMETRY)
        self.load_window_geometry()
        # Borderless-Status anwenden (ändert auch Events für Dragging)
        self.apply_borderless()
        # Änderungen an Größe/Position -> Geometrie speichern
        self.root.bind("<Configure>", self.on_configure)
        # Fokus erhalten -> Cursor ins Textfeld
        self.root.bind("<FocusIn>", self.on_focus_in)
        # Fokus verlieren -> ggf. Auto-Hide
        self.root.bind("<FocusOut>", self.on_focus_out)
        # Maus loslassen -> evtl. an Ränder andocken
        self.root.bind("<ButtonRelease-1>", self.snap_to_edges)
        # UI + Kontextmenü
        self.create_widgets()
        self.apply_colors()
        self.apply_font()
        self.create_context_menu()
        # Text laden
        self.load_content()
        # Tray-Icon starten (falls pystray verfügbar)
        self._start_tray_icon()
        # Hotkeys registrieren (global oder lokal)
        self.register_hotkeys()

    # ==================== Sichtbarkeit & Hotkey-Logik ====================

    def hide_window(self):
        """Fenster ausblenden und internen State aktualisieren."""
        if not self.visible:
            return
        self.root.withdraw()
        self.visible = False

    def show_window(self):
        """Fenster einblenden, in den Vordergrund holen und fokussieren."""
        if self.visible:
            return
        self.root.deiconify()
        self.root.lift()
        try:
            self.root.focus_force()
        except Exception:
            pass
        try:
            self.text.focus_set()
        except Exception:
            pass
        self.visible = True

    def toggle_visibility(self, event=None):
        """Ein-/Ausblenden umschalten (für Hotkeys, Tray, Auto-Hide)."""
        if self._is_closing:
            if event is not None:
                return "break"
            return

        if self.visible:
            self.hide_window()
        else:
            self.show_window()

        # Falls über ein Tk-Event aufgerufen, weitere Verarbeitung stoppen
        if event is not None:
            return "break"

    # ==================== KONFIG-LOAD/SAVE ====================
    
    def load_config(self):
        cfg = DEFAULT_CONFIG.copy()
        if self.config_file.exists():
            try:
                data = json.loads(self.config_file.read_text(encoding="utf-8"))
                for k, v in data.items():
                    if k in cfg:
                        cfg[k] = v
            except Exception as e:
                print(f"Fehler beim Laden der Konfiguration: {e}", file=sys.stderr)

        if not cfg.get("note_colors"):
            cfg["note_colors"] = DEFAULT_NOTE_COLORS

        return cfg

    def save_config(self):
        try:
            self.config_file.write_text(
                json.dumps(self.config, indent=2), encoding="utf-8"
            )
        except Exception as e:
            print(f"Fehler beim Speichern der Konfiguration: {e}", file=sys.stderr)

    def register_hotkeys(self):
        """Registriert globalen Hotkey (keyboard), mit Fallback auf lokalen Tk-Hotkey."""
        global_registered = False

        # Globaler Hotkey bevorzugt, falls Modul und Key gesetzt
        if keyboard is not None and GLOBAL_TOGGLE_KEY:
            try:
                keyboard.add_hotkey(
                    GLOBAL_TOGGLE_KEY,
                    lambda: self.root.after(0, self.toggle_visibility)
                )
                global_registered = True
            except Exception as e:
                print(
                    f"Globaler Hotkey '{GLOBAL_TOGGLE_KEY}' konnte nicht registriert werden: {e}",
                    file=sys.stderr,
                )

        # Fallback: lokaler Hotkey im Fenster
        if not global_registered and LOCAL_TOGGLE_KEY:
            self.root.bind(LOCAL_TOGGLE_KEY, self.toggle_visibility)

    # ==================== UI-Bau ====================

    def setup_styles(self):
        """ttk-Styles für Buttons, Frames und Scrollbar definieren."""
        self.style = ttk.Style(self.root)
        # neutrales Theme wählen, das sich gut anpassen lässt
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass

        bg = self.config["text_bg"]
        fg = self.config["text_fg"]

        # Grund-Frame-Hintergrund
        self.root.configure(bg=bg)
        self.style.configure("TFrame", background=bg)

        # Toolbar-Frame (Button-Leiste)
        self.style.configure(
            "Toolbar.TFrame",
            background=bg
        )

        # Moderner, flacher Button
        self.style.configure(
            "Toolbar.TButton",
            background=bg,
            foreground=fg,
            padding=(8, 2),
            borderwidth=0,
            focusthickness=0
        )
        self.style.map(
            "Toolbar.TButton",
            background=[
                ("pressed", "#333333"),
                ("active", "#222222")
            ]
        )

        # Schlanke Scrollbar im Dark-Style
        self.style.configure(
            "Custom.Vertical.TScrollbar",
            gripcount=0,
            background="#333333",
            troughcolor=bg,
            bordercolor=bg,
            arrowcolor="#888888",
            relief="flat"
        )
        self.style.map(
            "Custom.Vertical.TScrollbar",
            background=[
                ("pressed", "#555555"),
                ("active", "#444444")
            ]
        )

    def apply_app_icon(self):
        """Setzt das App-/Fenster-Icon.

        Priorität:
        1) APP_ICON_PATH (direkter Dateipfad, z.B. im Dev-Setup)
        2) ICON_APP_REL relativ über resource_path (für PyInstaller/Installer)
        """
        icon_path = APP_ICON_PATH

        # 1) direkter Pfad, falls gesetzt
        if icon_path:
            try:
                if icon_path.lower().endswith(".ico"):
                    try:
                        self.root.iconbitmap(icon_path)
                        return
                    except Exception:
                        pass

                img = tk.PhotoImage(file=icon_path)
                self._app_icon_image = img
                self.root.iconphoto(True, img)
                return
            except Exception as e:
                print(f"Fehler beim Setzen des App-Icons ({icon_path}): {e}", file=sys.stderr)

        # 2) Fallback: relative Ressource (für EXE/Installer)
        try:
            rel_path = resource_path(ICON_APP_REL)
            if rel_path.suffix.lower() == ".ico":
                try:
                    self.root.iconbitmap(rel_path)
                    return
                except Exception:
                    pass

            img = tk.PhotoImage(file=rel_path)
            self._app_icon_image = img
            self.root.iconphoto(True, img)
        except Exception as e:
            print(f"Fehler beim Setzen des App-Icons (Ressource {ICON_APP_REL}): {e}", file=sys.stderr)


    def create_widgets(self):
        # Hauptcontainer
        main_frame = ttk.Frame(self.root, padding=(6, 6, 6, 4), style="TFrame")
        main_frame.pack(fill="both", expand=True)

        # Container für Text + Scrollbar
        text_container = ttk.Frame(main_frame, style="TFrame")
        text_container.pack(side="top", fill="both", expand=True)

        self.text = tk.Text(
            text_container,
            wrap="word",
            undo=True,
            height=10,
            bd=0,
            highlightthickness=0,
        )
        self.text.pack(side="left", fill="both", expand=True)

        # Tags für farbige Einträge (aus Config)
        self.note_colors = list(self.config["note_colors"])
        for i, color in enumerate(self.note_colors):
            self.text.tag_configure(f"note{i}", background=color)

        # Schlanke, eigene Scrollbar rechts vom Text
        scrollbar = ttk.Scrollbar(
            text_container,
            orient="vertical",
            command=self.text.yview,
            style="Custom.Vertical.TScrollbar",
        )
        scrollbar.pack(side="right", fill="y")
        self.text.configure(yscrollcommand=scrollbar.set)

        # Textänderungen -> einfärben + Speichern planen
        self.text.bind("<KeyRelease>", self.on_text_changed)

        # Button-Leiste: nur ein schlanker "Save"-Button, rechts ausgerichtet
        button_frame = ttk.Frame(main_frame, style="Toolbar.TFrame")
        button_frame.pack(side="bottom", fill="x", pady=(6, 0))

        self.save_button = ttk.Button(
            button_frame,
            text="Save",
            command=self.add_timestamp_and_save,
            style="Toolbar.TButton",
        )
        self.save_button.pack(side="right")
        
    # Tray-Icon und Kontextmenü.
    def apply_colors(self):
        """Farben aus Config auf Textfeld + Tags anwenden."""
        self.text.configure(
            fg=self.config["text_fg"],
            bg=self.config["text_bg"],
            insertbackground=self.config["text_fg"],
        )
        self.note_colors = list(self.config["note_colors"])
        for i, color in enumerate(self.note_colors):
            self.text.tag_configure(f"note{i}", background=color)

    def apply_font(self):
        """Schrift aus Config anwenden."""
        self.text.configure(
            font=(self.config["font_family"], self.config["font_size"])
        )

    # ==================== Kontextmenü ====================

    def create_context_menu(self):
        self.menu = tk.Menu(self.root, tearoff=0)

        # Booleans für Menü-Checkmarks
        self.autohide_var = tk.BooleanVar(
            value=bool(self.config.get("auto_hide_on_focus", False))
        )
        self.borderless_var = tk.BooleanVar(
            value=bool(self.config.get("borderless", False))
        )

        # Untermenü: Farben
        colors_menu = tk.Menu(self.menu, tearoff=0)
        colors_menu.add_command(
            label="Textfarbe…",
            command=self.change_text_color,
        )
        colors_menu.add_command(
            label="Hintergrund…",
            command=self.change_background_color,
        )
        for idx in range(len(self.note_colors)):
            colors_menu.add_command(
                label=f"Eintragsfarbe {idx+1}…",
                command=lambda i=idx: self.change_note_color(i),
            )
        self.menu.add_cascade(label="Farben", menu=colors_menu)

        # Untermenü: Schrift
        self.font_menu = tk.Menu(self.menu, tearoff=0)
        current_font_label = f"Aktuell: {self.config['font_family']} {self.config['font_size']}"
        self.font_menu.add_command(
            label=current_font_label,
            state="disabled",
        )
        self.font_current_label_index = 0
        self.font_menu.add_separator()
        self.font_menu.add_command(
            label="Schrift wählen…",
            command=self.show_font_dialog,
        )
        self.menu.add_cascade(label="Schrift", menu=self.font_menu)

        # Untermenü: Transparenz mit Indikator (Radiobuttons)
        alpha_menu = tk.Menu(self.menu, tearoff=0)
        for value, label in [
            (0.5, "50%"),
            (0.7, "70%"),
            (0.85, "85%"),
            (0.95, "95%"),
            (1.0, "100%"),
        ]:
            alpha_menu.add_radiobutton(
                label=label,
                value=value,
                variable=self.alpha_var,
                command=lambda v=value: self.set_alpha(v),
            )
        self.menu.add_cascade(label="Transparenz", menu=alpha_menu)

        # Toggles
        self.menu.add_checkbutton(
            label="Auto-Hide bei Fokusverlust",
            variable=self.autohide_var,
            command=self._toggle_autohide_from_menu,
        )
        self.menu.add_checkbutton(
            label="Randlos (Borderless)",
            variable=self.borderless_var,
            command=self.toggle_borderless,
        )
        self.menu.add_command(
            label="Immer im Vordergrund umschalten",
            command=self._toggle_topmost
        )

           # NEU: Ein-/Ausblenden über Kontextmenü
        self.menu.add_command(
            label="Fenster ein-/ausblenden",
            command=self.toggle_visibility,
        )

        # Handbuch
        self.menu.add_command(
            label="Handbuch öffnen",
            command=self.open_manual,
        )

        self.menu.add_separator()
        self.menu.add_command(label="Beenden", command=self.on_close)

        # Rechtsklick-Bindung: auf Fenster UND Textfeld
        self.root.bind("<Button-3>", self._show_context_menu)
        self.text.bind("<Button-3>", self._show_context_menu)
     
    def update_font_menu_label(self):
        """Beschriftung 'Aktuell: ...' im Schrift-Untermenü aktualisieren."""
        label = f"Aktuell: {self.config['font_family']} {self.config['font_size']}"
        self.font_menu.entryconfig(self.font_current_label_index, label=label)

    # ==================== Borderless & Drag ====================

    def apply_borderless(self):
        """Borderless aus self.config anwenden und Drag-Events verwalten."""
        borderless = bool(self.config.get("borderless", False))
        geom = self.root.winfo_geometry()
        self.root.overrideredirect(borderless)
        self.root.geometry(geom)

        if borderless:
            self.root.bind("<ButtonPress-1>", self._start_move)
            self.root.bind("<B1-Motion>", self._on_move)
        else:
            self.root.unbind("<ButtonPress-1>")
            self.root.unbind("<B1-Motion>")

    def _start_move(self, event):
        self._drag_x = event.x
        self._drag_y = event.y

    def _on_move(self, event):
        x = event.x_root - self._drag_x
        y = event.y_root - self._drag_y
        self.root.geometry(f"+{x}+{y}")

    # ==================== Kontextmenü-Callbacks ====================

    def _show_context_menu(self, event):
        # Wenn das Fenster gerade geschlossen wird / schon weg ist -> nix tun
        if getattr(self, "_is_closing", False):
            return
        try:
            self.menu.tk_popup(event.x_root, event.y_root)
            self.menu.grab_release()
        except tk.TclError:
            # Tk bereits zerstört o.Ä. -> einfach ignorieren
            pass

    def _toggle_topmost(self):
        current = bool(self.root.attributes("-topmost"))
        new = not current
        self.root.attributes("-topmost", new)
        self.config["always_on_top"] = new
        self.save_config()

    def _toggle_autohide_from_menu(self):
        self.auto_hide_on_focus = self.autohide_var.get()
        self.config["auto_hide_on_focus"] = self.auto_hide_on_focus
        self.save_config()

    def toggle_borderless(self):
        self.config["borderless"] = self.borderless_var.get()
        self.apply_borderless()
        self.save_config()

    def change_text_color(self):
        color = colorchooser.askcolor(
            initialcolor=self.config["text_fg"],
            title="Textfarbe wählen",
        )[1]
        if color:
            self.config["text_fg"] = color
            self.apply_colors()
            self.save_config()

    def change_background_color(self):
        color = colorchooser.askcolor(
            initialcolor=self.config["text_bg"],
            title="Hintergrundfarbe wählen",
        )[1]
        if color:
            self.config["text_bg"] = color
            self.apply_colors()
            self.save_config()

    def change_note_color(self, idx: int):
        current = self.note_colors[idx] if idx < len(self.note_colors) else "#333333"
        color = colorchooser.askcolor(
            initialcolor=current,
            title=f"Eintragsfarbe {idx+1} wählen",
        )[1]
        if color:
            self.note_colors[idx] = color
            self.config["note_colors"][idx] = color
            self.apply_colors()
            self.colorize_entries()
            self.save_config()

    def show_font_dialog(self):
        """Toplevel mit Dropdown (Combobox) für Schriftart + Größe."""
        win = tk.Toplevel(self.root)
        win.title("Schrift wählen")
        win.transient(self.root)
        win.grab_set()

        frm = ttk.Frame(win, padding=10)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="Schriftart:").grid(row=0, column=0, sticky="w")
        fonts = sorted(set(tkfont.families()))
        fam_var = tk.StringVar(value=self.config["font_family"])
        combo = ttk.Combobox(
            frm,
            values=fonts,
            textvariable=fam_var,
            state="readonly",
            width=30,
        )
        combo.grid(row=0, column=1, sticky="ew", padx=(5, 0))

        ttk.Label(frm, text="Größe:").grid(row=1, column=0, sticky="w", pady=(8, 0))
        try:
            current_size = int(self.config["font_size"])
        except Exception:
            current_size = DEFAULT_FONT_SIZE
        size_var = tk.IntVar(value=current_size)
        size_spin = tk.Spinbox(
            frm,
            from_=6,
            to=72,
            textvariable=size_var,
            width=5,
        )
        size_spin.grid(row=1, column=1, sticky="w", padx=(5, 0), pady=(8, 0))

        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=(12, 0), sticky="e")

        def on_ok():
            fam = fam_var.get() or self.config["font_family"]
            try:
                size = int(size_var.get())
            except Exception:
                size = self.config["font_size"]
            self.config["font_family"] = fam
            self.config["font_size"] = size
            self.apply_font()
            self.update_font_menu_label()
            self.save_config()
            win.destroy()

        def on_cancel():
            win.destroy()

        ok_btn = ttk.Button(btn_frame, text="OK", command=on_ok)
        cancel_btn = ttk.Button(btn_frame, text="Abbrechen", command=on_cancel)
        cancel_btn.pack(side="right", padx=(5, 0))
        ok_btn.pack(side="right")

        frm.columnconfigure(1, weight=1)

    def set_alpha(self, value: float):
        self.alpha_var.set(float(value))
        self.config["window_alpha"] = float(value)
        self.root.attributes("-alpha", self.config["window_alpha"])
        self.save_config()

    def open_manual(self):
        """Öffnet das Handbuch (PDF) mit der Standard-Anwendung."""
        try:
            manual_path = resource_path(MANUAL_REL)
            if manual_path.exists():
                os.startfile(manual_path)  # Windows
            else:
                print(f"Manual nicht gefunden unter {manual_path}", file=sys.stderr)
        except Exception as e:
            print(f"Manual konnte nicht geöffnet werden: {e}", file=sys.stderr)

    # ==================== Text-Persistenz & Einfärben ====================

    def load_content(self):
        if self.todo_file.exists():
            try:
                content = self.todo_file.read_text(encoding="utf-8")
                self.text.delete("1.0", "end")
                self.text.insert("1.0", content)
            except Exception as e:
                print(f"Fehler beim Laden des Textes: {e}", file=sys.stderr)

        self.text.focus_set()
        self.colorize_entries()

    def on_text_changed(self, event=None):
        self.colorize_entries()
        self.schedule_text_save()

    def schedule_text_save(self, event=None):
        if self.save_text_after_id is not None:
            self.root.after_cancel(self.save_text_after_id)
        self.save_text_after_id = self.root.after(800, self.save_content)

    def save_content(self):
        self.save_text_after_id = None
        try:
            text = self.text.get("1.0", "end-1c")
            self.todo_file.write_text(text, encoding="utf-8")
        except Exception as e:
            print(f"Fehler beim Speichern des Textes: {e}", file=sys.stderr)

    def _is_timestamp_line(self, line: str) -> bool:
        line = line.strip()
        return line.startswith("[") and "]" in line and len(line) >= 10

    def colorize_entries(self):
        for i in range(len(self.note_colors)):
            self.text.tag_remove(f"note{i}", "1.0", "end")

        content = self.text.get("1.0", "end-1c")
        if not content.strip():
            return

        lines = content.split("\n")
        entry_start_line = 1
        entry_index = 0

        for line_no, line in enumerate(lines, start=1):
            if self._is_timestamp_line(line):
                if line_no >= entry_start_line:
                    tag_name = f"note{entry_index % len(self.note_colors)}"
                    start_idx = f"{entry_start_line}.0"
                    end_idx = f"{line_no}.end"
                    self.text.tag_add(tag_name, start_idx, end_idx)
                    entry_index += 1
                    entry_start_line = line_no + 1

    # ==================== Geometrie-Persistenz ====================

    def load_window_geometry(self):
        if self.geom_file.exists():
            try:
                geom = self.geom_file.read_text(encoding="utf-8").strip()
                if geom:
                    self.root.geometry(geom)
            except Exception as e:
                print(f"Fehler beim Laden der Fenstergeometrie: {e}", file=sys.stderr)

    def save_window_geometry(self):
        try:
            geom = self.root.winfo_geometry()
            self.geom_file.write_text(geom, encoding="utf-8")
        except Exception as e:
            print(f"Fehler beim Speichern der Fenstergeometrie: {e}", file=sys.stderr)

    # ==================== Events & Logik ====================

    def on_configure(self, event):
        # Beim Schließen keine neuen Timer mehr planen
        if self._is_closing:
            return

        if self.save_geom_after_id is not None:
            try:
                self.root.after_cancel(self.save_geom_after_id)
            except tk.TclError:
                pass
            self.save_geom_after_id = None

        self.save_geom_after_id = self.root.after(300, self.save_window_geometry)

    def on_focus_in(self, event):
        self.text.focus_set()

    def on_focus_out(self, event):
        if not self.auto_hide_on_focus or self._is_closing:
            return

        # alten Auto-Hide-Callback abbrechen, falls noch geplant
        if self.auto_hide_after_id is not None:
            try:
                self.root.after_cancel(self.auto_hide_after_id)
            except tk.TclError:
                pass
            self.auto_hide_after_id = None

        # neuen Auto-Hide-Callback planen
        self.auto_hide_after_id = self.root.after(
            80, self._auto_hide_if_still_unfocused
        )

    def _auto_hide_if_still_unfocused(self):
        """Versteckt das Fenster, wenn Auto-Hide aktiv ist und der Fokus weg ist."""
        # Callback erledigt -> ID zurücksetzen
        self.auto_hide_after_id = None

        if self._is_closing or not self.auto_hide_on_focus:
            return

        # Wenn das Fenster irgendwo noch Fokus hat -> nichts tun
        try:
            if self.root.focus_displayof() is not None:
                return
        except tk.TclError:
            # Tk schon weg -> einfach abbrechen
            return

        # Nur verstecken, wenn aktuell sichtbar
        if self.visible:
            self.hide_window()

    def add_timestamp_and_save(self):
        end_index = self.text.index("end-1c")
        last_char = self.text.get("end-2c", "end-1c") if end_index != "1.0" else ""

        if last_char not in ("\n", ""):
            self.text.insert("end", "\n")

        now_line = datetime.now().strftime(TIMESTAMP_FORMAT)
        self.text.insert("end", now_line + "\n")

        self.save_content()
        self.colorize_entries()

    def snap_to_edges(self, event=None):
        self.root.update_idletasks()

        x = self.root.winfo_x()
        y = self.root.winfo_y()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()

        snap = self.config.get("snap_distance", DEFAULT_SNAP_DISTANCE)

        new_x, new_y = x, y

        if x < snap:
            new_x = 0
        elif sw - (x + w) < snap:
            new_x = sw - w

        if y < snap:
            new_y = 0
        elif sh - (y + h) < snap:
            new_y = sh - h

        if (new_x, new_y) != (x, y):
            self.root.geometry(f"+{new_x}+{new_y}")
            self.save_window_geometry()

    # ==================== Tray-Icon ====================

    def _create_tray_image(self, width=64, height=64):
        """Erzeugt das Tray-Icon-Bild.

        Priorität:
        1) TRAY_ICON_PATH oder APP_ICON_PATH (direkte Dateipfade)
        2) ICON_TRAY_REL über resource_path (für EXE/Installer)
        3) generiertes 'T'-Icon
        """
        if Image is None:
            return None

        # 1) direkter Pfad
        icon_path = TRAY_ICON_PATH or APP_ICON_PATH
        if icon_path:
            try:
                img = Image.open(icon_path).convert("RGBA")
                if img.size != (width, height):
                    resample = getattr(Image, "LANCZOS", Image.BICUBIC)
                    img = img.resize((width, height), resample)
                return img
            except Exception as e:
                print(f"Fehler beim Laden des Tray-Icons ({icon_path}): {e}", file=sys.stderr)

        # 2) Fallback: relative Ressource
        try:
            rel_path = resource_path(ICON_TRAY_REL)
            img = Image.open(rel_path).convert("RGBA")
            if img.size != (width, height):
                resample = getattr(Image, "LANCZOS", Image.BICUBIC)
                img = img.resize((width, height), resample)
            return img
        except Exception as e:
            print(f"Fehler beim Laden des Tray-Icons (Ressource {ICON_TRAY_REL}): {e}", file=sys.stderr)

        # 3) Fallback: generiertes kleines 'T'-Icon
        if ImageDraw is None:
            return None

        image = Image.new("RGB", (width, height), (30, 30, 30))
        draw = ImageDraw.Draw(image)
        margin = 8
        draw.rectangle(
            [margin, margin, width - margin, height - margin],
            outline=(180, 180, 180),
            fill=(50, 50, 50),
        )
        draw.text((width // 3, height // 3), "T", fill=(220, 220, 220))
        return image

    def _on_tray_toggle(self, icon, item):
        self.root.after(0, self.toggle_visibility)

    def _on_tray_toggle_autohide(self, icon, item):
        self.auto_hide_on_focus = not self.auto_hide_on_focus
        self.autohide_var.set(self.auto_hide_on_focus)
        self.config["auto_hide_on_focus"] = self.auto_hide_on_focus
        self.save_config()

    def _on_tray_quit(self, icon, item):
        icon.stop()
        self.root.after(0, self.on_close)

    def _start_tray_icon(self):
        if pystray is None or Image is None:
            print(
                "Hinweis: 'pystray' oder 'Pillow' nicht installiert. "
                "Tray-Icon ist deaktiviert.\n"
                "Installiere sie mit:\n    pip install pystray pillow",
                file=sys.stderr,
            )
            return

        image = self._create_tray_image()
        if image is None:
            return

        menu = pystray.Menu(
            pystray.MenuItem("Tafel ein/aus", self._on_tray_toggle),
            pystray.MenuItem(
                "Auto-Hide bei Fokusverlust",
                self._on_tray_toggle_autohide,
                checked=lambda item: self.auto_hide_on_focus,
            ),
            pystray.MenuItem("Beenden", self._on_tray_quit),
        )
        self.tray_icon = pystray.Icon(APP_NAME, image, APP_NAME, menu)

        def run_icon():
            self.tray_icon.run()

        t = threading.Thread(target=run_icon, daemon=True)
        t.start()

    # ==================== Lebenszyklus ====================

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()
    
    def on_close(self):
        # merken, dass wir schließen -> Callbacks & Menüs sollen nichts mehr tun
        self._is_closing = True

        # alle geplanten after-Callbacks abbrechen
        for attr in ("save_text_after_id", "save_geom_after_id", "auto_hide_after_id"):
            after_id = getattr(self, attr, None)
            if after_id is not None:
                try:
                    self.root.after_cancel(after_id)
                except tk.TclError:
                    pass
                setattr(self, attr, None)

        # Inhalte & Geometrie noch speichern (so gut es geht)
        try:
            self.save_content()
        except Exception:
            pass
        try:
            self.save_window_geometry()
        except Exception:
            pass

        # Tray-Icon stoppen
        if self.tray_icon is not None:
            try:
                self.tray_icon.stop()
            except Exception:
                pass

        # Tk-Fenster schließen
        try:
            self.root.destroy()
        except tk.TclError:
            pass

def main():
    root = tk.Tk()
    app = DesktopTodoApp(root)
    app.run()

if __name__ == "__main__":
    main()

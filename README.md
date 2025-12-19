# MindPic

Eine schlanke Windows Desktop-Notiz-App mit Zeitstempel-Organisation und farbigen Blöcken.

![Version](https://img.shields.io/badge/version-0.2.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)

## Features

- Always-on-Top mit automatischem Andocken an Bildschirmränder
- Zeitstempel-basierte Einträge mit automatischer Farbkodierung
- Auto-Save für Inhalte und Einstellungen
- Borderless Mode mit Drag & Resize
- Globaler Hotkey (F9) zum Ein-/Ausblenden
- System Tray Integration
- Anpassbare Schriftart, Farben und Transparenz
- Optional: Auto-Hide bei Fokusverlust

## Quick Start

### Für Nutzer

1. Download der aktuellen Version von [Releases](https://github.com/BeRob/mindpic/releases)
2. `MindPic_Setup.exe` ausführen und installieren
3. MindPic über das Startmenü starten
4. Mit F9 jederzeit ein-/ausblenden

### Für Entwickler

```bash
git clone https://github.com/BeRob/mindpic.git
cd mindpic
pip install -r mindpic/requirements.txt
python -m mindpic
```

## Installation

**Windows Installer:** Download von `MindPic_Setup.exe` und Installation über den Wizard.

**Portable:** ZIP herunterladen, entpacken und `MindPic.exe` starten.

## Bedienung

### Grundfunktionen

Einfach ins Textfeld klicken und losschreiben. Der Inhalt wird automatisch gespeichert.

**Zeitstempel hinzufügen:**
1. Notiz schreiben
2. Save-Button (unten rechts) klicken
3. Zeitstempel `[DD-MM-YYYY HH:MM]` wird eingefügt
4. Einträge werden automatisch farbig markiert

**Sichtbarkeit:**
- F9 drücken (funktioniert systemweit)
- Rechtsklick → "Fenster ein-/ausblenden"
- System Tray Icon verwenden

### Fenster

**Verschieben:**
- Normal: Titelleiste ziehen
- Borderless: Irgendwo ins Fenster klicken und ziehen

**Größe ändern:** An den Fensterrändern ziehen (Minimum: 420×220px)

**Snap:** Fenster nah an einen Bildschirmrand ziehen, es dockt automatisch an.

### Kontextmenü (Rechtsklick)

- **Farben** - Text, Hintergrund und Eintragsfarben anpassen
- **Schrift** - Font und Größe wählen
- **Randlos (Borderless)** - Fensterrahmen ein/aus
- **Transparenz** - 50% bis 100%
- **Auto-Hide bei Fokusverlust** - Automatisches Ausblenden
- **Immer im Vordergrund umschalten** - Always-on-top
- **Beenden** - App schließen

## Development

### Struktur

```
mindpic/
├── app.py           # Hauptanwendung (MindPicApp)
├── ui.py            # UI-Komponenten, Styles, Kontextmenü
├── settings.py      # Zentrale Konfiguration
├── persistence.py   # Speichern & Laden von Inhalt/Geometrie
├── config_io.py     # JSON Config mit Deep Merge
├── colorize.py      # Zeitstempel-Erkennung & Farbblöcke
├── hotkeys.py       # Globale Hotkeys
├── tray.py          # System Tray
├── paths.py         # Pfadauflösung (Dev vs. Frozen)
├── __main__.py      # Entry Point mit Logging
└── run_mindpic.py   # PyInstaller Launcher
```

### Setup

```bash
cd D:\Coding\Projekte\mindpic
python -m venv .venv
.venv\Scripts\activate
pip install -r mindpic/requirements.txt
python -m mindpic
```

### Build

**Executable erstellen:**
```bash
cd mindpic
pyinstaller MindPic.spec
# Output: dist/MindPic/MindPic.exe
```

**Installer bauen:**

[Inno Setup](https://jrsoftware.org/isinfo.php) muss installiert sein.

```bash
# installer.iss öffnen und ProjectDir (Zeile 8) anpassen
iscc mindpic/installer.iss
# Output: mindpic/dist/MindPic_Setup.exe
```

### Testing

```bash
# Syntax Check
python -m py_compile mindpic/app.py mindpic/ui.py

# Import Check
python -c "import mindpic; print('OK')"

# Debug Logging
# settings.py: LOG_LEVEL = "DEBUG"
python -m mindpic
# siehe mindpic.log
```

## Konfiguration

Alle Einstellungen sind in `settings.py` zentralisiert:

```python
# Verhalten
DEFAULT_ALWAYS_ON_TOP = True
DEFAULT_BORDERLESS = False
DEFAULT_WINDOW_ALPHA = 0.92
DEFAULT_SNAP_DISTANCE = 16

# Hotkeys
LOCAL_TOGGLE_KEY = "<F9>"
GLOBAL_TOGGLE_HOTKEY = "f9"

# Features
ENABLE_TRAY = True
ENABLE_GLOBAL_HOTKEYS = True
DEFAULT_AUTO_HIDE_ON_FOCUS_LOST = False
AUTO_HIDE_DELAY_MS = 650

# UI
DEFAULT_FONT_FAMILY = "Dosis"
DEFAULT_FONT_SIZE = 9
```

Benutzereinstellungen werden in `config.json` und die Fenstergeometrie in `window_geometry.json` gespeichert.

## Architektur

**State Management:**
- `MindPicApp` hält den Runtime State
- Config wird beim Start aus `config_io.load_config()` geladen (Merge von Defaults und gespeicherten Werten)
- Fenstergeometrie wird separat persistiert

**Debouncing & Throttling:**
- Config-Saves werden um 2s verzögert (`_schedule_config_save()`)
- Recolorize wird nach 350ms ausgeführt
- Window Snap ist auf max. 10x/sec gedrosselt
- Font-Liste wird gecacht
- Alle Pfadfunktionen nutzen `@lru_cache`

**Event Flow:**
- UI Callbacks aktualisieren die Config und rufen `_schedule_config_save()`
- Text-Änderungen triggern `<<Modified>>` → debounced recolorize
- Configure Events triggern throttled Snap Checks
- Auto-Hide nutzt Focus Events mit verzögerten Jobs

**Path Resolution:**
- `paths.py` erkennt ob frozen (`sys.frozen`) und löst Pfade entsprechend auf
- DEV: nutzt `settings.DEV_PROJECT_DIR`
- Frozen: nutzt `_MEIPASS` für Assets, Exe-Verzeichnis für Daten

## Dependencies

**Core:**
- `tkinter` (inkl. Python)
- `keyboard` (optional, für globale Hotkeys)
- `pystray` (optional, für System Tray)
- `pillow` (optional, für Tray Icon)

**Build:**
- `pyinstaller`
- Inno Setup

Alle Python-Dependencies stehen in `requirements.txt`.

## Troubleshooting

**F9 funktioniert nicht:**
- Prüfen ob andere App F9 belegt
- Als Admin starten
- `pip install keyboard` ausführen

**Fensterposition wird nicht gespeichert:**
- `window_geometry.json` im App-Verzeichnis prüfen
- Schreibrechte für App-Ordner überprüfen

**Tray Icon fehlt:**
- `pip install pystray pillow`
- In `settings.py`: `ENABLE_TRAY = True`

**Farben ändern sich nicht:**
- Zeitstempel müssen Format `[DD-MM-YYYY HH:MM]` haben
- Save-Button klicken um Recolorize zu triggern

## License

MIT License - siehe [LICENSE](LICENSE) Datei.

## Roadmap

- Linux/macOS Support
- Export nach Markdown/HTML
- Suchfunktion
- Notiz-Templates
- Cloud Sync
- Mehrere Notizseiten/Tabs

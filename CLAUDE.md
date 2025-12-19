# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MindPic is a Windows desktop note-taking application with timestamp-based entry organization and color-coded blocks. It's built with Python/Tkinter and packaged as a standalone Windows executable.

**Key Characteristics:**
- Desktop note app with "always-on-top" and snap-to-edges functionality
- Automatic persistence of content, settings, and window geometry
- System tray integration with global hotkeys (F9)
- PyInstaller one-dir build distribution
- Inno Setup installer for Windows

## Architecture

### Module Structure

```
mindpic/
├── app.py          - Main orchestrator (MindPicApp class)
├── ui.py           - UI components, styles, context menus, borderless drag/resize
├── settings.py     - Centralized configuration (all user-editable constants)
├── persistence.py  - Content & window geometry I/O
├── config_io.py    - JSON config load/save with deep merge
├── colorize.py     - Timestamp detection & color block assignment
├── hotkeys.py      - Global hotkey manager (optional keyboard module)
├── tray.py         - System tray controller (optional pystray)
├── paths.py        - Path resolution (DEV vs PyInstaller frozen)
├── __main__.py     - Entry point with logging setup
└── run_mindpic.py  - PyInstaller launcher script
```

### Key Design Patterns

**State Management:**
- `MindPicApp` holds runtime state (config dict, visibility flags, job IDs)
- Config is loaded at init from `config_io.load_config()` which merges saved config with defaults from `settings.DEFAULT_CONFIG`
- Window geometry persisted separately in `window_geometry.json`

**Debouncing & Throttling:**
- Config saves are debounced (2s delay) via `_schedule_config_save()`
- Recolorize operations are debounced (350ms) after text changes
- Window snap-to-edge is throttled (max 10x/sec)
- Font list is cached at module level in ui.py
- All path functions use `@lru_cache` for performance

**Event Flow:**
- UI callbacks (`_menu_set_*`) update config dict and call `_schedule_config_save()`
- Text modifications trigger `<<Modified>>` event → debounced recolorize
- Configure events trigger throttled snap checks
- Auto-hide uses focus events with delayed job scheduling

**Borderless Mode:**
- `BorderlessDragger` and `BorderlessResizer` manage drag/resize with stored binding IDs
- Uses `add="+"` flag to avoid removing other event handlers
- Graceful unbind via stored binding IDs

**Path Resolution:**
- `paths.py` detects frozen state (`sys.frozen`) and resolves paths accordingly
- DEV: uses `settings.DEV_PROJECT_PATH`
- Frozen: uses `_MEIPASS` for assets, executable dir for data files
- Override via `settings.SAVE_DIR_OVERRIDE` if needed

**Logging:**
- Configured in `__main__.setup_logging()` before app init
- Dual output: file (`mindpic.log`) + console
- Level controlled by `settings.LOG_LEVEL`
- All modules use `logger = logging.getLogger(__name__)`

## Common Development Commands

### Setup
```bash
# Install dependencies
pip install -r mindpic/requirements.txt

# Run from source (from project root)
cd D:\Coding\Projekte\mindpic
python -m mindpic
```

### Building Executable
```bash
# Build with PyInstaller (from mindpic/ directory)
cd mindpic
pyinstaller MindPic.spec

# Output: dist/MindPic/MindPic.exe (one-dir build)
```

### Creating Installer
```bash
# Compile with Inno Setup (requires Inno Setup installed)
# Edit installer.iss first to set correct ProjectDir path (line 8)
iscc mindpic/installer.iss

# Output: mindpic/dist/MindPic_Setup.exe
```

### Testing
```bash
# Syntax check
python -m py_compile mindpic/app.py mindpic/ui.py

# Import check
python -c "import mindpic; print('OK')"

# Run with specific log level
# Edit settings.py: LOG_LEVEL = "DEBUG"
python -m mindpic
# Check mindpic.log for detailed output
```

## Configuration System

All user-configurable values are centralized in `settings.py`:

**App Behavior:**
- `DEFAULT_ALWAYS_ON_TOP`, `DEFAULT_BORDERLESS`, `DEFAULT_WINDOW_ALPHA`
- `AUTOSAVE_INTERVAL_MS`, `AUTO_HIDE_DELAY_MS`
- `DEFAULT_SNAP_DISTANCE`

**UI Constants (UI_* prefix):**
- `UI_THEME_NAME`, `UI_ALPHA_PRESETS`
- `UI_BUTTON_PAD_XY`, `UI_MAIN_PADDING`
- `UI_BORDERLESS_GRIP_*` (symbol, offset, min dimensions)

**Hotkeys:**
- `LOCAL_TOGGLE_KEY` (Tk binding, e.g., "<F9>")
- `GLOBAL_TOGGLE_HOTKEY` (keyboard module, e.g., "f9")
- `ENABLE_GLOBAL_HOTKEYS` (master toggle)

**Feature Flags:**
- `ENABLE_TRAY` (system tray integration)
- `ENABLE_SNAP` (in app.py, controls snap-to-edges)

**Important:** Never hardcode UI constants in modules. Always import from `settings.py`.

## Adding New Features

**New Config Setting:**
1. Add to `settings.DEFAULT_CONFIG` dict
2. Add default constant (e.g., `DEFAULT_MY_SETTING`)
3. Access in code via `self.config.get("my_setting", settings.DEFAULT_MY_SETTING)`
4. If UI-related, use `UI_*` prefix in constant name

**New Menu Item:**
1. Add callback in `app.py` (follows pattern: `_menu_set_*`)
2. Update `ui.MenuCallbacks` dataclass
3. Add menu item in `ui.create_context_menu()`
4. Call `self._schedule_config_save()` after changes

**New Hotkey:**
1. Add to `settings.py` (local and/or global)
2. Bind in `app.py.__init__()` using `self.root.bind()` or `self._hotkeys.register_global_hotkey()`

## Exception Handling Pattern

Use specific exceptions instead of generic `except Exception:`:

```python
try:
    # File operation
except (OSError, IOError) as e:
    logger.error(f"Failed to ...: {e}")
except json.JSONDecodeError as e:
    logger.error(f"Invalid JSON: {e}")
```

**Common patterns:**
- File I/O: `OSError, IOError`
- Encoding: `UnicodeDecodeError`
- JSON: `json.JSONDecodeError`
- Imports: `ImportError`

## Notes on Dependencies

**Optional dependencies** (graceful degradation):
- `keyboard` (global hotkeys) - falls back to local Tk bindings only
- `pystray` + `pillow` (system tray) - tray disabled if unavailable

**Check availability:**
- `hotkeys.HotkeyManager.available` property
- `tray.TrayController.available` property

## Performance Considerations

**When modifying text processing:**
- Keep recolorize logic fast (runs on every keystroke after debounce)
- Current approach: full text scan via `iter_blocks()` - acceptable for <10k lines
- For larger texts: consider incremental updates

**When adding config options:**
- Use `_schedule_config_save()` instead of immediate `save_config()`
- Avoids disk I/O spikes during rapid setting changes

**When adding path lookups:**
- Add `@lru_cache(maxsize=None)` decorator to getter functions
- Paths are constant during runtime

**When adding UI dialogs:**
- Cache expensive operations (like font list in `get_available_fonts()`)

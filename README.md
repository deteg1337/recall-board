# Recall Board

[![CI](https://github.com/deteg1337/recall-board/actions/workflows/ci.yml/badge.svg)](https://github.com/deteg1337/recall-board/actions/workflows/ci.yml)

A clipboard history manager for GNOME/Wayland. Press **Super+V** to open a popup with your clipboard history — click any entry to copy it back.

## Features

- Clipboard history stored persistently in SQLite
- Wayland-native — GDK clipboard API for monitoring, `wl-copy` for writing
- GTK4 + libadwaita popup (follows GNOME HIG)
- Global shortcut (Super+V) auto-registered via GNOME Settings
- Autostart on login via XDG autostart (registered on first launch)
- Daemon mode — runs silently in the background, activated via D-Bus
- Click or Enter on an entry pastes it directly into the active window
- Arrow key navigation in the entry list
- Escape or focus-loss closes the popup
- Deduplication: re-copied entries move to the top

## Installation

```bash
git clone https://github.com/deteg1337/recall-board.git
cd recall-board
./install.sh
```

The script checks all dependencies, installs the app to `~/.local/`, registers Super+V, and sets up autostart. Press **Super+V** to open Recall Board after installation.

To uninstall:
```bash
./uninstall.sh
```

---

## Requirements

- Ubuntu 24.04 LTS (GNOME + Wayland session)
- Python 3.12+
- GTK4, libadwaita, wl-clipboard, wtype

## Setup

```bash
sudo apt install python3-gi gir1.2-gtk-4.0 gir1.2-adw-1 wl-clipboard wtype
```

Verify:
```bash
python3 -c "import gi; gi.require_version('Gtk', '4.0'); gi.require_version('Adw', '1'); from gi.repository import Gtk, Adw; print('GTK', Gtk.get_major_version(), '- OK')"
```

## How to Test

```bash
sudo apt install python3-pytest
python3 -m pytest tests/ -v
```

## How to Run

```bash
python3 src/main.py
```

The app starts as a background daemon. Press **Super+V** to open the popup. The Super+V shortcut is registered automatically in GNOME Settings on first launch.

## How to Test D-Bus Activation

```bash
gdbus call --session \
  --dest com.github.dennis.RecallBoard \
  --object-path /com/github/dennis/RecallBoard \
  --method org.freedesktop.Application.ActivateAction \
  'show' '[]' '{}'
```

## Architecture

The app runs as a daemon (`self.hold()` in `do_startup`). No window is shown on startup. Super+V triggers `org.freedesktop.Application.ActivateAction 'show'` via D-Bus, which calls `_on_show()` and creates a fresh window.

| File | Role |
|------|------|
| `src/main.py` | Entry point — sets up GI version requirements, creates and runs the app |
| `src/application.py` | `RecallBoardApplication` — daemon lifecycle, holds store and clipboard manager |
| `src/window.py` | `RecallBoardWindow` — popup UI, list, Escape/focus-dismiss |
| `src/clipboard_manager.py` | Monitors clipboard via GDK `changed` signal, stores new entries, notifies window |
| `src/history_store.py` | SQLite at `~/.local/share/recall-board/history.db`, deduplication |
| `src/keybinding.py` | Registers/unregisters Super+V as GNOME custom keybinding via gsettings |
| `src/autostart.py` | Writes/removes XDG autostart `.desktop` file in `~/.config/autostart/` |

## License

GPL-3.0-or-later

## Resources

- [PyGObject Documentation](https://amolenaar.pages.gitlab.gnome.org/pygobject-docs/)
- [GTK4 API Reference](https://docs.gtk.org/gtk4/)
- [libadwaita API Reference](https://gnome.pages.gitlab.gnome.org/libadwaita/doc/1-latest/)
- [GNOME Developer Documentation](https://developer.gnome.org/)

# Recall Board

A clipboard history manager for GNOME/Wayland. Press Super+V to browse and re-use previous clipboard entries.

## Development Setup

### System Dependencies (Ubuntu)
```bash
sudo apt install python3-gi gir1.2-gtk-4.0 gir1.2-adw-1 libadwaita-1-dev wl-clipboard meson ninja-build gettext git
```

### Verify Installation
```bash
python3 -c "import gi; gi.require_version('Gtk', '4.0'); gi.require_version('Adw', '1'); from gi.repository import Gtk, Adw; print('GTK', Gtk.get_major_version(), '- OK')"
```

## Project Structure
```
recall-board/
|--- src/
|   |--- main.py                # App source code
|   |--- application.py         # Entry point
|   |--- window.py              # Main popup window
|   |--- clipboard_manager.py   # Wayland clipboard listener
|   |--- history_store.py       # SQLite storage backend
|   |--- keybinding.py          # Global shortcut registration
|--- data/      # Desktop files, icons, schemas
|--- tests/     # Unit tests
|--- flatpak    # Flatpak build manifest
```

## License

GPL-3.0-or-later
EOF
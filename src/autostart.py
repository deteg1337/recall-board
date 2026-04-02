import sys
from pathlib import Path


_AUTOSTART_DIR = Path.home() / ".config" / "autostart"
_DESKTOP_FILE = _AUTOSTART_DIR / "com.github.dennis.RecallBoard.desktop"


def register_autostart():
    """Write an XDG autostart .desktop file so the daemon starts on login."""
    if _DESKTOP_FILE.exists():
        return

    main_py = (Path(__file__).parent / "main.py").resolve()
    exec_cmd = f"{sys.executable} {main_py}"

    _AUTOSTART_DIR.mkdir(parents=True, exist_ok=True)

    _DESKTOP_FILE.write_text(
        "[Desktop Entry]\n"
        "Type=Application\n"
        "Name=Recall Board\n"
        "Comment=Clipboard history manager\n"
        f"Exec={exec_cmd}\n"
        "Icon=edit-paste\n"
        "X-GNOME-Autostart-enabled=true\n"
        "NoDisplay=true\n"
    )


def unregister_autostart():
    """Remove the XDG autostart entry."""
    _DESKTOP_FILE.unlink(missing_ok=True)

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

import autostart as autostart_module
from autostart import register_autostart, unregister_autostart


@pytest.fixture(autouse=True)
def isolated_autostart_dir(tmp_path, monkeypatch):
    """Redirect autostart paths to a temporary directory for each test."""
    autostart_dir = tmp_path / ".config" / "autostart"
    desktop_file = autostart_dir / "com.github.dennis.RecallBoard.desktop"
    monkeypatch.setattr(autostart_module, "_AUTOSTART_DIR", autostart_dir)
    monkeypatch.setattr(autostart_module, "_DESKTOP_FILE", desktop_file)


def test_register_creates_desktop_file():
    register_autostart()
    assert autostart_module._DESKTOP_FILE.exists()


def test_register_creates_parent_dirs():
    register_autostart()
    assert autostart_module._AUTOSTART_DIR.is_dir()


def test_register_file_contains_required_keys():
    register_autostart()
    content = autostart_module._DESKTOP_FILE.read_text()
    assert "[Desktop Entry]" in content
    assert "Type=Application" in content
    assert "X-GNOME-Autostart-enabled=true" in content
    assert "NoDisplay=true" in content


def test_register_exec_points_to_main_py():
    register_autostart()
    content = autostart_module._DESKTOP_FILE.read_text()
    exec_line = next(l for l in content.splitlines() if l.startswith("Exec="))
    assert "main.py" in exec_line


def test_register_exec_uses_current_python():
    register_autostart()
    content = autostart_module._DESKTOP_FILE.read_text()
    exec_line = next(l for l in content.splitlines() if l.startswith("Exec="))
    assert sys.executable in exec_line


def test_register_is_idempotent(tmp_path):
    register_autostart()
    first_mtime = autostart_module._DESKTOP_FILE.stat().st_mtime

    register_autostart()
    second_mtime = autostart_module._DESKTOP_FILE.stat().st_mtime

    assert first_mtime == second_mtime


def test_unregister_removes_file():
    register_autostart()
    assert autostart_module._DESKTOP_FILE.exists()

    unregister_autostart()
    assert not autostart_module._DESKTOP_FILE.exists()


def test_unregister_when_not_registered_is_safe():
    unregister_autostart()  # file does not exist — must not raise

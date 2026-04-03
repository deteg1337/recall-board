from unittest.mock import MagicMock, patch

import pytest

from keybinding import register_shortcut, unregister_shortcut

_BASE = "/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings"
_OUR_PATH = f"{_BASE}/recall-board-toggle/"
_SCHEMA_KEYS = "org.gnome.settings-daemon.plugins.media-keys"


def _run_result(stdout):
    r = MagicMock()
    r.stdout = stdout
    return r


def _list_update_calls(mock_run):
    """Return gsettings set calls that update the custom-keybindings list."""
    return [
        c for c in mock_run.call_args_list
        if c[0][0][0] == "gsettings"
        and c[0][0][1] == "set"
        and c[0][0][2] == _SCHEMA_KEYS
        and c[0][0][3] == "custom-keybindings"
    ]


def test_register_when_list_is_empty():
    with patch("keybinding.subprocess.run") as mock_run:
        mock_run.return_value = _run_result("@as []")
        register_shortcut()

    updates = _list_update_calls(mock_run)
    assert updates, "custom-keybindings list was not updated"
    assert _OUR_PATH in updates[0][0][0][4]


def test_register_idempotent_when_already_present():
    existing = f"['{_OUR_PATH}']"
    with patch("keybinding.subprocess.run") as mock_run:
        mock_run.return_value = _run_result(existing)
        register_shortcut()

    assert _list_update_calls(mock_run) == []


def test_register_preserves_existing_entries():
    other = "/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/other/"
    existing = f"['{other}']"

    with patch("keybinding.subprocess.run") as mock_run:
        mock_run.return_value = _run_result(existing)
        register_shortcut()

    updates = _list_update_calls(mock_run)
    assert updates
    written = updates[0][0][0][4]
    assert other in written
    assert _OUR_PATH in written


def test_register_sets_name_command_binding():
    with patch("keybinding.subprocess.run") as mock_run:
        mock_run.return_value = _run_result("@as []")
        register_shortcut()

    binding_set_calls = [
        c[0][0] for c in mock_run.call_args_list
        if c[0][0][0] == "gsettings"
        and c[0][0][1] == "set"
        and c[0][0][2] != _SCHEMA_KEYS
    ]
    keys_set = {c[3] for c in binding_set_calls}
    assert "name" in keys_set
    assert "command" in keys_set
    assert "binding" in keys_set


def test_unregister_removes_our_path():
    existing = f"['{_OUR_PATH}']"

    with patch("keybinding.subprocess.run") as mock_run:
        mock_run.return_value = _run_result(existing)
        unregister_shortcut()

    updates = _list_update_calls(mock_run)
    assert updates
    assert _OUR_PATH not in updates[0][0][0][4]


def test_unregister_empty_list_uses_as_syntax():
    existing = f"['{_OUR_PATH}']"

    with patch("keybinding.subprocess.run") as mock_run:
        mock_run.return_value = _run_result(existing)
        unregister_shortcut()

    updates = _list_update_calls(mock_run)
    assert updates[0][0][0][4] == "@as []"


def test_unregister_when_not_present_is_idempotent():
    with patch("keybinding.subprocess.run") as mock_run:
        mock_run.return_value = _run_result("@as []")
        unregister_shortcut()

    assert _list_update_calls(mock_run) == []

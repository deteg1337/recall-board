from unittest.mock import MagicMock, patch

import pytest

from clipboard_manager import ClipboardManager


@pytest.fixture
def manager(store):
    return ClipboardManager(store)


def _make_run_result(stdout="", returncode=0):
    result = MagicMock()
    result.stdout = stdout
    result.returncode = returncode
    return result


def test_poll_new_content_is_stored(manager, store):
    with patch("clipboard_manager.subprocess.run") as mock_run:
        mock_run.return_value = _make_run_result("hello")
        manager._poll_clipboard()

    entries = store.get_all()
    assert len(entries) == 1
    assert entries[0]["content"] == "hello"


def test_poll_new_content_triggers_callback(manager):
    callback = MagicMock()
    manager.set_on_change(callback)

    with patch("clipboard_manager.subprocess.run") as mock_run:
        mock_run.return_value = _make_run_result("hello")
        manager._poll_clipboard()

    callback.assert_called_once()


def test_poll_same_content_is_ignored(manager, store):
    manager.last_content = "same"

    with patch("clipboard_manager.subprocess.run") as mock_run:
        mock_run.return_value = _make_run_result("same")
        manager._poll_clipboard()

    assert store.get_all() == []


def test_poll_same_content_does_not_trigger_callback(manager):
    manager.last_content = "same"
    callback = MagicMock()
    manager.set_on_change(callback)

    with patch("clipboard_manager.subprocess.run") as mock_run:
        mock_run.return_value = _make_run_result("same")
        manager._poll_clipboard()

    callback.assert_not_called()


def test_poll_empty_content_is_ignored(manager, store):
    with patch("clipboard_manager.subprocess.run") as mock_run:
        mock_run.return_value = _make_run_result("")
        manager._poll_clipboard()

    assert store.get_all() == []


def test_poll_nonzero_returncode_is_ignored(manager, store):
    with patch("clipboard_manager.subprocess.run") as mock_run:
        mock_run.return_value = _make_run_result("something", returncode=1)
        manager._poll_clipboard()

    assert store.get_all() == []


def test_poll_timeout_is_handled(manager):
    import subprocess

    with patch("clipboard_manager.subprocess.run") as mock_run:
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="wl-paste", timeout=1)
        manager._poll_clipboard()  # must not raise


def test_poll_missing_wl_paste_is_handled(manager):
    with patch("clipboard_manager.subprocess.run") as mock_run:
        mock_run.side_effect = FileNotFoundError
        manager._poll_clipboard()  # must not raise


def test_poll_returns_true_to_keep_timer(manager):
    with patch("clipboard_manager.subprocess.run") as mock_run:
        mock_run.return_value = _make_run_result("")
        result = manager._poll_clipboard()

    assert result is True


def test_poll_updates_last_content(manager):
    with patch("clipboard_manager.subprocess.run") as mock_run:
        mock_run.return_value = _make_run_result("new content")
        manager._poll_clipboard()

    assert manager.last_content == "new content"


def test_set_clipboard_calls_wl_copy(manager):
    mock_process = MagicMock()
    with patch("clipboard_manager.subprocess.Popen") as mock_popen:
        mock_popen.return_value = mock_process
        manager.set_clipboard("hello")

    mock_popen.assert_called_once()
    args = mock_popen.call_args[0][0]
    assert args == ["wl-copy"]
    mock_process.communicate.assert_called_once_with(input=b"hello")


def test_set_clipboard_updates_last_content(manager):
    mock_process = MagicMock()
    with patch("clipboard_manager.subprocess.Popen") as mock_popen:
        mock_popen.return_value = mock_process
        manager.set_clipboard("copied")

    assert manager.last_content == "copied"


def test_set_clipboard_missing_wl_copy_is_handled(manager):
    with patch("clipboard_manager.subprocess.Popen") as mock_popen:
        mock_popen.side_effect = FileNotFoundError
        manager.set_clipboard("hello")  # must not raise


def test_stop_removes_timer(manager):
    with patch("clipboard_manager.GLib.source_remove") as mock_remove:
        manager.timer_id = 42
        manager.stop()

    mock_remove.assert_called_once_with(42)
    assert manager.timer_id is None


def test_stop_when_not_started_is_safe(manager):
    manager.stop()  # timer_id is None — must not raise

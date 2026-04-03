from unittest.mock import MagicMock, patch

import pytest

from clipboard_manager import ClipboardManager


@pytest.fixture
def mock_clipboard():
    clipboard = MagicMock()
    display = MagicMock()
    display.get_clipboard.return_value = clipboard
    return clipboard, display


@pytest.fixture
def manager(store, mock_clipboard):
    clipboard, display = mock_clipboard
    with patch("clipboard_manager.Gdk.Display.get_default", return_value=display):
        m = ClipboardManager(store)
        m.start()
    return m, clipboard


# ── start / stop ───────────────────────────────────────────────────────────────

def test_start_connects_to_changed_signal(store, mock_clipboard):
    clipboard, display = mock_clipboard
    with patch("clipboard_manager.Gdk.Display.get_default", return_value=display):
        m = ClipboardManager(store)
        m.start()
    clipboard.connect.assert_called_once_with("changed", m._on_clipboard_changed)


def test_start_without_display_is_safe(store):
    with patch("clipboard_manager.Gdk.Display.get_default", return_value=None):
        m = ClipboardManager(store)
        m.start()  # must not raise
    assert m._clipboard is None


def test_stop_disconnects_signal(manager):
    m, clipboard = manager
    handler_id = m._handler_id  # save before stop() clears it
    m.stop()
    clipboard.disconnect.assert_called_once_with(handler_id)


def test_stop_clears_handler_id(manager):
    m, clipboard = manager
    m.stop()
    assert m._handler_id is None


def test_stop_when_not_started_is_safe(store):
    m = ClipboardManager(store)
    m.stop()  # never started — must not raise


# ── _on_clipboard_changed ──────────────────────────────────────────────────────

def test_on_clipboard_changed_requests_text_async(manager):
    m, clipboard = manager
    m._on_clipboard_changed(clipboard)
    clipboard.read_text_async.assert_called_once_with(None, m._on_text_received)


# ── _on_text_received ──────────────────────────────────────────────────────────

def test_new_content_is_stored(manager, store):
    m, clipboard = manager
    clipboard.read_text_finish.return_value = "hello"
    m._on_text_received(clipboard, MagicMock())

    entries = store.get_all()
    assert len(entries) == 1
    assert entries[0]["content"] == "hello"


def test_new_content_triggers_callback(manager):
    m, clipboard = manager
    callback = MagicMock()
    m.set_on_change(callback)

    clipboard.read_text_finish.return_value = "hello"
    m._on_text_received(clipboard, MagicMock())

    callback.assert_called_once()


def test_same_content_is_ignored(manager, store):
    m, clipboard = manager
    m._last_content = "same"
    clipboard.read_text_finish.return_value = "same"
    m._on_text_received(clipboard, MagicMock())

    assert store.get_all() == []


def test_same_content_does_not_trigger_callback(manager):
    m, clipboard = manager
    m._last_content = "same"
    callback = MagicMock()
    m.set_on_change(callback)

    clipboard.read_text_finish.return_value = "same"
    m._on_text_received(clipboard, MagicMock())

    callback.assert_not_called()


def test_empty_content_is_ignored(manager, store):
    m, clipboard = manager
    clipboard.read_text_finish.return_value = ""
    m._on_text_received(clipboard, MagicMock())

    assert store.get_all() == []


def test_none_content_is_ignored(manager, store):
    m, clipboard = manager
    clipboard.read_text_finish.return_value = None
    m._on_text_received(clipboard, MagicMock())

    assert store.get_all() == []


def test_read_exception_is_handled(manager):
    m, clipboard = manager
    clipboard.read_text_finish.side_effect = Exception("GLib error")
    m._on_text_received(clipboard, MagicMock())  # must not raise


def test_last_content_is_updated(manager):
    m, clipboard = manager
    clipboard.read_text_finish.return_value = "new content"
    m._on_text_received(clipboard, MagicMock())

    assert m._last_content == "new content"


# ── set_clipboard ──────────────────────────────────────────────────────────────

def test_set_clipboard_calls_wl_copy(manager):
    m, _ = manager
    mock_process = MagicMock()
    with patch("clipboard_manager.subprocess.Popen") as mock_popen:
        mock_popen.return_value = mock_process
        m.set_clipboard("hello")

    mock_popen.assert_called_once_with(["wl-copy"], stdin=-1)
    mock_process.communicate.assert_called_once_with(input=b"hello")


def test_set_clipboard_updates_last_content(manager):
    m, _ = manager
    mock_process = MagicMock()
    with patch("clipboard_manager.subprocess.Popen") as mock_popen:
        mock_popen.return_value = mock_process
        m.set_clipboard("copied")

    assert m._last_content == "copied"


def test_set_clipboard_missing_wl_copy_is_handled(manager):
    m, _ = manager
    with patch("clipboard_manager.subprocess.Popen") as mock_popen:
        mock_popen.side_effect = FileNotFoundError
        m.set_clipboard("hello")  # must not raise

from unittest.mock import MagicMock, patch

import pytest
from gi.repository import Gdk, GLib

from window import RecallBoardWindow


def _pump_events():
    ctx = GLib.MainContext.default()
    while ctx.pending():
        ctx.iteration(False)


@pytest.fixture
def window(app_with_store):
    win = RecallBoardWindow(application=app_with_store)
    yield win
    if not win.is_visible():
        return
    win.destroy()
    _pump_events()


def test_window_title(window):
    assert window.get_title() == "Recall Board"


def test_window_default_size(window):
    assert window.get_default_size() == (400, 500)


def test_refresh_list_empty_shows_placeholder(window):
    window.refresh_list()
    _pump_events()

    row = window.list_box.get_row_at_index(0)
    assert row is not None
    assert not hasattr(row, "entry_data")


def test_refresh_list_shows_entries(window, app_with_store):
    app_with_store.store.add("hello")
    app_with_store.store.add("world")
    window.refresh_list()
    _pump_events()

    row0 = window.list_box.get_row_at_index(0)
    row1 = window.list_box.get_row_at_index(1)
    assert row0 is not None
    assert row1 is not None
    assert row0.entry_data["content"] == "world"  # newest first
    assert row1.entry_data["content"] == "hello"


def test_refresh_list_clears_previous_rows(window, app_with_store):
    app_with_store.store.add("first")
    window.refresh_list()

    app_with_store.store.add("second")
    window.refresh_list()
    _pump_events()

    rows = []
    i = 0
    while row := window.list_box.get_row_at_index(i):
        if hasattr(row, "entry_data"):
            rows.append(row)
        i += 1
    assert len(rows) == 2


def test_refresh_list_schedules_focus_of_first_row(window, app_with_store):
    app_with_store.store.add("entry")
    with patch("window.GLib.idle_add") as mock_idle:
        window.refresh_list()
    mock_idle.assert_called_once_with(window._focus_first_row)


def test_refresh_list_empty_does_not_schedule_focus(window):
    with patch("window.GLib.idle_add") as mock_idle:
        window.refresh_list()
    mock_idle.assert_not_called()


def test_focus_first_row_selects_and_grabs_focus(window, app_with_store):
    app_with_store.store.add("entry")
    window.refresh_list()
    _pump_events()

    first_row = window.list_box.get_row_at_index(0)
    first_row.grab_focus = MagicMock()
    window.list_box.select_row = MagicMock()
    window._focus_first_row()

    window.list_box.select_row.assert_called_once_with(first_row)
    first_row.grab_focus.assert_called_once()


def test_focus_first_row_returns_false(window):
    result = window._focus_first_row()
    assert result is False


def test_create_row_label_text(window, app_with_store):
    app_with_store.store.add("test content")
    window.refresh_list()
    _pump_events()

    row = window.list_box.get_row_at_index(0)
    assert row.entry_data["content"] == "test content"


def test_create_row_height(window, app_with_store):
    app_with_store.store.add("row")
    window.refresh_list()
    _pump_events()

    row = window.list_box.get_row_at_index(0)
    assert row.get_size_request()[1] == 44


def test_row_activation_calls_set_clipboard(window, app_with_store):
    app_with_store.store.add("copy me")
    window.refresh_list()
    _pump_events()

    window.destroy = MagicMock()
    row = window.list_box.get_row_at_index(0)
    window._on_row_activated(window.list_box, row)

    app_with_store.clipboard_manager.set_clipboard.assert_called_once_with("copy me")


def test_row_activation_closes_window(window, app_with_store):
    app_with_store.store.add("copy me")
    window.refresh_list()
    _pump_events()

    window.destroy = MagicMock()
    row = window.list_box.get_row_at_index(0)
    window._on_row_activated(window.list_box, row)

    window.destroy.assert_called_once()


def test_row_activation_on_empty_state_row_is_safe(window):
    window.refresh_list()
    _pump_events()

    window.destroy = MagicMock()
    row = window.list_box.get_row_at_index(0)
    window._on_row_activated(window.list_box, row)
    window.destroy.assert_not_called()


def test_escape_key_closes_window(window):
    window.destroy = MagicMock()
    window._on_key_pressed(None, Gdk.KEY_Escape, 0, 0)
    window.destroy.assert_called_once()


def test_other_key_does_not_close_window(window):
    window.destroy = MagicMock()
    result = window._on_key_pressed(None, Gdk.KEY_a, 0, 0)

    window.destroy.assert_not_called()
    assert result is False


def test_focus_loss_schedules_timer(window):
    with patch("window.GLib.timeout_add") as mock_add:
        mock_add.return_value = 99
        with patch.object(window, "is_active", return_value=False):
            window._on_focus_changed(window, None)
    mock_add.assert_called_once()


def test_focus_regain_cancels_timer(window):
    window._focus_loss_timer = 42

    with patch("window.GLib.source_remove") as mock_remove:
        with patch.object(window, "is_active", return_value=True):
            window._on_focus_changed(window, None)

    mock_remove.assert_called_once_with(42)
    assert window._focus_loss_timer is None


def test_close_if_unfocused_destroys_when_inactive(window):
    window.destroy = MagicMock()

    with patch.object(window, "is_active", return_value=False):
        window._close_if_unfocused()

    window.destroy.assert_called_once()


def test_close_if_unfocused_keeps_window_when_active(window):
    window.destroy = MagicMock()

    with patch.object(window, "is_active", return_value=True):
        window._close_if_unfocused()

    window.destroy.assert_not_called()

from unittest.mock import MagicMock, patch

import pytest
from gi.repository import GLib

from application import RecallBoardApplication


@pytest.fixture
def app():
    """RecallBoardApplication with all external calls mocked.

    D-Bus registration is skipped so tests work without a session bus
    or a running instance of the app.
    """
    with (
        patch("application.HistoryStore") as mock_store_cls,
        patch("application.ClipboardManager") as mock_cm_cls,
        patch("application.register_shortcut"),
        patch("application.register_autostart"),
        patch.object(RecallBoardApplication, "register", return_value=True),
        patch("application.Adw.Application.do_startup"),
        patch("application.Adw.Application.do_shutdown"),
    ):
        mock_store_cls.return_value = MagicMock()
        mock_cm_cls.return_value = MagicMock()

        application = RecallBoardApplication()
        application.do_startup()
        yield application
        application.do_shutdown()


def test_startup_initializes_store(app):
    assert app.store is not None


def test_startup_initializes_clipboard_manager(app):
    assert app.clipboard_manager is not None


def test_startup_starts_clipboard_polling(app):
    app.clipboard_manager.start.assert_called_once()


def test_startup_registers_show_action(app):
    action = app.lookup_action("show")
    assert action is not None


def test_startup_calls_register_shortcut():
    with (
        patch("application.HistoryStore"),
        patch("application.ClipboardManager"),
        patch("application.register_shortcut") as mock_shortcut,
        patch("application.register_autostart"),
        patch.object(RecallBoardApplication, "register", return_value=True),
        patch("application.Adw.Application.do_startup"),
        patch("application.Adw.Application.do_shutdown"),
    ):
        application = RecallBoardApplication()
        application.do_startup()
        mock_shortcut.assert_called_once()
        application.do_shutdown()


def test_startup_calls_register_autostart():
    with (
        patch("application.HistoryStore"),
        patch("application.ClipboardManager"),
        patch("application.register_shortcut"),
        patch("application.register_autostart") as mock_autostart,
        patch.object(RecallBoardApplication, "register", return_value=True),
        patch("application.Adw.Application.do_startup"),
        patch("application.Adw.Application.do_shutdown"),
    ):
        application = RecallBoardApplication()
        application.do_startup()
        mock_autostart.assert_called_once()
        application.do_shutdown()


def test_on_show_creates_window(app):
    with patch("application.RecallBoardWindow") as mock_win_cls:
        mock_win = MagicMock()
        mock_win_cls.return_value = mock_win
        app._on_show(None, None)

    mock_win_cls.assert_called_once_with(application=app)
    mock_win.present.assert_called_once()


def test_on_show_calls_refresh_list(app):
    with patch("application.RecallBoardWindow") as mock_win_cls:
        mock_win = MagicMock()
        mock_win_cls.return_value = mock_win
        app._on_show(None, None)

    mock_win.refresh_list.assert_called_once()


def test_on_show_sets_on_change_callback(app):
    with patch("application.RecallBoardWindow") as mock_win_cls:
        mock_win = MagicMock()
        mock_win_cls.return_value = mock_win
        app._on_show(None, None)

    app.clipboard_manager.set_on_change.assert_called_once_with(mock_win.refresh_list)


def test_on_show_destroys_existing_window(app):
    old_window = MagicMock()
    with patch.object(app, "get_active_window", return_value=old_window):
        with patch("application.RecallBoardWindow") as mock_win_cls:
            mock_win_cls.return_value = MagicMock()
            app._on_show(None, None)

    old_window.destroy.assert_called_once()


def test_shutdown_stops_clipboard_manager(app):
    app.do_shutdown()
    app.clipboard_manager.stop.assert_called()


def test_shutdown_closes_store(app):
    app.do_shutdown()
    app.store.close.assert_called()

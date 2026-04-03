import sys
from pathlib import Path
from unittest.mock import MagicMock

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

import pytest
from gi.repository import Adw, Gio

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from history_store import HistoryStore


@pytest.fixture
def store():
    """In-memory HistoryStore — isolated per test."""
    s = HistoryStore(db_path=":memory:")
    yield s
    s.close()


@pytest.fixture(scope="session")
def gtk_app():
    """Minimal registered Adw.Application for widget tests."""
    app = Adw.Application(application_id="com.test.RecallBoard")
    app.register(None)
    yield app


@pytest.fixture
def app_with_store(gtk_app, store):
    """gtk_app with a fresh in-memory store and mock clipboard manager."""
    gtk_app.store = store
    gtk_app.clipboard_manager = MagicMock()
    return gtk_app

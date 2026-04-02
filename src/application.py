from gi.repository import Adw, Gio

from clipboard_manager import ClipboardManager
from history_store import HistoryStore
from window import RecallBoardWindow


class RecallBoardApplication(Adw.Application):
    def __init__(self):
        super().__init__(
            application_id="com.github.dennis.RecallBoard",
            flags=Gio.ApplicationFlags.FLAGS_NONE,
        )
        self.store = None
        self.clipboard_manager = None

    def do_activate(self):
        window = self.props.active_window
        if not window:
            # First launch — initialize everything
            self.store = HistoryStore()
            self.clipboard_manager = ClipboardManager(self.store)
            self.clipboard_manager.start()

            window = RecallBoardWindow(application=self)

        window.refresh_list()
        window.present()

    def do_shutdown(self):
        if self.clipboard_manager:
            self.clipboard_manager.stop()
        if self.store:
            self.store.close()
        Adw.Application.do_shutdown(self)
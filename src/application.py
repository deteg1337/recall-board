from gi.repository import Adw, Gio

from clipboard_manager import ClipboardManager
from history_store import HistoryStore
from keybinding import register_shortcut
from window import RecallBoardWindow


class RecallBoardApplication(Adw.Application):
    def __init__(self):
        super().__init__(
            application_id="com.github.dennis.RecallBoard",
            flags=Gio.ApplicationFlags.FLAGS_NONE,
        )
        self.store = None
        self.clipboard_manager = None

    def do_startup(self):
        Adw.Application.do_startup(self)
        self.store = HistoryStore()
        self.clipboard_manager = ClipboardManager(self.store)
        self.clipboard_manager.start()

        # Register "show" action — this is what Super+V triggers
        show_action = Gio.SimpleAction.new("show", None)
        show_action.connect("activate", self._on_show)
        self.add_action(show_action)

        register_shortcut()
        self.hold()

    def do_activate(self):
        # Daemon mode — app starts silently in the background
        # Window is shown via the "show" action (Super+V)
        pass

    def _on_show(self, action, param):
        old = self.props.active_window
        if old:
            old.destroy()

        window = RecallBoardWindow(application=self)
        self.clipboard_manager.set_on_change(window.refresh_list)
        window.refresh_list()
        window.present()

    def do_shutdown(self):
        if self.clipboard_manager:
            self.clipboard_manager.stop()
        if self.store:
            self.store.close()
        Adw.Application.do_shutdown(self)
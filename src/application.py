from gi.repository import Adw, Gio

from window import RecallBoardWindow


class RecallBoardApplication(Adw.Application):
    def __init__(self):
        super().__init__(
            application_id="com.github.deteg1337.RecallBoard",
            flags=Gio.ApplicationFlags.FLAGS_NONE,
        )

    def do_activate(self):
        window = RecallBoardWindow(application=self)
        window.present()
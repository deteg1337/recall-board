from gi.repository import Adw, Gtk


class RecallBoardWindow(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_title("Recall Board")
        self.set_default_size(400, 500)

        # Header bar
        header = Adw.HeaderBar()

        # Main layout
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        content.append(header)

        self.set_content(content)
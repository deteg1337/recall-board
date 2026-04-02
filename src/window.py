from gi.repository import Adw, Gtk


class RecallBoardWindow(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_title("Recall Board")
        self.set_default_size(400, 500)

        # Header bar
        header = Adw.HeaderBar()

        # Scrollable list area
        self.list_box = Gtk.ListBox()
        self.list_box.set_selection_mode(Gtk.SelectionMode.NONE)
        self.list_box.add_css_class("boxed-list")
        self.list_box.connect("row-activated", self._on_row_activated)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_child(self.list_box)

        # Wrap list in margins
        clamp = Adw.Clamp()
        clamp.set_maximum_size(500)
        clamp.set_child(scrolled)

        # Main layout
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        content.append(header)
        content.append(clamp)

        self.set_content(content)

    def refresh_list(self):
        while row := self.list_box.get_row_at_index(0):
            self.list_box.remove(row)

        store = self.get_application().store
        entries = store.get_all()

        if not entries:
            label = Gtk.Label(label="Clipboard history is empty")
            label.add_css_class("dim-label")
            label.set_margin_top(24)
            label.set_margin_bottom(24)
            self.list_box.append(label)
            return

        for entry in entries:
            row = self._create_row(entry)
            self.list_box.append(row)

    def _create_row(self, entry):
        label = Gtk.Label(label=entry["content"])
        label.set_xalign(0)
        label.set_ellipsize(3)  # PANGO_ELLIPSIZE_END
        label.set_max_width_chars(50)
        label.set_single_line_mode(True)

        label.set_margin_top(8)
        label.set_margin_bottom(8)
        label.set_margin_start(12)
        label.set_margin_end(12)

        row = Gtk.ListBoxRow()
        row.set_size_request(-1, 44)
        row.set_child(label)
        row.entry_data = entry

        return row

    def _on_row_activated(self, list_box, row):
        if not hasattr(row, "entry_data"):
            return

        content = row.entry_data["content"]
        app = self.get_application()
        app.clipboard_manager.set_clipboard(content)
        self.close()
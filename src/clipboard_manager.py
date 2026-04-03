import subprocess

from gi.repository import Gdk


class ClipboardManager:
    def __init__(self, history_store):
        self.store = history_store
        self._clipboard = None
        self._handler_id = None
        self._last_content = ""
        self.on_change_callback = None

    def start(self):
        display = Gdk.Display.get_default()
        if display is None:
            return
        self._clipboard = display.get_clipboard()
        self._handler_id = self._clipboard.connect("changed", self._on_clipboard_changed)

    def stop(self):
        if self._clipboard is not None and self._handler_id is not None:
            self._clipboard.disconnect(self._handler_id)
            self._handler_id = None

    def set_on_change(self, callback):
        self.on_change_callback = callback

    def _on_clipboard_changed(self, clipboard):
        clipboard.read_text_async(None, self._on_text_received)

    def _on_text_received(self, clipboard, result):
        try:
            text = clipboard.read_text_finish(result)
        except Exception:
            return

        if not text or text == self._last_content:
            return

        self._last_content = text
        self.store.add(text)

        if self.on_change_callback:
            self.on_change_callback()

    def set_clipboard(self, content):
        try:
            process = subprocess.Popen(["wl-copy"], stdin=subprocess.PIPE)
            process.communicate(input=content.encode())
            self._last_content = content
        except FileNotFoundError:
            pass

import subprocess

from gi.repository import GLib


class ClipboardManager:
    def __init__(self, history_store):
        self.store = history_store
        self.last_content = ""
        self.timer_id = None
        self.on_change_callback = None

    def start(self):
        self.timer_id = GLib.timeout_add(500, self._poll_clipboard)

    def stop(self):
        if self.timer_id is not None:
            GLib.source_remove(self.timer_id)
            self.timer_id = None

    def set_on_change(self, callback):
        self.on_change_callback = callback

    def _poll_clipboard(self):
        try:
            result = subprocess.run(
                ["wl-paste", "--no-newline"],
                capture_output=True,
                text=True,
                timeout=1,
            )

            content = result.stdout

            if result.returncode == 0 and content and content != self.last_content:
                self.last_content = content
                self.store.add(content)

                if self.on_change_callback:
                    self.on_change_callback()

        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        return True

    def set_clipboard(self, content):
        try:
            process = subprocess.Popen(
                ["wl-copy"],
                stdin=subprocess.PIPE,
            )
            process.communicate(input=content.encode())
            self.last_content = content
        except FileNotFoundError:
            pass
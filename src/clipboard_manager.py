import subprocess

from gi.repository import GLib


class ClipboardManager:
    def __init__(self, history_store):
        self.store = history_store
        self.last_content = ""
        self.timer_id = None

    def start(self):
        # Check clipboard every 500ms
        self.timer_id = GLib.timeout_add(500, self._poll_clipboard)

    def stop(self):
        if self.timer_id is not None:
            GLib.source_remove(self.timer_id)
            self.timer_id = None

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

        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        # Return True to keep the timer running
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
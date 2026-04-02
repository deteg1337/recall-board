import subprocess


def register_shortcut():
    """Register Super+V as a custom GNOME shortcut to launch Recall Board."""

    name = "recall-board-toggle"
    command = (
            "gdbus call --session"
            " --dest com.github.dennis.RecallBoard"
            " --object-path /com/github/dennis/RecallBoard"
            " --method org.freedesktop.Application.ActivateAction"
            " 'show' '[]' '{}'"
        )
    binding = "<Super>v"

    result = subprocess.run(
        [
            "gsettings", "get",
            "org.gnome.settings-daemon.plugins.media-keys",
            "custom-keybindings",
        ],
        capture_output=True,
        text=True,
    )

    current = result.stdout.strip()

    base_path = "/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings"
    our_path = f"{base_path}/{name}/"

    if our_path in current:
        return

    if current == "@as []":
        new_list = f"['{our_path}']"
    else:
        entries = current.strip("[]").split(", ")
        entries.append(f"'{our_path}'")
        new_list = f"[{', '.join(entries)}]"

    schema = (
        f"org.gnome.settings-daemon.plugins.media-keys"
        f".custom-keybinding:{our_path}"
    )

    subprocess.run(["gsettings", "set", schema, "name", name])
    subprocess.run(["gsettings", "set", schema, "command", command])
    subprocess.run(["gsettings", "set", schema, "binding", binding])

    subprocess.run([
        "gsettings", "set",
        "org.gnome.settings-daemon.plugins.media-keys",
        "custom-keybindings",
        new_list,
    ])


def unregister_shortcut():
    """Remove the custom GNOME shortcut."""

    name = "recall-board-toggle"
    base_path = "/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings"
    our_path = f"{base_path}/{name}/"

    result = subprocess.run(
        [
            "gsettings", "get",
            "org.gnome.settings-daemon.plugins.media-keys",
            "custom-keybindings",
        ],
        capture_output=True,
        text=True,
    )

    current = result.stdout.strip()

    if our_path not in current:
        return

    entries = current.strip("[]").split(", ")
    entries = [e for e in entries if our_path not in e]

    if entries:
        new_list = f"[{', '.join(entries)}]"
    else:
        new_list = "@as []"

    schema = (
        f"org.gnome.settings-daemon.plugins.media-keys"
        f".custom-keybinding:{our_path}"
    )
    subprocess.run(["gsettings", "reset-recursively", schema])

    subprocess.run([
        "gsettings", "set",
        "org.gnome.settings-daemon.plugins.media-keys",
        "custom-keybindings",
        new_list,
    ])
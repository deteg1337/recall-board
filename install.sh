#!/usr/bin/env bash
set -euo pipefail

APP_ID="com.github.dennis.RecallBoard"
INSTALL_DIR="$HOME/.local/share/recall-board"
BIN_DIR="$HOME/.local/bin"
APPLICATIONS_DIR="$HOME/.local/share/applications"

# ── Colours ────────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
info()    { echo -e "${GREEN}[recall-board]${NC} $*"; }
warning() { echo -e "${YELLOW}[recall-board]${NC} $*"; }
error()   { echo -e "${RED}[recall-board]${NC} $*" >&2; exit 1; }

# ── Pre-flight checks ──────────────────────────────────────────────────────────
[[ "$XDG_SESSION_TYPE" == "wayland" ]] \
    || warning "Wayland session not detected — clipboard monitoring may not work."

python3 -c "import gi" 2>/dev/null \
    || error "python3-gi not found. Run: sudo apt install python3-gi"

python3 -c "
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw
" 2>/dev/null \
    || error "GTK4/libadwaita not found. Run: sudo apt install gir1.2-gtk-4.0 gir1.2-adw-1"

command -v wl-copy >/dev/null \
    || error "wl-clipboard not found. Run: sudo apt install wl-clipboard"

# ── Install ────────────────────────────────────────────────────────────────────
info "Installing to $INSTALL_DIR ..."

mkdir -p "$INSTALL_DIR" "$BIN_DIR" "$APPLICATIONS_DIR"

cp -r src/* "$INSTALL_DIR/"

# Launcher script
cat > "$BIN_DIR/recall-board" <<EOF
#!/usr/bin/env bash
exec python3 "$INSTALL_DIR/main.py" "\$@"
EOF
chmod +x "$BIN_DIR/recall-board"

# .desktop file for app launcher / GNOME search
cat > "$APPLICATIONS_DIR/$APP_ID.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Recall Board
Comment=Clipboard history manager
Exec=$BIN_DIR/recall-board
Icon=edit-paste
Categories=Utility;
Keywords=clipboard;history;paste;
StartupNotify=false
NoDisplay=true
EOF

# ── Start the daemon ───────────────────────────────────────────────────────────
if [[ "${RECALL_BOARD_NO_START:-}" != "1" ]]; then
    info "Starting daemon (registers Super+V shortcut and autostart) ..."
    if "$BIN_DIR/recall-board" & sleep 1; then
        info "Daemon started."
    else
        warning "Could not start daemon — no Wayland session? Run 'recall-board' manually after login."
    fi
fi

info "Done."
echo ""
echo "  Press Super+V to open Recall Board."
echo "  The app will start automatically on login."
echo ""

# ── PATH hint ─────────────────────────────────────────────────────────────────
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    warning "$BIN_DIR is not in your PATH."
    echo "  Add this to your ~/.bashrc or ~/.zshrc:"
    echo "    export PATH=\"\$HOME/.local/bin:\$PATH\""
fi

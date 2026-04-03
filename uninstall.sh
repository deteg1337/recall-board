#!/usr/bin/env bash
set -euo pipefail

APP_ID="com.github.dennis.RecallBoard"
INSTALL_DIR="$HOME/.local/share/recall-board"
BIN_DIR="$HOME/.local/bin"
APPLICATIONS_DIR="$HOME/.local/share/applications"
AUTOSTART_DIR="$HOME/.config/autostart"

GREEN='\033[0;32m'; NC='\033[0m'
info() { echo -e "${GREEN}[recall-board]${NC} $*"; }

# Stop running daemon
if pgrep -f "recall-board/main.py" >/dev/null 2>&1; then
    info "Stopping daemon ..."
    pkill -f "recall-board/main.py" || true
fi

# Unregister Super+V keybinding
if [[ -d "$INSTALL_DIR" ]]; then
    info "Unregistering Super+V shortcut ..."
    python3 - <<EOF 2>/dev/null || true
import sys
sys.path.insert(0, "$INSTALL_DIR")
from keybinding import unregister_shortcut
unregister_shortcut()
EOF
fi

# Remove files
info "Removing files ..."
rm -rf "$INSTALL_DIR"
rm -f  "$BIN_DIR/recall-board"
rm -f  "$APPLICATIONS_DIR/$APP_ID.desktop"
rm -f  "$AUTOSTART_DIR/$APP_ID.desktop"

info "Recall Board has been uninstalled."

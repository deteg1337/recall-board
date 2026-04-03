#!/usr/bin/env bats
# Tests for install.sh and uninstall.sh
# Runs with a fake HOME so nothing touches the real system.

setup() {
    export HOME="$BATS_TEST_TMPDIR"
    export RECALL_BOARD_NO_START=1

    # Fake PATH entries so dependency checks pass
    local fake_bin="$BATS_TEST_TMPDIR/fake-bin"
    mkdir -p "$fake_bin"

    # Fake wl-paste and wl-copy
    printf '#!/usr/bin/env bash\nexit 0\n' > "$fake_bin/wl-paste"
    printf '#!/usr/bin/env bash\nexit 0\n' > "$fake_bin/wl-copy"
    chmod +x "$fake_bin/wl-paste" "$fake_bin/wl-copy"

    # Fake wtype
    printf '#!/usr/bin/env bash\nexit 0\n' > "$fake_bin/wtype"
    chmod +x "$fake_bin/wtype"

    # Fake python3 that passes gi/GTK/Adw import checks
    cat > "$fake_bin/python3" <<'EOF'
#!/usr/bin/env bash
# Pass all -c checks silently; delegate everything else to real python3
if [[ "$1" == "-c" ]]; then
    exit 0
fi
exec /usr/bin/python3 "$@"
EOF
    chmod +x "$fake_bin/python3"

    export PATH="$fake_bin:$PATH"

    # Fake a Wayland session so the Wayland warning is suppressed
    export XDG_SESSION_TYPE=wayland

    REPO_ROOT="$(cd "$BATS_TEST_DIRNAME/.." && pwd)"
}

# ── install.sh ─────────────────────────────────────────────────────────────────

@test "install creates app directory" {
    run bash "$REPO_ROOT/install.sh"
    [ -d "$HOME/.local/share/recall-board" ]
}

@test "install copies source files" {
    run bash "$REPO_ROOT/install.sh"
    [ -f "$HOME/.local/share/recall-board/main.py" ]
    [ -f "$HOME/.local/share/recall-board/application.py" ]
    [ -f "$HOME/.local/share/recall-board/window.py" ]
}

@test "install creates executable launcher" {
    run bash "$REPO_ROOT/install.sh"
    [ -f "$HOME/.local/bin/recall-board" ]
    [ -x "$HOME/.local/bin/recall-board" ]
}

@test "launcher points to installed main.py" {
    run bash "$REPO_ROOT/install.sh"
    grep -q "recall-board/main.py" "$HOME/.local/bin/recall-board"
}

@test "install creates .desktop file" {
    run bash "$REPO_ROOT/install.sh"
    [ -f "$HOME/.local/share/applications/com.github.dennis.RecallBoard.desktop" ]
}

@test ".desktop file has required keys" {
    run bash "$REPO_ROOT/install.sh"
    local desktop="$HOME/.local/share/applications/com.github.dennis.RecallBoard.desktop"
    grep -q "Type=Application"  "$desktop"
    grep -q "Name=Recall Board" "$desktop"
    grep -q "Exec="              "$desktop"
}

@test "install exits 0" {
    run bash "$REPO_ROOT/install.sh"
    [ "$status" -eq 0 ]
}

@test "install is idempotent" {
    bash "$REPO_ROOT/install.sh"
    run bash "$REPO_ROOT/install.sh"
    [ "$status" -eq 0 ]
}

# ── uninstall.sh ───────────────────────────────────────────────────────────────

@test "uninstall removes app directory" {
    bash "$REPO_ROOT/install.sh"
    run bash "$REPO_ROOT/uninstall.sh"
    [ ! -d "$HOME/.local/share/recall-board" ]
}

@test "uninstall removes launcher" {
    bash "$REPO_ROOT/install.sh"
    run bash "$REPO_ROOT/uninstall.sh"
    [ ! -f "$HOME/.local/bin/recall-board" ]
}

@test "uninstall removes .desktop file" {
    bash "$REPO_ROOT/install.sh"
    run bash "$REPO_ROOT/uninstall.sh"
    [ ! -f "$HOME/.local/share/applications/com.github.dennis.RecallBoard.desktop" ]
}

@test "uninstall exits 0" {
    bash "$REPO_ROOT/install.sh"
    run bash "$REPO_ROOT/uninstall.sh"
    [ "$status" -eq 0 ]
}

@test "uninstall without prior install is safe" {
    run bash "$REPO_ROOT/uninstall.sh"
    [ "$status" -eq 0 ]
}

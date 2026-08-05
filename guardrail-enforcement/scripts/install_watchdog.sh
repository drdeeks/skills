#!/usr/bin/env bash
# install_watchdog.sh -- generate + install a system-level systemd service
# that runs watchdog.sh (which itself self-resolves the skills repo root
# and scan interval -- see watchdog.sh's own header). The ONE thing that
# must be concrete is the systemd unit's ExecStart path; everything it
# points at is resolved dynamically at watchdog.sh's own runtime, not
# baked into this installer's source (FOREVER-SYSTEM.md Sec 2).
#
# System-level (root, /etc/systemd/system) by explicit choice: matches this
# machine's existing convention (see openclaw-gateway.service) and survives
# regardless of whether the target user is logged in.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
WATCHDOG="$SCRIPT_DIR/watchdog.sh"
UNIT_NAME="guardrail-watchdog.service"
UNIT_PATH="/etc/systemd/system/$UNIT_NAME"
TARGET_USER="${GUARDRAIL_WATCHDOG_USER:-$(id -un)}"

usage() {
    cat <<EOF
usage: install_watchdog.sh [--help] [--dry-run] [--uninstall] [--user NAME]

Installs (or removes) a system-level systemd service that keeps
watchdog.sh running: it scans for skill version bumps on an interval and
auto-commits them, restarting automatically on crash and on boot.

Requires sudo (writes to /etc/systemd/system/).

Options:
  --user NAME   Run the service as this user (default: whoever invokes this
                script, currently resolves to '$TARGET_USER'; override with
                \$GUARDRAIL_WATCHDOG_USER too).
  --dry-run     Print the unit file and the commands that would run; touch
                nothing.
  --uninstall   Stop, disable, and remove the service.
  --help        Show this help message.

Environment forwarded into the service (see watchdog.sh --help):
  GUARDRAIL_SKILLS_ROOT, GUARDRAIL_SCAN_INTERVAL
EOF
}

DRY_RUN=false
UNINSTALL=false
while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help) usage; exit 0 ;;
        --dry-run) DRY_RUN=true; shift ;;
        --uninstall) UNINSTALL=true; shift ;;
        --user) TARGET_USER="${2:?--user needs a name}"; shift 2 ;;
        *) echo "error: unrecognized argument: $1" >&2; usage >&2; exit 2 ;;
    esac
done

run() {
    if $DRY_RUN; then
        echo "[DRY RUN] $*"
    else
        "$@"
    fi
}

if $UNINSTALL; then
    echo "Uninstalling $UNIT_NAME ..."
    run sudo systemctl stop "$UNIT_NAME" || true
    run sudo systemctl disable "$UNIT_NAME" || true
    run sudo rm -f "$UNIT_PATH"
    run sudo systemctl daemon-reload
    echo "Done."
    exit 0
fi

if [[ ! -x "$WATCHDOG" ]]; then
    echo "error: $WATCHDOG not found or not executable" >&2
    exit 1
fi

UNIT_CONTENT="$(cat <<EOF
[Unit]
Description=Guardrail watcher watchdog (auto-commit skill version bumps)
Documentation=file://$SKILLS_ROOT/guardrail-enforcement/SKILL.md
After=network.target

[Service]
Type=simple
User=$TARGET_USER
ExecStart=$WATCHDOG
Restart=always
RestartSec=10
Environment=GUARDRAIL_SKILLS_ROOT=$SKILLS_ROOT

[Install]
WantedBy=multi-user.target
EOF
)"

echo "Skills root:  $SKILLS_ROOT"
echo "Watchdog:     $WATCHDOG"
echo "Run as user:  $TARGET_USER"
echo "Unit path:    $UNIT_PATH"
echo
echo "--- unit file ---"
echo "$UNIT_CONTENT"
echo "-----------------"

if $DRY_RUN; then
    echo "[DRY RUN] would write the above to $UNIT_PATH, then:"
    echo "[DRY RUN]   sudo systemctl daemon-reload"
    echo "[DRY RUN]   sudo systemctl enable $UNIT_NAME"
    echo "[DRY RUN]   sudo systemctl start $UNIT_NAME"
    exit 0
fi

echo "$UNIT_CONTENT" | sudo tee "$UNIT_PATH" >/dev/null
sudo systemctl daemon-reload
sudo systemctl enable "$UNIT_NAME"
sudo systemctl start "$UNIT_NAME"

echo
echo "Installed and started. Check with:"
echo "  systemctl status $UNIT_NAME"
echo "  journalctl -u $UNIT_NAME -f"

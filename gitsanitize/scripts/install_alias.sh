#!/usr/bin/env bash
# Optional convenience only. Neither gitsanitize.py nor sanitize.py ever
# requires this to run -- `python3 scripts/sanitize.py <args>` already
# works with zero setup.
#
# This offers to add TWO alias lines to your shell rc:
#   gitsanitize   full interface: --repo PATH, every subcommand and flag
#   sanitize      short front door: sanitize [path] [subcommand...], path
#                 defaults to the current directory, verifies it's a real
#                 git repo first
#
# It asks before touching anything, tells you exactly what lines it's
# adding and to which file, and does nothing if you say no.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GS_ENTRY="$HERE/gitsanitize.py"
SAN_ENTRY="$HERE/sanitize.py"
GS_ALIAS="alias gitsanitize='python3 \"$GS_ENTRY\"'"
SAN_ALIAS="alias sanitize='python3 \"$SAN_ENTRY\"'"

case "${1:-}" in
    -h|--help)
        cat <<USAGE
usage: install_alias.sh [-h|--help]

Optional convenience only -- neither gitsanitize.py nor sanitize.py
requires this to run. Offers to add two alias lines to your shell rc file:
'gitsanitize' (full interface) and 'sanitize' (short, path-first front
door). Asks before touching anything; run with no arguments to actually
use it.
USAGE
        exit 0
        ;;
esac

if [ ! -f "$GS_ENTRY" ] || [ ! -f "$SAN_ENTRY" ]; then
    echo "error: expected to find gitsanitize.py and sanitize.py next to this script in $HERE" >&2
    exit 1
fi

echo "This adds TWO lines to your shell rc file:"
echo
echo "  $GS_ALIAS"
echo "  $SAN_ALIAS"
echo
echo "'gitsanitize' is the full interface (--repo PATH, any subcommand)."
echo "'sanitize' is the short form: sanitize [path] [subcommand...],"
echo "defaulting to the current directory when no path is given."
echo

RC="${SHELL_RC:-}"
if [ -z "$RC" ]; then
    case "$(basename "${SHELL:-bash}")" in
        zsh) RC="$HOME/.zshrc" ;;
        *)   RC="$HOME/.bashrc" ;;
    esac
fi

read -r -p "Add them to $RC now? [y/N] " ans
case "$ans" in
    y|Y|yes|Yes) ;;
    *)
        echo "Not touching anything. Both scripts still work directly:"
        echo "  python3 $GS_ENTRY <command>"
        echo "  python3 $SAN_ENTRY [path] [command]"
        exit 0
        ;;
esac

added=0
for pair in "$GS_ALIAS" "$SAN_ALIAS"; do
    if [ -f "$RC" ] && grep -qF "$pair" "$RC"; then
        continue
    fi
    printf '\n# gitsanitize / sanitize (added by install_alias.sh, self-contained skill copy)\n%s\n' \
        "$pair" >> "$RC"
    added=$((added + 1))
done

if [ "$added" -eq 0 ]; then
    echo "Already present in $RC -- nothing to do."
else
    echo "Added $added new alias line(s) to $RC. Restart your shell, or run: source $RC"
fi

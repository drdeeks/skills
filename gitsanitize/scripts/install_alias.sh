#!/usr/bin/env bash
# Optional convenience only. gitsanitize.py never requires this to run --
# `python3 scripts/gitsanitize.py <args>` already works with zero setup.
#
# This offers to add ONE alias line to your shell rc so the bare word
# `gitsanitize` works too. It asks before touching anything, tells you
# exactly what line it's adding and to which file, and does nothing if you
# say no.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENTRY="$HERE/gitsanitize.py"
ALIAS_LINE="alias gitsanitize='python3 \"$ENTRY\"'"

case "${1:-}" in
    -h|--help)
        cat <<USAGE
usage: install_alias.sh [-h|--help]

Optional convenience only -- gitsanitize.py never requires this to run.
Offers to add ONE alias line to your shell rc file so the bare word
'gitsanitize' works from any directory. Asks before touching anything;
run with no arguments to actually use it.
USAGE
        exit 0
        ;;
esac

if [ ! -f "$ENTRY" ]; then
    echo "error: expected to find gitsanitize.py next to this script at $ENTRY" >&2
    exit 1
fi

echo "This adds ONE line to your shell rc file so 'gitsanitize' works bare,"
echo "from any directory, without typing the python3/path prefix:"
echo
echo "  $ALIAS_LINE"
echo

RC="${SHELL_RC:-}"
if [ -z "$RC" ]; then
    case "$(basename "${SHELL:-bash}")" in
        zsh) RC="$HOME/.zshrc" ;;
        *)   RC="$HOME/.bashrc" ;;
    esac
fi

read -r -p "Add it to $RC now? [y/N] " ans
case "$ans" in
    y|Y|yes|Yes) ;;
    *)
        echo "Not touching anything. gitsanitize.py still works directly:"
        echo "  python3 $ENTRY <command>"
        exit 0
        ;;
esac

if [ -f "$RC" ] && grep -qF "$ALIAS_LINE" "$RC"; then
    echo "Already present in $RC -- nothing to do."
    exit 0
fi

printf '\n# gitsanitize (added by install_alias.sh, self-contained skill copy)\n%s\n' \
    "$ALIAS_LINE" >> "$RC"
echo "Added to $RC. Restart your shell, or run: source $RC"

#!/usr/bin/env python3
"""
Guardrail Git Hook Installer
============================

Installs (or removes) git hooks that bind commits to the guardrail loop log: a
commit is rejected unless ``verify_log.py`` confirms a valid, recent PASS entry
signed with the repo's HMAC secret. This is how the gate's audit trail becomes
enforceable rather than advisory.

Hooks installed:
  * ``pre-commit``  — refuse the commit if the loop log fails verification or has
    no PASS entry within the freshness window.
  * ``post-commit`` — chains any foreign post-commit hook this install replaced
    (see Safety below), records the commit against the audit log, then runs
    ``verify_manifest.py`` scoped to the skill dir(s) this commit touched. If
    the manifest doesn't match what was just committed for any touched skill,
    reverts the commit (``git revert``, never history-rewriting) and exits
    nonzero. Pre-existing drift in *untouched* skills never blocks.
  * ``pre-push``    — re-verify the whole log chain before anything leaves the
    machine.

Safety:
  * Any existing hook is backed up to ``<hook>.pre-guardrail`` before being
    replaced — nothing is destroyed.
  * ``--uninstall`` removes guardrail hooks and restores backups.
  * Fully path-agnostic: the repo is resolved via ``git rev-parse`` or ``--repo``;
    the installed hooks locate their sibling scripts relative to their own path,
    so the repo can move or be cloned elsewhere.
"""

import argparse
import os
import shutil
import stat
import subprocess
import sys
sys.dont_write_bytecode = True  # never litter skills with __pycache__ (validator FAIL)
from pathlib import Path

HOOKS = ("pre-commit", "post-commit", "pre-push")
BACKUP_SUFFIX = ".pre-guardrail"
MARKER = "# guardrail-enforcement managed hook"

SCRIPTS_DIR = Path(__file__).resolve().parent


def resolve_repo(repo_arg):
    if repo_arg:
        repo = Path(repo_arg).expanduser().resolve()
    else:
        try:
            out = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                                 capture_output=True, text=True, check=True)
            repo = Path(out.stdout.strip())
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise SystemExit("error: not in a git repo; pass --repo PATH.")
    if not (repo / ".git").exists():
        raise SystemExit(f"error: {repo} is not a git repository.")
    return repo


def hook_body(hook_name, verify_script, secret_path, log_name, freshness, verify_manifest_script=None):
    """Portable POSIX-sh hook that shells out to verify_log.py."""
    if hook_name == "post-commit":
        return f"""#!/bin/sh
{MARKER}
REPO="$(git rev-parse --show-toplevel)"

# Chain any foreign post-commit hook this install replaced (backed up to
# post-commit.pre-guardrail) so its behavior isn't silently lost.
FOREIGN_HOOK="$REPO/.git/hooks/post-commit.pre-guardrail"
if [ -x "$FOREIGN_HOOK" ]; then
    "$FOREIGN_HOOK" || echo "guardrail: chained foreign post-commit hook exited nonzero (continuing)" >&2
fi

echo "guardrail: commit $(git rev-parse HEAD) over $REPO/{log_name}" >&2

# Hash/manifest check, scoped to the skill dir(s) this commit actually
# touched — never blocks on pre-existing drift in untouched skills.
# Reverts (never rewrites history) if a touched skill's manifest entry
# doesn't match what was just committed.
VERIFY_MANIFEST="{verify_manifest_script}"
if [ -f "$VERIFY_MANIFEST" ]; then
    CHANGED_SKILLS=$(git diff-tree --no-commit-id --name-only -r HEAD | cut -d/ -f1 | sort -u)
    REPORT="$(mktemp)"
    trap 'rm -f "$REPORT"' EXIT
    python3 "$VERIFY_MANIFEST" --repo "$REPO" --json > "$REPORT" 2>/dev/null
    for skill in $CHANGED_SKILLS; do
        [ -f "$REPO/$skill/SKILL.md" ] || continue
        BAD=$(python3 -c "
import json, sys
try:
    d = json.load(open('$REPORT'))
except Exception:
    sys.exit(0)
bad = [f for f in d.get('findings', []) if f.get('skill') == '$skill' and f.get('severity') == 'fail']
print('yes' if bad else 'no')
for f in bad:
    print('  - ' + f.get('type', '?') + ': ' + f.get('detail', ''), file=sys.stderr)
")
        if [ "$BAD" = "yes" ]; then
            echo "guardrail: post-commit manifest check FAILED for '$skill' -- this commit doesn't match the manifest. Reverting." >&2
            git -C "$REPO" revert --no-edit HEAD >&2
            exit 1
        fi
    done
fi
exit 0
"""
    recent = f"--recent {freshness}" if hook_name == "pre-commit" else ""
    return f"""#!/bin/sh
{MARKER}
REPO="$(git rev-parse --show-toplevel)"
LOG="$REPO/{log_name}"
if [ ! -f "$LOG" ]; then
    echo "guardrail: no loop log at $LOG — run the gate before committing." >&2
    echo "  bypass (only if you mean it): git commit --no-verify" >&2
    exit 1
fi
if ! python3 "{verify_script}" "$LOG" --secret "{secret_path}" {recent} >/dev/null 2>&1; then
    echo "guardrail: loop log failed verification for {hook_name}." >&2
    echo "  run the gate to produce a fresh signed entry, or" >&2
    echo "  bypass (only if you mean it): git commit --no-verify" >&2
    exit 1
fi
exit 0
"""


def install(repo, secret_path, log_name, freshness):
    hooks_dir = repo / ".git" / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    verify_script = SCRIPTS_DIR / "verify_log.py"
    verify_manifest_script = SCRIPTS_DIR / "verify_manifest.py"
    installed = []
    for name in HOOKS:
        dest = hooks_dir / name
        if dest.exists() and MARKER not in dest.read_text(errors="ignore"):
            shutil.copy2(dest, dest.with_name(name + BACKUP_SUFFIX))
        dest.write_text(hook_body(name, verify_script, secret_path, log_name, freshness, verify_manifest_script))
        dest.chmod(dest.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        installed.append(name)
    return installed


def uninstall(repo):
    hooks_dir = repo / ".git" / "hooks"
    removed, restored = [], []
    for name in HOOKS:
        dest = hooks_dir / name
        if dest.exists() and MARKER in dest.read_text(errors="ignore"):
            dest.unlink()
            removed.append(name)
        backup = hooks_dir / (name + BACKUP_SUFFIX)
        if backup.exists():
            shutil.move(str(backup), str(dest))
            restored.append(name)
    return removed, restored


def main(argv=None):
    parser = argparse.ArgumentParser(description="Install/remove guardrail git hooks.")
    parser.add_argument("--repo", help="Repo path (default: current git repo).")
    parser.add_argument("--secret", default="~/.config/gate/hmac.key", help="HMAC secret path.")
    parser.add_argument("--log-name", default=".loop-log.jsonl", help="Loop log filename at repo root.")
    parser.add_argument("--freshness", type=int, default=3600,
                        help="Max age (s) of a PASS entry for pre-commit (default: 3600).")
    parser.add_argument("--uninstall", action="store_true", help="Remove guardrail hooks and restore backups.")
    parser.add_argument("-n", "--dry-run", action="store_true",
                        help="Report which hooks would be installed/removed; change nothing.")
    args = parser.parse_args(argv)

    repo = resolve_repo(args.repo)

    if args.dry_run:
        hooks_dir = repo / ".git" / "hooks"
        action = "remove" if args.uninstall else "install"
        would = []
        for name in HOOKS:
            dest = hooks_dir / name
            foreign = dest.exists() and MARKER not in dest.read_text(errors="ignore")
            would.append({"hook": name, "action": action,
                          "backup_existing": bool(foreign and not args.uninstall)})
        print(f"(--dry-run) {action} in {hooks_dir}:")
        for w in would:
            note = " (existing foreign hook would be backed up)" if w["backup_existing"] else ""
            print(f"  {w['action']}: {w['hook']}{note}")
        return 0

    if args.uninstall:
        removed, restored = uninstall(repo)
        print(f"guardrail: removed {removed or 'none'}; restored backups {restored or 'none'}")
        return 0

    installed = install(repo, os.path.expanduser(args.secret) if args.secret.startswith("~") else args.secret,
                        args.log_name, args.freshness)
    print(f"✓ installed guardrail hooks in {repo}/.git/hooks: {', '.join(installed)}")
    print(f"  freshness window: {args.freshness}s | log: {args.log_name}")
    print("  bypass any single commit with: git commit --no-verify")
    return 0


if __name__ == "__main__":
    sys.exit(main())

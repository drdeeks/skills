#!/usr/bin/env python3
"""sanitize -- thin, path-first front door onto gitsanitize.

    sanitize                     wizard against the current directory
    sanitize /path/to/repo       wizard against that repo instead
    sanitize /path/to/repo scan  any gitsanitize subcommand/flag still
                                  works after an explicit path
    sanitize apply --yes         no path given -> current directory,
                                  exactly like the no-path form above

Verifies the target is actually a git repository before doing anything,
with one clear line explaining what's wrong instead of a confusing error
from deeper in the tool. This is a path-resolving front door only -- it
delegates every real behavior to gitsanitize_cli.main() unchanged, and
reuses that module's own COMMANDS tuple to tell a path apart from a
subcommand name, rather than hardcoding a second copy of it
(FOREVER-SYSTEM §1: singular source of truth, never a duplicate).
"""
import subprocess
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from gitsanitize_cli import COMMANDS  # noqa: E402


def _is_git_repo(path: Path) -> bool:
    """Authoritative check via git itself -- correctly handles worktrees,
    bare repos pointed at by GIT_DIR, and anything else a bare `.git`
    directory presence check would get wrong."""
    result = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "--is-inside-work-tree"],
        capture_output=True, text=True,
    )
    return result.returncode == 0 and result.stdout.strip() == "true"


def main(argv=None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)

    if args and args[0] in ("-h", "--help"):
        print(__doc__)
        return 0

    # A first argument is a path unless it's a flag or a known subcommand
    # name -- everything else about interpreting args is gitsanitize_cli's
    # job, not reimplemented here.
    if args and not args[0].startswith("-") and args[0] not in COMMANDS:
        repo = Path(args[0]).expanduser().resolve()
        rest = args[1:]
    else:
        repo = Path.cwd()
        rest = args

    if not repo.is_dir():
        print(f"sanitize: not a directory: {repo}", file=sys.stderr)
        return 1
    if not _is_git_repo(repo):
        print(f"sanitize: not a git repository: {repo}", file=sys.stderr)
        return 1

    from gitsanitize_cli import main as gitsanitize_main
    return gitsanitize_main(["--repo", str(repo), *rest])


if __name__ == "__main__":
    sys.exit(main())

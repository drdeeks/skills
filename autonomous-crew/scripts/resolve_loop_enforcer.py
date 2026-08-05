#!/usr/bin/env python3
"""
Self-resolving locator for loop-enforcer's canonical chain_enforce.py.

autonomous-crew-integration does not vendor its own chain-enforcement state
machine — chain gating is loop-enforcer's job, singularly (FOREVER-SYSTEM.md
Sec 1: route through the one runtime, don't re-implement enforcement).

Resolution order (FOREVER-SYSTEM.md Sec 2 - env override -> home default ->
built-in default, resolved fresh on every call, no hardcoded absolutes):
  1. explicit override via the CHAIN_ENFORCER_SCRIPT environment variable
  2. loop-enforcer's scripts dir under the global Claude Code skills directory
  3. loop-enforcer's scripts dir under the Hermes runtime skills install (devops category)
Fails closed (raises) if none exist - never silently points at a guessed
path that may not be there. See CANDIDATE_HOME_SUBPATHS below for the exact,
resolved-at-call-time paths checked.
"""
import os
from pathlib import Path

# Home-relative suffixes for candidate #2 and #3 above, kept as data (not
# string-literal-in-prose) so the actual lookup always resolves fresh
# against the real $HOME at call time -- see find_chain_enforce_script().
CANDIDATE_HOME_SUBPATHS = (
    (".claude", "skills", "loop-enforcer", "scripts", "chain_enforce.py"),
    (".hermes", "skills", "devops", "loop-enforcer", "scripts", "chain_enforce.py"),
)


def find_chain_enforce_script() -> str:
    override = os.environ.get("CHAIN_ENFORCER_SCRIPT")
    if override:
        if not Path(override).is_file():
            raise FileNotFoundError(
                f"$CHAIN_ENFORCER_SCRIPT is set to {override!r} but no file exists there."
            )
        return override

    candidates = [Path.home().joinpath(*parts) for parts in CANDIDATE_HOME_SUBPATHS]
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)

    raise FileNotFoundError(
        "Could not find loop-enforcer's chain_enforce.py in any known location "
        f"({', '.join(str(c) for c in candidates)}). Install loop-enforcer, or set "
        "$CHAIN_ENFORCER_SCRIPT to its path."
    )


if __name__ == "__main__":
    print(find_chain_enforce_script())

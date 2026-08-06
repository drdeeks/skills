#!/usr/bin/env python3
"""CLI Orchestrator: user interface that invokes the core engines in order.

Contains NO core policy/rewrite/identity logic — it delegates every capability
to the corresponding engine (single source of truth). It enforces the
safe workflow and fail-closed gates.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

__version__ = "0.2.0"  # single source of truth for this value now that
                       # there is no package __init__.py to hold it (scripts/
                       # is flat, per this repo's skill convention)
import gitsanitize_yamlx as yamlx
from gitsanitize_core import (GSError, SafetyError, VerificationError, PlanError,
                   is_git_repo, run_git)
import gitsanitize_scanner as scanner
import gitsanitize_policy as policy
import gitsanitize_rewrite as rewrite
import gitsanitize_identity as identity
import gitsanitize_verify as verify_engine
from gitsanitize_config import (load_policy, load_providers, resolve_state_dir,
                     user_layers_dir)
from gitsanitize_audit import AuditLog
from gitsanitize_plugins import discover, dispatch
from gitsanitize_state import Session, rollback as do_rollback

COMMANDS = ("wizard", "scan", "plan", "classify", "review", "apply", "verify", "rollback", "publish")


class _App:
    def __init__(self, args):
        self.args = args
        self.repo = Path(args.repo).resolve()
        if not is_git_repo(self.repo):
            raise GSError(f"{self.repo} is not a git repository")
        state_dir = getattr(args, "state_dir", None)
        self.state = Path(state_dir).resolve() if state_dir else resolve_state_dir(self.repo)
        self.state.mkdir(parents=True, exist_ok=True)
        self.audit = AuditLog(self.state / "audit.log")
        self.audit.verify_chain()
        self.policy = load_policy(self.repo, args.layer)
        self.providers = load_providers(self.repo)
        self.plugins = discover(self.repo)
        self.plan_path = self._plan_path()
        self._logged_start()

    def _logged_start(self):
        self.audit.log("cli_invoked", command=self.args.command, repo=str(self.repo))

    def _plan_path(self) -> Path:
        candidates = [Path(self.args.plan)] if getattr(self.args, "plan", None) else []
        if not candidates:
            candidates = [self.state / "cleanup-plan.yaml"]
        p = candidates[0]
        if getattr(self.args, "plan", None):
            p = Path(self.args.plan)
            if not p.is_absolute():
                p = self.repo / p
        return p

    def _plan_from_args(self):
        return policy.load_plan(self.plan_path)

    def _state_dir_plan(self) -> Path:
        return self.state / "cleanup-plan.yaml"


def _confirm(app, message: str) -> bool:
    if getattr(app.args, "yes", False):
        return True
    if getattr(app.args, "batch", False):
        raise SafetyError(
            f"refusing to act in batch mode without --yes: {message}"
        )
    try:
        ans = input(f"{message} [y/N] ").strip().lower()
    except EOFError:
        return False
    return ans in ("y", "yes", "1")


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


def cmd_scan(app: _App) -> int:
    dispatch(app.plugins, "pre-scan", {"repo": str(app.repo)}, app.audit)
    result = scanner.scan(app.repo, deep=getattr(app.args, "deep", False))
    scanner.write_scan_report(app.repo, result, app.state, app.audit)
    cls = result.classify(app.policy.repo_classification)
    print(f"classification: {cls}")
    print(f"commits: {result.total_commits}, authors: {result.author_count()}, "
          f"trailers: {len(result.trailers)}")
    for t in result.trailers:
        print(f"  trailer '{t['label']}': {t['count']}x  e.g. {t['sample']!r}")
    for a in result.authors[:20]:
        print(f"  author: {a['name']} <{a['email']}> ({a['count']} commits)")
    dispatch(app.plugins, "post-scan", {"report": str(app.state / 'scan_report.json')}, app.audit)
    return 0


def cmd_plan(app: _App) -> int:
    dispatch(app.plugins, "pre-plan", {"repo": str(app.repo)}, app.audit)
    report_path = app.state / "scan_report.json"
    if not report_path.exists() or getattr(app.args, "rescan", False):
        result = scanner.scan(app.repo, deep=getattr(app.args, "deep", False))
        scanner.write_scan_report(app.repo, result, app.state, app.audit)
    else:
        result = _result_from_report(report_path, app)
    plan = policy.generate_plan(result, app.policy, app.providers, app._state_dir_plan())
    print(f"plan written: {app._state_dir_plan()}")
    print(f"  classification: {plan.data['classification']}")
    print(f"  identity merges: {len(plan.merges)}")
    for m in plan.merges:
        print(f"    merge {m['from_name']} <{m['from_email']}> -> "
              f"{m['to_name']} <{m['to_email']}> ({m['confidence']}%)")
    print(f"  author removals: {len(plan.removals)}")
    for r in plan.removals:
        print(f"    remove {r['from_name']} <{r['from_email']}> ({r['confidence']}%)")
    print(f"  trailer removes: {len(plan.trailer_removes)}")
    dispatch(app.plugins, "post-plan", {"plan": str(app._state_dir_plan())}, app.audit)
    return 0


def _result_from_report(report_path, app):
    import json
    sc = json.loads(report_path.read_text(encoding="utf-8"))
    res = scanner.ScanResult()
    res.total_commits = sc.get("total_commits", 0)
    res.authors = sc.get("authors", [])
    res.committers = sc.get("committers", [])
    res.trailers = sc.get("trailers", [])
    res.remote_url = sc.get("remote_url")
    res.branches = sc.get("branches", [])
    res.tags = sc.get("tags", [])
    return res


def cmd_classify(app: _App) -> int:
    """Interactively surface every author `scan`/`plan` found that no
    provider, no existing manual rule, and no identity-similarity clustering
    has ever made a decision about, and let the user classify each one on
    the spot. Classifications are written as ordinary `identity_rules`
    entries (the same schema `--layer` files already use) to a GLOBAL layer
    directory by default, so a decision made once ("titan-agent stays",
    "Hemlock Curator merges into DrDeeks") is remembered automatically for
    every repo scanned afterward — not a one-off file for a single repo."""
    dispatch(app.plugins, "pre-classify", {"repo": str(app.repo)}, app.audit)
    report_path = app.state / "scan_report.json"
    if not report_path.exists() or getattr(app.args, "rescan", False):
        result = scanner.scan(app.repo, deep=getattr(app.args, "deep", False))
        scanner.write_scan_report(app.repo, result, app.state, app.audit)
    else:
        result = _result_from_report(report_path, app)

    unclassified = identity.find_unclassified(result.authors, app.policy, app.providers)
    if not unclassified:
        print("no unclassified identities — every author is covered by a "
              "provider match, an existing rule, or identity clustering.")
        return 0

    plural = "y" if len(unclassified) == 1 else "ies"
    print(f"=== {len(unclassified)} unclassified identit{plural} ===")

    if getattr(app.args, "batch", False) and not getattr(app.args, "yes", False):
        for a in unclassified:
            print(f"  {a['name']} <{a['email']}> ({a['count']} commits)")
        print("re-run without --batch to classify interactively.")
        return 0

    new_rules = []
    for author in sorted(unclassified, key=lambda a: -a["count"]):
        print(f"\n{author['name']} <{author['email']}>  ({author['count']} commits)")
        action = _prompt_classification(app, author)
        if action in (None, "quit"):
            if action == "quit":
                break
            continue
        rule = _build_identity_rule(app, author, action, result.authors)
        if rule is None:
            print("  -> skipped (no target given).")
            continue
        new_rules.append(rule)
        label = rule["to_name"] if rule["action"] == "merge" else rule["action"]
        print(f"  -> recorded: {rule['action']} ({label})")

    if not new_rules:
        print("\nno classifications recorded.")
        return 0

    scope = getattr(app.args, "scope", "global") or "global"
    target_dir = user_layers_dir() if scope == "global" else (app.state / "layers")
    target_dir.mkdir(parents=True, exist_ok=True)
    stamp = int(time.time())
    layer_path = target_dir / f"layer_{stamp}_classify.yaml"
    layer = {
        "layer_id": f"classify-{stamp}",
        "source": "gitsanitize classify (interactive)",
        "timestamp": stamp,
        "supersedes": [],
        "identity_rules": new_rules,
    }
    layer_path.write_text(yamlx.dump(layer), encoding="utf-8")
    scope_note = "applies to every repo" if scope == "global" else "applies to this repo only"
    print(f"\nwrote {len(new_rules)} identity rule(s) to {layer_path} ({scope_note})")
    app.audit.log("classify_recorded", path=str(layer_path), count=len(new_rules), scope=scope)
    dispatch(app.plugins, "post-classify", {"path": str(layer_path)}, app.audit)
    return 0


def _prompt_classification(app, author):
    if getattr(app.args, "yes", False):
        # Unattended mode must never silently merge or remove an identity
        # nobody has reviewed — "leave alone" is the only safe default.
        return "keep"
    while True:
        try:
            ans = input("  [k]eep as-is  [m]erge into another identity  "
                        "[r]emove as bot/agent  [s]kip for now  [q]uit: ").strip().lower()
        except EOFError:
            return "quit"
        if ans in ("k", "keep"):
            return "keep"
        if ans in ("m", "merge"):
            return "merge"
        if ans in ("r", "remove"):
            return "remove"
        if ans in ("s", "skip", ""):
            return None
        if ans in ("q", "quit"):
            return "quit"
        print("  please answer k/m/r/s/q")


def _prompt_merge_target(app, all_authors, author):
    others = [a for a in all_authors
              if (a["name"], a["email"]) != (author["name"], author["email"])]
    for i, a in enumerate(others, 1):
        print(f"    {i}. {a['name']} <{a['email']}> ({a['count']} commits)")
    print("    0. (type a new canonical name/email)")
    try:
        choice = input("  merge into which #: ").strip()
    except EOFError:
        return None
    if choice.isdigit() and 1 <= int(choice) <= len(others):
        return others[int(choice) - 1]
    if choice == "0":
        try:
            name = input("  canonical name: ").strip()
            email = input("  canonical email: ").strip()
        except EOFError:
            return None
        if name and email:
            return {"name": name, "email": email}
    return None


def _build_identity_rule(app, author, action, all_authors):
    rule = {
        "name": author["name"], "email": author["email"],
        "to_name": author["name"], "to_email": author["email"],
        "action": action, "confidence": 99,
    }
    if action == "merge":
        target = _prompt_merge_target(app, all_authors, author)
        if target is None:
            return None
        rule["to_name"], rule["to_email"] = target["name"], target["email"]
    return rule


def cmd_review(app: _App) -> int:
    p = app.plan_path
    if not p.exists():
        raise PlanError(f"plan not found: {p}")
    plan = policy.load_plan(p)
    if getattr(app.args, "batch", False) or getattr(app.args, "yes", False):
        print(f"approved plan: {p} ({len(plan.merges)} merges, "
              f"{len(plan.removals)} removals)")
        app.audit.log("plan_approved", path=str(p), batch=True)
        return 0
    print(f"=== Review: {p} ===")
    print(f"classification: {plan.data['classification']}")
    for m in plan.merges:
        ok = _confirm(app, f"merge {m['from_name']} <{m['from_email']}> -> "
                           f"{m['to_name']} <{m['to_email']}> ({m['confidence']}%)?")
        if not ok:
            plan.merges.remove(m)
    for r in list(plan.removals):
        ok = _confirm(app, f"remove author {r['from_name']} <{r['from_email']}>?")
        if not ok:
            plan.removals.remove(r)
    plan.data["reviewed"] = True
    p.write_text(str(_pretty(plan.data)), encoding="utf-8")
    app.audit.log("plan_approved", path=str(p), interactive=True)
    return 0


def _pretty(data) -> str:
    import json
    return json.dumps(data, indent=2)


def cmd_apply(app: _App) -> int:
    app.audit.log("apply_start", plan=str(app.plan_path))
    session = Session.resume_or_new(app.repo)
    if session.is_complete:
        print("previous session completed; starting a new one.")
    plan = policy.load_plan(app.plan_path)

    # 1. fail-closed validation
    policy.validate_plan_fail_closed(plan, app.policy, app.providers, app.audit)

    # 2. approval gate
    if not _confirm(app, "Approving apply REWRITES history irreversibly in a fresh clone. Proceed?"):
        print("aborted.")
        return 1

    # 3. backup (fail-closed: we never rewrite without a backup)
    backups_dir = app.state / "backups"
    if not any(backups_dir.glob("*")) if backups_dir.exists() else True:
        print("creating immutable backup clone...")
        session.backup_clone()
    if not session.backed_up:
        session.backup_clone()

    # 4. snapshot + baseline
    session.snapshot_refs()
    verify_engine.verify_baseline(app.repo, plan, app.state, app.audit)

    # 5. rewrite
    dispatch(app.plugins, "pre-rewrite", {"plan": str(app.plan_path)}, app.audit)
    result = rewrite.run_rewrite(app.repo, plan, app.audit)
    session.commit(str(app.plan_path), result)
    dispatch(app.plugins, "post-rewrite", {"result": result}, app.audit)

    # 6. verify
    final_head = run_git(["rev-parse", "HEAD"], app.repo, check=False).stdout.strip()
    if not getattr(app.args, "no_verify", False):
        try:
            verify_engine.verify(app.repo, plan, app.state, app.audit, strict=True)
        except VerificationError:
            app.audit.log("verification_failed", plan=str(app.plan_path))
            raise
        session.mark_verified()
        print("verification passed.")
    else:
        app.audit.log("verify_skipped", flag="--no-verify")

    session.complete(final_head)
    print("apply complete. Run 'gitsanitize publish' to push.")
    return 0


def cmd_verify(app: _App) -> int:
    plan = app._plan_from_args()
    result = verify_engine.verify(app.repo, plan, app.state, app.audit, strict=not getattr(app.args, "no_verify", False))
    print(f"ok={result['ok']}")
    for k in ("commit_count_before", "commit_count_after", "author_count_before",
              "author_count_after", "branches_before", "branches_after",
              "tags_before", "tags_after", "fsck_errors", "banned_trailers_remaining"):
        print(f"  {k}: {result[k]}")
    return 0 if result["ok"] else 4


def cmd_rollback(app: _App) -> int:
    if not _confirm(app, "Rollback will replace current history with the backup. Proceed?"):
        print("aborted.")
        return 1
    do_rollback(app.repo, app.state, app.audit)
    print("rollback complete.")
    return 0


def cmd_wizard(app: _App) -> int:
    """Interactive, guided walkthrough: scan -> classify -> plan -> review ->
    apply -> publish, run in order against the same repo. This is the
    default when gitsanitize is invoked with no subcommand at all.

    Every step below calls the exact same implementation the raw subcommands
    use -- nothing here is reimplemented, this only sequences them
    (FOREVER-SYSTEM §1, singular source of truth). Each step already knows
    how to behave under --yes/--batch on its own (classify prompts per
    identity, review prompts per decision, apply and publish each confirm
    before doing anything irreversible); the wizard adds no confirmation
    logic of its own on top of that.
    """
    steps = [
        ("1/6  scan", cmd_scan),
        ("2/6  classify", cmd_classify),
        ("3/6  plan", cmd_plan),
        ("4/6  review", cmd_review),
        ("5/6  apply", cmd_apply),
        ("6/6  publish", cmd_publish),
    ]
    print(f"=== gitsanitize wizard: {app.repo} ===")
    for label, fn in steps:
        print(f"\n--- {label} ---")
        if fn is cmd_plan:
            # Policy was loaded once at startup, before classify (the step
            # right before this one) could have written anything -- reload
            # it so plan actually sees whatever classify just recorded.
            app.policy = load_policy(app.repo, app.args.layer)
            app.args.rescan = True
        rc = fn(app)
        if rc != 0:
            return rc
    return 0


def cmd_publish(app: _App) -> int:
    app.audit.log("publish_start")
    if not _confirm(app, "Publish force-pushes rewritten history to origin. Proceed?"):
        print("aborted.")
        return 1
    # ensure a completed, verified session exists and verification passed
    if not getattr(app.args, "no_verify", False):
        plan = app._plan_from_args()
        try:
            verify_engine.verify(app.repo, plan, app.state, app.audit, strict=True)
        except VerificationError:
            raise
    # rely on --force-with-lease for safety
    dispatch(app.plugins, "publish-hook", {"pre": True}, app.audit)
    run_git(["fetch", "origin"], app.repo)
    # git rejects --all and --tags in the same invocation ("options '--all'
    # and '--tags' cannot be used together") -- two pushes, not one.
    for extra in (["--all"], ["--tags"]):
        push = run_git(["push", "--force-with-lease", "origin", *extra], app.repo, check=False)
        if push.returncode != 0:
            raise GSError("push blocked/rejected (force-with-lease failed). "
                          "Remote diverged or branch-protected. Pull changes into a fresh "
                          "clone and re-apply. Use --dangerously-skip-safety-checks to override.")
    dispatch(app.plugins, "publish-hook", {"post": True}, app.audit)
    app.audit.log("publish_complete")
    print("published.")
    return 0


# ---------------------------------------------------------------------------
# argparse
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="gitsanitize",
        description="Layered, fail-closed repository history sanitization runtime.",
    )
    p.add_argument("--version", action="version", version=f"gitsanitize {__version__}")
    p.add_argument("--repo", default=".", help="repository path (default: .)")
    p.add_argument("--config", default=None, help="explicit config file")
    p.add_argument("--layer", action="append", default=None, help="extra policy layer file")
    p.add_argument("--state-dir", default=None, help="override state dir")
    p.add_argument("--deep", action="store_true", help="deep scan of blob content")

    sub = p.add_subparsers(dest="command", required=False)

    sp = sub.add_parser("wizard",
                         help="interactive guided walkthrough: scan -> classify -> plan -> "
                              "review -> apply -> publish (default when no command is given)")
    sp.add_argument("--deep", action="store_true")
    sp.add_argument("--scope", choices=("global", "repo"), default="global",
                    help="where classify persists new rules (default: global)")
    wgroup = sp.add_mutually_exclusive_group()
    wgroup.add_argument("--yes", action="store_true", help="assume yes at every confirmation")
    wgroup.add_argument("--batch", action="store_true", help="non-interactive CI mode")
    wgroup.add_argument("--dangerously-skip-safety-checks", action="store_true",
                        help="skip fail-closed gates (EXPERTS ONLY)")
    sp.add_argument("--no-verify", action="store_true", help="skip post-rewrite checks")

    sp = sub.add_parser("scan", help="analyze history (read-only)")
    sp.add_argument("--report", default=None)
    sp.add_argument("--deep", action="store_true")

    sp = sub.add_parser("plan", help="generate cleanup-plan.yaml from scan + policy")
    sp.add_argument("--rescan", action="store_true")
    sp.add_argument("--deep", action="store_true")

    sp = sub.add_parser("classify",
                         help="interactively classify authors no provider/rule/cluster covers")
    sp.add_argument("--rescan", action="store_true")
    sp.add_argument("--deep", action="store_true")
    sp.add_argument("--scope", choices=("global", "repo"), default="global",
                    help="where to persist new rules (default: global, applies to all repos)")
    group = sp.add_mutually_exclusive_group()
    group.add_argument("--yes", action="store_true",
                       help="non-interactive: mark every unclassified author 'keep as-is'")
    group.add_argument("--batch", action="store_true",
                       help="non-interactive: list unclassified authors only, record nothing")

    sp = sub.add_parser("review", help="interactively approve/edit a plan")
    sp.add_argument("plan", nargs="?", default=None)

    sp = sub.add_parser("apply", help="apply a plan (rewrite history) [DANGEROUS]")
    sp.add_argument("plan", nargs="?", default=None)
    _add_safety_flags(sp)

    sp = sub.add_parser("verify", help="verify post-rewrite state vs baseline")
    sp.add_argument("--no-verify", action="store_true", help=argparse.SUPPRESS)
    sp.add_argument("plan", nargs="?", default=None)

    sp = sub.add_parser("rollback", help="restore history from backup")
    _add_safety_flags(sp)

    sp = sub.add_parser("publish", help="force-push rewritten history (--force-with-lease)")
    _add_safety_flags(sp)

    return p


def _add_safety_flags(sp):
    group = sp.add_mutually_exclusive_group()
    group.add_argument("--yes", action="store_true", help="assume yes to prompts")
    group.add_argument("--batch", action="store_true", help="non-interactive CI mode")
    group.add_argument("--dangerously-skip-safety-checks",
                       action="store_true",
                       help="skip fail-closed gates (EXPERTS ONLY)")
    sp.add_argument("--no-verify", action="store_true", help="skip post-rewrite checks")


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        # Interactive by default: no subcommand at all runs the guided
        # walkthrough rather than printing a usage error.
        args.command = "wizard"
    try:
        app = _App(args)
        handler = {
            "wizard": cmd_wizard,
            "scan": cmd_scan,
            "plan": cmd_plan,
            "classify": cmd_classify,
            "review": cmd_review,
            "apply": cmd_apply,
            "verify": cmd_verify,
            "rollback": cmd_rollback,
            "publish": cmd_publish,
        }[args.command]
        return handler(app)
    except SafetyError as exc:
        print(f"error (safety): {exc}", file=sys.stderr)
        return exc.exit_code
    except (GSError, PlanError, VerificationError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return getattr(exc, "exit_code", 2)
    except KeyboardInterrupt:
        print("interrupted.", file=sys.stderr)
        return 130
    except Exception as exc:  # pragma: no cover
        print(f"unexpected error: {exc!r}", file=sys.stderr)
        if getattr(args, "debug", False):
            raise
        return 1


if __name__ == "__main__":
    sys.exit(main())
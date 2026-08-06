#!/usr/bin/env python3
"""Self-resolving configuration discovery + layered policy merging.

Resolution precedence (first match wins for finding a FILE):
    environment override -> user state -> repo-local state -> built-in default

Policies are expressed as immutable LAYERS. Each layer carries metadata
(`layer_id`, `timestamp`, `supersedes`) and rule sections. Layers merge in
order (base first, newest last). A conflict (same identity key mapping to
different canonical targets across layers) BLOCKS the merge unless a newer
layer declares `supersedes` for that layer_id or the entry is an `override`.
"""
from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass, field
from pathlib import Path

import gitsanitize_yamlx as yamlx
from gitsanitize_core import GSError, SafetyError, sha256_file

# ---------------------------------------------------------------------------
# Schemas (strict; unknown keys / wrong types => error)
# ---------------------------------------------------------------------------

LAYER_SCHEMA = {
    "layer_id": True,
    "timestamp": "*",
    "source": True,
    "supersedes": "*",
    "identity_rules": [
        {
            "@label": "identity_rule",
            "@schema": {
                "name": True,
                "email": True,
                "to_name": True,
                "to_email": True,
                "action": True,
                "pattern": "*",
                "confidence": "*",
                "override": "*",
            },
        }
    ],
    "trailer_rules": [
        {
            "@label": "trailer_rule",
            "@schema": {
                "label": True,
                "pattern": True,
                "action": True,
                "override": "*",
            },
        }
    ],
    "repo_classification": {
        "mode": "*",
        "protected_authors": "*",
        "auto_merge_threshold": "*",
        "suggest_threshold": "*",
        "merge_confidence": "*",
        "remove_confidence": "*",
        "owner_dominance": "*",
    },
}

IDENTITY_RULE_SCHEMA = {
    "name": True,
    "email": True,
    "to_name": True,
    "to_email": True,
    "action": True,
    "pattern": "*",
    "confidence": "*",
    "override": "*",
}

TRAILER_RULE_SCHEMA = {
    "label": True,
    "pattern": True,
    "action": True,
    "override": "*",
}

PROVIDER_SCHEMA = {
    "name": True,
    "id_pattern": "*",
    "trailer_pattern": "*",
    "content_pattern": "*",
    "action": "*",
    "confidence": "*",
    "default_action": "*",
}

CONFIG_SCHEMA = {
    "thresholds": {
        "auto_merge": "*",
        "suggest": "*",
        "merge_confidence": "*",
        "remove_confidence": "*",
        "owner_dominance": "*",
    },
    "repo_classification": "*",
    "state_dir": "*",
    "backup_enabled": "*",
    "verify_enabled": "*",
    "user": "*",
    "email": "*",
}

# ---------------------------------------------------------------------------
# Built-in defaults (compiled in, hashable, immutable)
# ---------------------------------------------------------------------------

BUILTIN_LAYERS = [
    {
        "layer_id": "core-default-1",
        "source": "builtin",
        "supersedes": [],
        "repo_classification": {
            "mode": "auto",
            "owner_dominance": 80,
            "auto_merge_threshold": 90,
            "suggest_threshold": 70,
            "merge_confidence": 90,
            "remove_confidence": 95,
            "protected_authors": [],
        },
        "trailer_rules": [
            {
                "label": "Co-authored-by",
                "pattern": r"^Co-authored-by:",
                "action": "keep",
            }
        ],
    }
]

DEFAULT_THRESHOLDS = {
    "auto_merge": 90,
    "suggest": 70,
    "merge_confidence": 90,
    "remove_confidence": 95,
    "owner_dominance": 80,
}

# ---------------------------------------------------------------------------
# Path discovery
# ---------------------------------------------------------------------------


def user_state_dir() -> Path:
    env = os.environ.get("GITSANITIZE_STATE_DIR")
    if env:
        return Path(env).expanduser()
    if os.name == "nt":
        base = os.environ.get("APPDATA") or str(Path.home())
        return Path(base) / "GitSanitize"
    return Path.home() / ".gitsanitize"


def resolve_config_file(name: str, repo: Path | None) -> Path | None:
    """Find a config file by name following the resolution chain."""
    env = os.environ.get(f"GITSANITIZE_{name.upper().replace('.', '_').replace('-', '_')}")
    if env:
        p = Path(env).expanduser()
        if p.exists():
            return p
    cands = [user_state_dir() / name]
    if repo is not None:
        cands.append(repo / ".gitsanitize" / name)
    for cand in cands:
        if cand.exists():
            return cand
    return None


def repo_slug(repo: Path) -> str:
    """Stable, human-browsable identifier for a repo's per-repo state
    namespace: <dirname>-<sha256(abs path)[:12]>. The hash suffix keeps
    two differently-located repos that happen to share a directory name
    (e.g. two clones both named "skills") from colliding."""
    resolved = repo.resolve()
    digest = hashlib.sha256(str(resolved).encode("utf-8")).hexdigest()[:12]
    return f"{resolved.name}-{digest}"


def user_layers_dir() -> Path:
    """Global, cross-repo policy layers (e.g. identity rules recorded via
    `gitsanitize classify`). Loaded for every repo regardless of that
    repo's state-dir resolution, so a classification made once ("titan-agent
    stays", "Hemlock Curator merges into DrDeeks") is remembered for every
    repo scanned afterward, not just the one it was recorded against."""
    return user_state_dir() / "layers"


def resolve_state_dir(repo: Path | None) -> Path:
    """Per-repo working state (scan_report.json, cleanup-plan.yaml,
    audit.log, backups/). Distinct from `user_layers_dir()`, which is
    global on purpose. Previously this fell back straight to the shared
    `user_state_dir()` root for every repo without local `.gitsanitize/`
    state, so running `plan` against repo A then repo B without an explicit
    `--state-dir` silently overwrote A's plan/report with B's. Namespacing
    the fallback under a per-repo slug fixes that at the source instead of
    requiring every caller to remember `--state-dir`."""
    env = os.environ.get("GITSANITIZE_STATE_DIR")
    if env:
        return Path(env).expanduser()
    if repo is not None:
        local = repo / ".gitsanitize"
        if local.is_dir():
            return local
        return user_state_dir() / "repos" / repo_slug(repo)
    return user_state_dir()


def find_providers_db(repo: Path | None) -> Path | None:
    found = resolve_config_file("providers.json", repo)
    if found:
        return found
    # builtin fallback bundled with the skill. scripts/ is flat (this repo's
    # skill convention forbids subdirectories under it, including a data/
    # dir) and references/ only allows doc extensions (.md/.txt/.html/.pdf)
    # outside of references/templates/, which allows any file type -- so
    # that's where the bundled provider database actually lives.
    builtin = (Path(__file__).resolve().parent.parent / "references" / "templates"
               / "providers.json")
    return builtin if builtin.exists() else None


def find_plugin_path(repo: Path | None) -> list[Path]:
    env = os.environ.get("GITSANITIZE_PLUGIN_PATH")
    dirs = []
    if env:
        dirs.append(Path(env).expanduser())
    dirs.append(user_state_dir() / "plugins")
    if repo is not None:
        dirs.append(repo / ".gitsanitize" / "plugins")
    return [d for d in dirs if d.is_dir()]


# ---------------------------------------------------------------------------
# Layer loading + merging
# ---------------------------------------------------------------------------


def _load_layer_file(path: Path) -> dict:
    try:
        data = yamlx.load(path)
    except (ValueError, OSError) as exc:
        raise GSError(f"cannot load layer {path}: {exc}")
    if not isinstance(data, dict):
        raise GSError(f"layer {path} must be a mapping")
    from gitsanitize_core import validate_schema
    validate_schema(data, LAYER_SCHEMA, str(path))
    if "layer_id" not in data:
        raise GSError(f"layer {path} is missing required field 'layer_id'")
    data["_path"] = str(path)
    data["_sha256"] = sha256_file(path)
    return data


def _iter_layer_files(layers_dir: Path) -> list[Path]:
    if not layers_dir.is_dir():
        return []
    return sorted(p for p in layers_dir.glob("layer_*.yaml"))


def load_layers(repo: Path | None, extra: list[Path] | None = None) -> list[dict]:
    """Return ordered immutable layers: builtins first, then global
    (cross-repo) layers, then this repo's own state-dir layers (if that's a
    different directory), then any explicit --layer overrides."""
    layers = [dict(l) for l in BUILTIN_LAYERS]
    global_dir = user_layers_dir()
    for p in _iter_layer_files(global_dir):
        layers.append(_load_layer_file(p))
    repo_layers_dir = resolve_state_dir(repo) / "layers"
    if repo_layers_dir != global_dir:
        for p in _iter_layer_files(repo_layers_dir):
            layers.append(_load_layer_file(p))
    for p in (extra or []):
        layers.append(_load_layer_file(Path(p)))
    return layers


def _identity_key(rule: dict) -> str:
    name = (rule.get("name") or "").strip().lower()
    email = (rule.get("email") or "").strip().lower()
    return f"{name}|{email}"


def _merge_identity_rules(layers: list[dict]) -> list[dict]:
    merged: dict[str, dict] = {}
    order: list[str] = []
    for layer in layers:
        lid = layer["layer_id"]
        for rule in layer.get("identity_rules", []):
            key = _identity_key(rule)
            target = f"{rule.get('to_name')}|{rule.get('to_email')}"
            prev = merged.get(key)
            if prev is not None and not rule.get("override"):
                prev_target = f"{prev.get('to_name')}|{prev.get('to_email')}"
                if prev_target != target:
                    if lid not in (prev.get("_superseded_by") or []) and not _supersedes(
                        layer, prev.get("_layer_id")
                    ):
                        raise SafetyError(
                            "identity conflict: "
                            f"'{key}' maps to '{prev_target}' (in {prev.get('_layer_id')}) "
                            f"but '{target}' (in {lid}). Resolve by adding an "
                            "`override: true` rule in a newer layer."
                        )
            merged[key] = dict(rule)
            merged[key]["_layer_id"] = lid
            if key not in order:
                order.append(key)
    return [merged[k] for k in order]


def _supersedes(layer: dict, target_id: str | None) -> bool:
    if not target_id:
        return False
    for sid in layer.get("supersedes") or []:
        if sid == target_id:
            return True
    return False


def _merge_trailer_rules(layers: list[dict]) -> list[dict]:
    merged: dict[str, dict] = {}
    order: list[str] = []
    for layer in layers:
        lid = layer["layer_id"]
        for rule in layer.get("trailer_rules", []):
            key = rule.get("label", rule.get("pattern", ""))
            prev = merged.get(key)
            if prev is not None and prev.get("action") != rule.get("action") and not rule.get("override"):
                if not _supersedes(layer, prev.get("_layer_id")):
                    raise SafetyError(
                        "trailer conflict: "
                        f"'{key}' has action '{prev.get('action')}' (in {prev.get('_layer_id')}) "
                        f"but '{rule.get('action')}' (in {lid}). Use override or supersedes."
                    )
            merged[key] = dict(rule)
            merged[key]["_layer_id"] = lid
            if key not in order:
                order.append(key)
    return [merged[k] for k in order]


def _merge_repo_classification(layers: list[dict], default: dict) -> dict:
    out = dict(default)
    for layer in layers:
        rc = layer.get("repo_classification")
        if rc:
            out.update({k: v for k, v in rc.items() if v is not None})
    return out


@dataclass
class Policy:
    layers: list[dict]
    identity_rules: list[dict] = field(default_factory=list)
    trailer_rules: list[dict] = field(default_factory=list)
    repo_classification: dict = field(default_factory=dict)
    thresholds: dict = field(default_factory=lambda: dict(DEFAULT_THRESHOLDS))
    fingerprints: list[dict] = field(default_factory=list)

    @property
    def layer_ids(self) -> list[str]:
        return [l["layer_id"] for l in self.layers]

    def to_audit(self) -> dict:
        return {
            "layers": self.layer_ids,
            "fingerprints": self.fingerprints,
        }


def load_policy(repo: Path | None, extra_layers: list[Path] | None = None) -> Policy:
    from gitsanitize_core import validate_schema

    layers = load_layers(repo, extra_layers)
    for layer in layers:
        validate_schema(layer, LAYER_SCHEMA, layer.get("layer_id", "?"))

    identity_rules = _merge_identity_rules(layers)
    trailer_rules = _merge_trailer_rules(layers)

    cls_default = dict(BUILTIN_LAYERS[0]["repo_classification"])
    cls = _merge_repo_classification(layers, cls_default)

    thresholds = dict(DEFAULT_THRESHOLDS)
    for layer in layers:
        rc = layer.get("repo_classification") or {}
        for k in ("auto_merge_threshold", "suggest_threshold",
                  "merge_confidence", "remove_confidence", "owner_dominance"):
            if rc.get(k) is not None:
                thresholds[k] = rc[k]

    fingerprints = [
        {"layer_id": l["layer_id"], "sha256": l.get("_sha256"), "path": l.get("_path")}
        for l in layers
        if l.get("_sha256")
    ]
    return Policy(
        layers=layers,
        identity_rules=identity_rules,
        trailer_rules=trailer_rules,
        repo_classification=cls,
        thresholds=thresholds,
        fingerprints=fingerprints,
    )


def load_providers(repo: Path | None) -> list[dict]:
    """Load AI/service metadata database. Empty list if absent."""
    from gitsanitize_core import validate_schema

    path = find_providers_db(repo)
    if path is None:
        return []
    import json

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, OSError) as exc:
        raise GSError(f"invalid providers DB {path}: {exc}")
    if not isinstance(data, list):
        raise GSError(f"providers DB {path} must be a JSON list")
    validate_schema(data, [{"@label": "provider", "@schema": PROVIDER_SCHEMA}], str(path))
    return data


if __name__ == "__main__":  # pragma: no cover
    import argparse as _argparse
    _p = _argparse.ArgumentParser(
        prog="gitsanitize_config.py",
        description=(
            "gitsanitize library module: config.py. This is implementation, "
            "not a standalone CLI -- run scripts/gitsanitize.py instead, "
            "which is the real entry point and imports this module itself."
        ),
    )
    _p.parse_args()  # no arguments defined: --help prints usage and exits 0;
                      # any unexpected argument is argparse's own clean
                      # "unrecognized arguments" error (exit 2), not a traceback

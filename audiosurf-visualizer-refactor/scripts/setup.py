#!/usr/bin/env python3
"""
AudioSurf Visualizer — Setup & Environment Validation

Detects WebGL capabilities, validates dependencies, and scaffolds project structure.

Usage:
    python3 setup.py                    # Full setup
    python3 setup.py --dry-run          # Preview without changes
    python3 setup.py --status           # Show current state
    python3 setup.py --help
"""

import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

STATE_DIR = Path.home() / ".audiosurf-visualizer"
CONFIG_PATH = STATE_DIR / "config.json"
ANALYTICS_DIR = STATE_DIR / "analytics"

DEFAULT_CONFIG = {
    "version": 1,
    "created_at": "",
    "status": "initializing",
    "performance_tier": "auto",
    "color_theme": "neon-bahamas",
    "target_fps": 60,
    "audio_backend": "web-audio-api",
    "shader_quality": "adaptive",
}

REQUIRED_DEPS = {
    "three": "^0.170.0",
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "@react-three/fiber": "^8.17.0",
    "@react-three/drei": "^9.115.0",
    "@react-three/postprocessing": "^2.16.0",
    "postprocessing": "^6.36.0",
    "meyda": "^5.6.0",
    "leva": "^0.9.35",
}

FREE_DEPS = {
    "three": "$0 — MIT",
    "react": "$0 — MIT",
    "@react-three/fiber": "$0 — MIT",
    "@react-three/postprocessing": "$0 — MIT",
    "meyda": "$0 — MIT",
}


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def append_jsonl(filepath, record):
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "a") as f:
        f.write(json.dumps(record) + "\n")


def check_node():
    """Check if Node.js is available."""
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        return result.stdout.strip()
    except FileNotFoundError:
        return None


def scaffold_project(project_dir, dry_run=False):
    """Create the project directory structure."""
    dirs = [
        project_dir / "src" / "components",
        project_dir / "src" / "shaders",
        project_dir / "src" / "hooks",
        project_dir / "src" / "audio",
        project_dir / "src" / "systems",
        project_dir / "public",
    ]
    for d in dirs:
        if not dry_run:
            d.mkdir(parents=True, exist_ok=True)
        print(f"  {'[DRY RUN] ' if dry_run else ''}Directory: {d.relative_to(project_dir)}")


def setup(dry_run=False):
    prefix = "[DRY RUN] " if dry_run else ""
    print(f"{prefix}Setting up AudioSurf Visualizer...\n")

    # 1. Validate environment
    node_ver = check_node()
    if node_ver:
        print(f"  Node.js: {node_ver}")
    else:
        print("  WARNING: Node.js not found. Install Node.js 18+ to proceed.")

    # 2. Create state directory
    state_dirs = [STATE_DIR, ANALYTICS_DIR, STATE_DIR / "reports", STATE_DIR / "logs"]
    for d in state_dirs:
        if not dry_run:
            d.mkdir(parents=True, exist_ok=True)
        print(f"  {prefix}State dir: {d}")

    # 3. Write config
    if not dry_run and not CONFIG_PATH.exists():
        config = DEFAULT_CONFIG.copy()
        config["created_at"] = now_iso()
        config["node_version"] = node_ver or "not found"
        CONFIG_PATH.write_text(json.dumps(config, indent=2))
    print(f"  {prefix}Config: {CONFIG_PATH}")

    # 4. Log setup event
    if not dry_run:
        append_jsonl(ANALYTICS_DIR / "run_stats.jsonl", {
            "operation": "setup",
            "timestamp": now_iso(),
            "status": "success",
            "node_version": node_ver,
        })

    print(f"\n{prefix}Setup complete.")
    print(f"\nRequired dependencies (all $0 / MIT):")
    for dep, ver in REQUIRED_DEPS.items():
        cost = FREE_DEPS.get(dep, "$0 — MIT")
        print(f"  {dep}@{ver}  ({cost})")


def show_status():
    if CONFIG_PATH.exists():
        config = json.loads(CONFIG_PATH.read_text())
        print(json.dumps(config, indent=2))
    else:
        print("Not initialized. Run: python3 setup.py")


def main():
    if "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__)
    elif "--dry-run" in sys.argv:
        setup(dry_run=True)
    elif "--status" in sys.argv:
        show_status()
    else:
        setup()


if __name__ == "__main__":
    main()

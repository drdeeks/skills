#!/usr/bin/env python3
"""
Render Manim video from scene file.
"""

import argparse
import sys
import subprocess
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Render Manim video")
    parser.add_argument("scene_file", help="Path to scene file")
    parser.add_argument("--scene", help="Scene class name to render")
    parser.add_argument("--quality", choices=["low", "medium", "high", "4k"], default="medium")
    parser.add_argument("--output", help="Output directory")
    parser.add_argument("--preview", action="store_true", help="Preview after render")
    args = parser.parse_args()
    
    scene_file = Path(args.scene_file)
    if not scene_file.exists():
        print(f"Error: {scene_file} not found")
        return 1
    
    quality_flags = {
        "low": "-ql",
        "medium": "-qm",
        "high": "-qh",
        "4k": "-qk"
    }
    
    cmd = ["manim", "render", quality_flags[args.quality], str(scene_file)]
    if args.scene:
        cmd.append(args.scene)
    if args.output:
        cmd.extend(["--media_dir", args.output])
    if args.preview:
        cmd.append("-p")
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())

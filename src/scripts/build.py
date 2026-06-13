#!/usr/bin/env python3
"""
Build src project.
"""

import argparse
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Build src project")
    parser.add_argument("--target", type=str, default="production", help="Build target")
    parser.add_argument("--output", type=str, help="Output directory")
    args = parser.parse_args()
    
    print(f"Building for target: {args.target}")
    print(f"Output: {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

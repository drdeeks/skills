#!/usr/bin/env python3
"""
Benchmark inference performance.
"""

import argparse
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Benchmark inference")
    parser.add_argument("--endpoint", required=True, help="Inference endpoint URL")
    parser.add_argument("--requests", type=int, default=100)
    parser.add_argument("--concurrency", type=int, default=10)
    parser.add_argument("--prompt", default="Hello, how are you?")
    args = parser.parse_args()
    
    print(f"Benchmarking {args.endpoint}")
    print(f"Requests: {args.requests}, Concurrency: {args.concurrency}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

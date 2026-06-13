#!/usr/bin/env python3
"""
Evaluate trained model.
"""

import argparse
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Evaluate model")
    parser.add_argument("--model", required=True, help="Model path")
    parser.add_argument("--dataset", required=True, help="Evaluation dataset")
    parser.add_argument("--metrics", nargs="+", default=["perplexity", "accuracy"])
    parser.add_argument("--output", help="Results output file")
    args = parser.parse_args()
    
    print(f"Evaluating {args.model} on {args.dataset}")
    print(f"Metrics: {args.metrics}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Linear CLI - Manage Linear issues, projects, and teams via GraphQL API.
"""

import argparse
import os
import json
import sys
import subprocess
from pathlib import Path


def run_query(query, variables=None):
    """Execute a GraphQL query against Linear API."""
    api_key = os.environ.get("LINEAR_API_KEY")
    if not api_key:
        print("Error: LINEAR_API_KEY not set", file=sys.stderr)
        return None
    
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    
    cmd = [
        "curl", "-s", "-X", "POST", "https://api.linear.app/graphql",
        "-H", f"Authorization: {api_key}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(payload)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout


def main():
    parser = argparse.ArgumentParser(description="Linear CLI")
    parser.add_argument("--query", help="GraphQL query to execute")
    parser.add_argument("--file", help="File containing GraphQL query")
    parser.add_argument("--teams", action="store_true", help="List teams")
    parser.add_argument("--issues", action="store_true", help="List issues")
    parser.add_argument("--me", action="store_true", help="Get current user")
    args = parser.parse_args()
    
    if args.me:
        query = "{ viewer { id name email } }"
        result = run_query(query)
    elif args.teams:
        query = "{ teams { nodes { id name key } } }"
        result = run_query(query)
    elif args.issues:
        query = "{ issues(first: 20) { nodes { identifier title priority state { name type } assignee { name } team { key } url } pageInfo { hasNextPage endCursor } } }"
        result = run_query(query)
    elif args.query:
        result = run_query(args.query)
    elif args.file:
        with open(args.file) as f:
            query = f.read()
        result = run_query(query)
    else:
        parser.print_help()
        return 1
    
    if result:
        print(result)
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())

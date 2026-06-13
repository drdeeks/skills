#!/usr/bin/env python3
"""
Create Linear issues interactively.
"""

import argparse
import os
import json
import sys
import subprocess
from pathlib import Path


def run_mutation(mutation, variables):
    """Execute a GraphQL mutation against Linear API."""
    api_key = os.environ.get("LINEAR_API_KEY")
    if not api_key:
        print("Error: LINEAR_API_KEY not set", file=sys.stderr)
        return None
    
    payload = {"query": mutation, "variables": variables}
    
    cmd = [
        "curl", "-s", "-X", "POST", "https://api.linear.app/graphql",
        "-H", f"Authorization: {api_key}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(payload)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout


def main():
    parser = argparse.ArgumentParser(description="Create Linear issue")
    parser.add_argument("--team", required=True, help="Team key (e.g., ENG)")
    parser.add_argument("--title", required=True, help="Issue title")
    parser.add_argument("--description", help="Issue description")
    parser.add_argument("--priority", type=int, default=3, help="Priority (0-4)")
    parser.add_argument("--assignee", help="Assignee email")
    args = parser.parse_args()
    
    # Get team ID
    team_query = f'{{ teams(filter: {{ key: {{ eq: "{args.team}" }} }}) {{ nodes {{ id }} }} }}'
    import subprocess as sp
    result = sp.run([
        "curl", "-s", "-X", "POST", "https://api.linear.app/graphql",
        "-H", f"Authorization: {os.environ.get('LINEAR_API_KEY')}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps({"query": team_query})
    ], capture_output=True, text=True)
    
    team_data = json.loads(result.stdout)
    team_id = team_data.get("data", {}).get("teams", {}).get("nodes", [{}])[0].get("id")
    
    if not team_id:
        print(f"Error: Team {args.team} not found", file=sys.stderr)
        return 1
    
    # Create issue
    mutation = """
    mutation($input: IssueCreateInput!) {
        issueCreate(input: $input) {
            success
            issue { id identifier title url }
        }
    }
    """
    
    variables = {
        "input": {
            "teamId": team_id,
            "title": args.title,
            "priority": args.priority
        }
    }
    
    if args.description:
        variables["input"]["description"] = args.description
    
    result = run_mutation(mutation, variables)
    print(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())

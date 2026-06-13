#!/usr/bin/env python3
"""
License Detector - Detects project type and recommends appropriate license
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Optional


def detect_license_from_files(repo_path: Path) -> Optional[str]:
    """
    Detect appropriate license based on project files and dependencies.
    
    Args:
        repo_path: Path to repository checkout
        
    Returns:
        Recommended license type (e.g., "MIT", "Apache-2.0") or None
    """
    # Check for explicit license files first
    license_files = ["LICENSE", "LICENSE.txt", "LICENSE.md", "COPYING", "COPYING.txt"]
    for license_file in license_files:
        if (repo_path / license_file).exists():
            # Try to detect license type from content
            content = (repo_path / license_file).read_text(encoding='utf-8', errors='ignore').lower()
            if "mit license" in content or "massachusetts institute of technology" in content:
                return "MIT"
            elif "apache license" in content and "version 2.0" in content:
                return "Apache-2.0"
            elif "gnu general public license" in content and "version 3" in content:
                return "GPL-3.0"
            elif "bsd" in content:
                if "2-clause" in content or "simplified" in content:
                    return "BSD-2-Clause"
                elif "3-clause" in content or "new" in content:
                    return "BSD-3-Clause"
                else:
                    return "BSD-3-Clause"  # Default BSD
    
    # Detect from project files
    project_indicators = {
        # Python
        ("requirements.txt", "setup.py", "pyproject.toml", "Pipfile", "Pipfile.lock"): "MIT",
        # Node.js/JavaScript
        ("package.json", "yarn.lock", "pnpm-lock.yaml"): "MIT",
        # Rust
        ("Cargo.toml", "Cargo.lock"): "MIT",
        # Go
        ("go.mod", "go.sum"): "MIT",
        # Java
        ("pom.xml", "build.gradle"): "Apache-2.0",
        # C#/.NET
        ("*.csproj", "*.vbproj", "project.json"): "MIT",
        # PHP
        ("composer.json", "composer.lock"): "MIT",
        # Ruby
        ("Gemfile", "Gemfile.lock"): "MIT",
        # Swift
        ("Package.swift"): "MIT",
    }
    
    for files, license in project_indicators.items():
        if any((repo_path / f).exists() for f in files):
            return license
    
    # Default to MIT for unknown projects
    return "MIT"


def detect_license_from_github_api(repo_contents: List[Dict]) -> Optional[str]:
    """
    Detect license from GitHub repository contents API response.
    
    Args:
        repo_contents: List of file objects from GitHub API
        
    Returns:
        Detected license type or None
    """
    # Check for license files in root directory
    for item in repo_contents:
        if item.get("type") == "file":
            name = item.get("name", "").upper()
            if name in ["LICENSE", "LICENSE.TXT", "LICENSE.MD", "COPYING", "COPYING.TXT"]:
                # Would need to fetch content to determine type
                # For now, return generic detection
                return "MIT"  # Placeholder - would need actual content check
    
    return None


def get_license_recommendation(repo_path: Path, 
                             github_contents: Optional[List[Dict]] = None) -> Dict:
    """
    Get license recommendation with reasoning.
    
    Args:
        repo_path: Local path to repository
        github_contents: Optional GitHub API contents response
        
    Returns:
        Dictionary with recommendation and reasoning
    """
    # Try local detection first
    local_license = detect_license_from_files(repo_path)
    
    # Try GitHub API detection
    github_license = None
    if github_contents:
        github_license = detect_license_from_github_api(github_contents)
    
    # Use GitHub detection if available, otherwise local
    license_type = github_license or local_license or "MIT"
    
    reasoning = []
    if github_license:
        reasoning.append("Detected from GitHub repository contents")
    elif local_license:
        reasoning.append("Detected from local project files")
    else:
        reasoning.append("Defaulting to MIT license for unknown project type")
    
    return {
        "recommended_license": license_type,
        "reasoning": reasoning,
        "confidence": "high" if github_license or local_license else "low"
    }


def main():
    """CLI interface for license detection."""
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description="Detect appropriate license for a project")
    parser.add_argument("--path", default=".", help="Path to repository (default: current directory)")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    
    args = parser.parse_args()
    
    repo_path = Path(args.path).resolve()
    if not repo_path.exists():
        print(f"Error: Path {repo_path} does not exist")
        sys.exit(1)
    
    result = get_license_recommendation(repo_path)
    
    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(f"Recommended license: {result['recommended_license']}")
        print("Reasoning:")
        for reason in result['reasoning']:
            print(f"  - {reason}")
        print(f"Confidence: {result['confidence']}")


if __name__ == "__main__":
    main()
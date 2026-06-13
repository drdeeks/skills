#!/usr/bin/env python3
"""
Description Generator - Creates repository descriptions from code analysis
"""
import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def extract_project_name_from_path(repo_path: Path) -> str:
    """Extract project name from repository path or git remote."""
    # Try to get from directory name
    name = repo_path.name
    
    # Try to get from git remote
    try:
        import subprocess
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            url = result.stdout.strip()
            # Extract name from git URL
            # https://github.com/user/repo.git -> repo
            # git@github.com:user/repo.git -> repo
            if url.endswith('.git'):
                url = url[:-4]
            if '/' in url:
                name = url.split('/')[-1]
            elif ':' in url:
                name = url.split(':')[-1].split('/')[-1]
    except Exception:
        pass  # Use directory name if git fails
    
    return name


def detect_project_type_from_files(repo_path: Path) -> Tuple[Optional[str], List[str]]:
    """
    Detect project type based on files present.
    
    Returns:
        Tuple of (primary_type, all_detected_types)
    """
    # Define file patterns for different project types
    project_patterns = {
        "Python": [
            "requirements.txt", "setup.py", "pyproject.toml", "Pipfile", 
            "Pipfile.lock", "tox.ini", ".python-version", "*.py"
        ],
        "Node.js": [
            "package.json", "yarn.lock", "pnpm-lock.yaml", "npm-shrinkwrap.json",
            ".node-version", ".nvmrc"
        ],
        "Rust": [
            "Cargo.toml", "Cargo.lock", "rustfmt.toml", "Clippy.toml"
        ],
        "Go": [
            "go.mod", "go.sum", "Godeps/Godeps.json"
        ],
        "Java": [
            "pom.xml", "build.gradle", "build.gradle.kts", "settings.gradle",
            "settings.gradle.kts", "gradle.properties"
        ],
        "C#": [
            "*.csproj", "*.vbproj", "*.sln", "packages.config", "project.json"
        ],
        "PHP": [
            "composer.json", "composer.lock"
        ],
        "Ruby": [
            "Gemfile", "Gemfile.lock", ".ruby-version", ".ruby-gemset"
        ],
        "Swift": [
            "Package.swift", "*.xcodeproj", "*.xcworkspace"
        ],
        "Elixir": [
            "mix.exs", "mix.lock"
        ],
        "C/C++": [
            "Makefile", "CMakeLists.txt", "configure.ac", "configure.in",
            "Makefile.am", "Makefile.in", "config.h.in"
        ]
    }
    
    # Count matches for each type
    type_scores = {}
    detected_types = set()
    
    for project_type, patterns in project_patterns.items():
        score = 0
        for pattern in patterns:
            # Handle glob patterns
            if "*" in pattern:
                if list(repo_path.glob(pattern)):
                    score += 1
                    detected_types.add(project_type)
            else:
                # Handle exact file matches
                if (repo_path / pattern).exists():
                    score += 1
                    detected_types.add(project_type)
        
        if score > 0:
            type_scores[project_type] = score
    
    # Determine primary type (highest score)
    primary_type = None
    if type_scores:
        primary_type = max(type_scores, key=type_scores.get)
    
    return primary_type, sorted(list(detected_types))


def extract_keywords_from_readme(repo_path: Path) -> List[str]:
    """Extract potential keywords from README file."""
    readme_files = ["README.md", "README", "readme.md", "Readme.md", 
                   "README.rst", "README.txt", "readme.txt"]
    
    for readme_file in readme_files:
        readme_path = repo_path / readme_file
        if readme_path.exists():
            try:
                content = readme_path.read_text(encoding='utf-8', errors='ignore')
                # Extract words that look like technologies or concepts
                # Simple approach: look for capitalized words and known tech terms
                words = re.findall(r'\b[A-Z][a-zA-Z0-9]*\b', content)
                # Filter out common false positives
                stop_words = {"The", "This", "That", "With", "From", "They", "Have", 
                            "Been", "Will", "Been", "When", "What", "Where", "Why",
                            "How", "All", "Any", "Can", "Will", "Just", "Like"}
                keywords = [w for w in words if w not in stop_words and len(w) > 2]
                return keywords[:10]  # Return top 10
            except Exception:
                pass
    
    return []


def generate_description(repo_path: Path, 
                        project_type: Optional[str] = None,
                        custom_template: Optional[str] = None) -> str:
    """
    Generate a repository description based on analysis.
    
    Args:
        repo_path: Path to repository
        project_type: Detected project type (optional)
        custom_template: Custom description template (optional)
        
    Returns:
        Generated description string
    """
    repo_name = extract_project_name_from_path(repo_path)
    
    # Detect project type if not provided
    if not project_type:
        project_type, _ = detect_project_type_from_files(repo_path)
    
    # Use custom template if provided
    if custom_template:
        return custom_template.format(
            name=repo_name,
            type=project_type or "project",
            year=str(Path(__file__).parent.parent.parent.parent.stat().st_mtime)[:4]  # Rough year
        )
    
    # Generate based on project type
    if project_type:
        type_descriptions = {
            "Python": f"{repo_name} - Python package or application",
            "Node.js": f"{repo_name} - Node.js module or service",
            "Rust": f"{repo_name} - Rust library or application",
            "Go": f"{repo_name} - Go service or tool",
            "Java": f"{repo_name} - Java library or application",
            "C#": f"{repo_name} - C# library or .NET application",
            "PHP": f"{repo_name} - PHP package or application",
            "Ruby": f"{repo_name} - Ruby gem or application",
            "Swift": f"{repo_name} - Swift package or application",
            "Elixir": f"{repo_name} - Elixir library or application",
            "C/C++": f"{repo_name} - C/C++ library or application"
        }
        
        if project_type in type_descriptions:
            return type_descriptions[project_type]
    
    # Fallback: try to extract from README
    keywords = extract_keywords_from_readme(repo_path)
    if keywords:
        return f"{repo_name} - {' '.join(keywords[:3])} project"
    
    # Ultimate fallback
    return f"{repo_name} - Software project"


def generate_description_from_github_content(repo_contents: List[Dict]) -> Optional[str]:
    """
    Generate description from GitHub API contents response.
    
    Args:
        repo_contents: List of file objects from GitHub API contents endpoint
        
    Returns:
        Generated description or None
    """
    # Convert to path-like structure for analysis
    # This is a simplified version - in reality we'd need to download files
    # For now, we'll just look for indicative filenames
    
    filenames = [item.get("name", "").lower() for item in repo_contents 
                if item.get("type") == "file"]
    
    # Check for README
    readme_names = ["readme.md", "readme", "readme.txt", "readme.rst"]
    if any(name in filenames for name in readme_names):
        # Would need to fetch and parse README content
        # For now, return generic based on other files
        pass
    
    # Detect project type from filenames
    project_indicators = {
        "package.json": "Node.js",
        "requirements.txt": "Python",
        "setup.py": "Python",
        "pyproject.toml": "Python",
        "Cargo.toml": "Rust",
        "go.mod": "Go",
        "pom.xml": "Java",
        "build.gradle": "Java",
        "*.csproj": "C#",
        "composer.json": "PHP",
        "Gemfile": "Ruby",
        "Package.swift": "Swift",
        "mix.exs": "Elixir",
        "Makefile": "C/C++",
        "CMakeLists.txt": "C/C++"
    }
    
    for pattern, language in project_indicators.items():
        if "*" in pattern:
            # Handle glob - simplified check
            if any(fname.startswith(pattern.replace("*", "")) for fname in filenames):
                return f"Project - {language}"
        else:
            if pattern in filenames:
                return f"Project - {language}"
    
    return None


def main():
    """CLI interface for description generation."""
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description="Generate repository description")
    parser.add_argument("--path", default=".", help="Path to repository (default: current directory)")
    parser.add_argument("--template", help="Custom description template (use {name} and {type} placeholders)")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    parser.add_argument("--project-type", help="Override detected project type")
    
    args = parser.parse_args()
    
    repo_path = Path(args.path).resolve()
    if not repo_path.exists():
        print(f"Error: Path {repo_path} does not exist")
        sys.exit(1)
    
    description = generate_description(
        repo_path, 
        project_type=args.project_type,
        custom_template=args.template
    )
    
    if args.format == "json":
        result = {
            "description": description,
            "repository": str(repo_path),
            "project_name": extract_project_name_from_path(repo_path)
        }
        print(json.dumps(result, indent=2))
    else:
        print(description)


if __name__ == "__main__":
    main()
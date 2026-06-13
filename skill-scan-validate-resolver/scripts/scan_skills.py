#!/usr/bin/env python3
"""
Scan multiple directories for skills and identify missing ones in target.
"""

import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Set
from datetime import datetime

def scan_directory(directory: Path) -> Set[str]:
    """Scan a directory for skill subdirectories."""
    skills = set()
    if not directory.exists():
        return skills
    for item in directory.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            # Check if it looks like a skill (has SKILL.md or is a directory)
            if (item / 'SKILL.md').exists() or any(item.iterdir()):
                skills.add(item.name)
    return skills

def find_skill_files(skill_dir: Path) -> List[Path]:
    """Find all files in a skill directory."""
    files = []
    if skill_dir.exists():
        for item in skill_dir.rglob('*'):
            if item.is_file():
                files.append(item)
    return files

def scan_sources(sources: List[str], target: str) -> Dict:
    """Scan source directories and compare with target."""
    target_path = Path(target)
    target_skills = scan_directory(target_path)
    
    all_source_skills = {}
    new_skills = {}
    
    for source in sources:
        source_path = Path(source)
        source_skills = scan_directory(source_path)
        all_source_skills[source] = source_skills
        
        for skill in source_skills:
            if skill not in target_skills:
                if skill not in new_skills:
                    new_skills[skill] = []
                new_skills[skill].append(source)
    
    return {
        'target': target,
        'target_skills': sorted(target_skills),
        'sources': {s: sorted(skills) for s, skills in all_source_skills.items()},
        'new_skills': {k: v for k, v in sorted(new_skills.items())},
        'timestamp': datetime.now().isoformat()
    }

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Scan for skills')
    parser.add_argument('--sources', nargs='+', required=True, help='Source directories to scan')
    parser.add_argument('--target', required=True, help='Target skills directory')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    args = parser.parse_args()
    
    result = scan_sources(args.sources, args.target)
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"=== Skill Scan Report ===")
        print(f"Target: {result['target']}")
        print(f"Target skills: {len(result['target_skills'])}")
        print(f"\nSource directories:")
        for source, skills in result['sources'].items():
            print(f"  {source}: {len(skills)} skills")
        print(f"\nNew skills to copy: {len(result['new_skills'])}")
        if result['new_skills']:
            for skill, sources in result['new_skills'].items():
                print(f"  - {skill} (from: {', '.join(sources)})")

if __name__ == '__main__':
    main()

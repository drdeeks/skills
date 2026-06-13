#!/usr/bin/env python3
"""
Generate comprehensive audit reports for skills.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime

def scan_skill_categories(target_dir: Path) -> Dict:
    """Categorize skills by their type/focus."""
    categories = {
        'blockchain': [],
        'creativity': [],
        'agent-first': [],
        'knowledge': [],
        'infrastructure': [],
        'media': [],
        'productivity': [],
        'software-development': [],
        'agent-infrastructure': [],
        'other': []
    }
    
    # Keywords for categorization
    keywords = {
        'blockchain': ['blockchain', 'web3', 'crypto', 'nft', 'defi', 'token', 'wallet', 'erc', 'chain'],
        'creativity': ['creative', 'art', 'design', 'video', 'audio', 'music', 'writing', 'content'],
        'agent-first': ['agent', 'autonomous', 'multi-agent', 'subagent', 'orchestrat'],
        'knowledge': ['knowledge', 'index', 'search', 'documentation', 'learn'],
        'infrastructure': ['infra', 'deploy', 'docker', 'kubernetes', 'server', 'hosting'],
        'media': ['media', 'gif', 'image', 'photo', 'video', 'youtube'],
        'productivity': ['productivity', 'workspace', 'calendar', 'email', 'task', 'project'],
        'software-development': ['develop', 'code', 'debug', 'test', 'review', 'plan'],
        'agent-infrastructure': ['agent-mail', 'base-agent', 'bootstrap', 'registration']
    }
    
    for skill_dir in sorted(target_dir.iterdir()):
        if not skill_dir.is_dir() or skill_dir.name.startswith('.'):
            continue
        
        skill_name = skill_dir.name.lower()
        categorized = False
        
        # Check keywords
        for category, kws in keywords.items():
            for kw in kws:
                if kw in skill_name:
                    categories[category].append(skill_dir.name)
                    categorized = True
                    break
            if categorized:
                break
        
        if not categorized:
            categories['other'].append(skill_dir.name)
    
    return categories

def generate_report(target_dir: str) -> Dict:
    """Generate comprehensive audit report."""
    target_path = Path(target_dir)
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'target': target_dir,
        'summary': {
            'total_skills': 0,
            'valid_skills': 0,
            'skills_by_category': {}
        },
        'categories': {},
        'validation_results': [],
        'hardcoded_issues': []
    }
    
    # Count skills
    for skill_dir in target_path.iterdir():
        if skill_dir.is_dir() and not skill_dir.name.startswith('.'):
            report['summary']['total_skills'] += 1
    
    # Categorize
    categories = scan_skill_categories(target_path)
    for cat, skills in categories.items():
        report['categories'][cat] = skills
        report['summary']['skills_by_category'][cat] = len(skills)
    
    # Validate each skill
    for skill_dir in sorted(target_path.iterdir()):
        if not skill_dir.is_dir() or skill_dir.name.startswith('.'):
            continue
        
        skill_md = skill_dir / 'SKILL.md'
        if skill_md.exists():
            report['summary']['valid_skills'] += 1
            report['validation_results'].append({
                'name': skill_dir.name,
                'status': 'valid'
            })
    
    return report

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Generate report')
    parser.add_argument('--target', required=True, help='Target directory')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    args = parser.parse_args()
    
    target_path = Path(args.target)
    if not target_path.exists():
        print(f'Error: Target directory not found: {args.target}')
        sys.exit(1)
    
    report = generate_report(args.target)
    
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"=== Skill Audit Report ===")
        print(f"Generated: {report['timestamp']}")
        print(f"Target: {report['target']}")
        print()
        print(f"=== Summary ===")
        print(f"Total skills: {report['summary']['total_skills']}")
        print(f"Valid skills: {report['summary']['valid_skills']}")
        print()
        print(f"=== Skills by Category ===")
        for cat, count in report['summary']['skills_by_category'].items():
            print(f"  {cat}: {count}")
        print()
        print(f"=== Category Details ===")
        for cat, skills in report['categories'].items():
            if skills:
                print(f"\n{cat.upper()} ({len(skills)}):")
                for skill in skills:
                    print(f"  - {skill}")

if __name__ == '__main__':
    main()

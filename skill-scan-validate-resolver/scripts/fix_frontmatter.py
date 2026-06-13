#!/usr/bin/env python3
"""
Fix SKILL.md frontmatter issues.
"""

import os
import sys
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime

try:
    import yaml
except ModuleNotFoundError:
    yaml = None

ALLOWED_PROPERTIES = {'name', 'description', 'license', 'metadata', 'allowed-tools'}

def extract_frontmatter(content: str) -> Tuple[Optional[str], str]:
    """Extract YAML frontmatter and return it with the body."""
    lines = content.splitlines()
    if not lines or lines[0].strip() != '---':
        return None, content
    
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            frontmatter = '\n'.join(lines[1:i])
            body = '\n'.join(lines[i+1:])
            return frontmatter, body
    
    return None, content

def fix_frontmatter(frontmatter_text: str) -> Tuple[str, List[str]]:
    """Fix frontmatter by removing invalid keys."""
    fixes = []
    
    if yaml is not None:
        try:
            frontmatter = yaml.safe_load(frontmatter_text)
            if not isinstance(frontmatter, dict):
                return frontmatter_text, ['Invalid YAML structure']
        except yaml.YAMLError:
            return frontmatter_text, ['Invalid YAML syntax']
    else:
        # Basic parsing without PyYAML
        frontmatter = {}
        for line in frontmatter_text.splitlines():
            if ':' in line:
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip()
    
    # Remove invalid keys
    original_keys = set(frontmatter.keys())
    invalid_keys = original_keys - ALLOWED_PROPERTIES
    
    if invalid_keys:
        for key in invalid_keys:
            del frontmatter[key]
            fixes.append(f'Removed invalid key: {key}')
    
    # Ensure required keys exist
    if 'name' not in frontmatter:
        fixes.append('Missing required key: name')
    if 'description' not in frontmatter:
        fixes.append('Missing required key: description')
    
    # Reconstruct frontmatter
    if yaml is not None:
        fixed = yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True)
    else:
        fixed = ''
        for key, value in frontmatter.items():
            if ' ' in str(value) or ':' in str(value):
                fixed += f'{key}: "{value}"\n'
            else:
                fixed += f'{key}: {value}\n'
    
    return fixed, fixes

def fix_skill_md(file_path: Path, dry_run: bool = True) -> Tuple[bool, List[str]]:
    """Fix a SKILL.md file."""
    try:
        content = file_path.read_text(encoding='utf-8')
        frontmatter_text, body = extract_frontmatter(content)
        
        if frontmatter_text is None:
            return False, ['No valid frontmatter found']
        
        fixed_frontmatter, fixes = fix_frontmatter(frontmatter_text)
        
        if fixes:
            if not dry_run:
                new_content = f'---\n{fixed_frontmatter}---\n{body}'
                file_path.write_text(new_content, encoding='utf-8')
                return True, fixes
            else:
                return True, [f'Would fix: {", ".join(fixes)}']
        
        return False, ['No fixes needed']
    except Exception as e:
        return False, [f'Error: {e}']

def scan_directory(target_dir: Path, dry_run: bool = True) -> Dict:
    """Scan all SKILL.md files for frontmatter issues."""
    results = {
        'target': str(target_dir),
        'timestamp': datetime.now().isoformat(),
        'dry_run': dry_run,
        'files_scanned': 0,
        'files_with_issues': 0,
        'total_fixes': 0,
        'fixes': []
    }
    
    for file_path in target_dir.rglob('SKILL.md'):
        if file_path.is_file():
            results['files_scanned'] += 1
            fixed, fixes = fix_skill_md(file_path, dry_run)
            
            if fixes:
                results['files_with_issues'] += 1
                results['total_fixes'] += len(fixes)
                results['fixes'].append({
                    'file': str(file_path.relative_to(target_dir)),
                    'fixed': fixed,
                    'fixes': fixes
                })
    
    return results

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Fix frontmatter')
    parser.add_argument('--target', required=True, help='Target directory')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    args = parser.parse_args()
    
    target_path = Path(args.target)
    if not target_path.exists():
        print(f'Error: Target directory not found: {args.target}')
        sys.exit(1)
    
    results = scan_directory(target_path, args.dry_run)
    
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(f"=== Frontmatter Fix Report ===")
        print(f"Target: {results['target']}")
        print(f"Dry run: {results['dry_run']}")
        print(f"Files scanned: {results['files_scanned']}")
        print(f"Files with issues: {results['files_with_issues']}")
        print(f"Total fixes: {results['total_fixes']}")
        print()
        
        for fix in results['fixes']:
            status = '✓' if fix['fixed'] else '✗'
            print(f"{status} {fix['file']}")
            for f in fix['fixes']:
                print(f"    {f}")

if __name__ == '__main__':
    main()

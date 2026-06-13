#!/usr/bin/env python3
"""
Detect and fix hardcoded paths in skill files.
"""

import os
import sys
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

# Hardcoded patterns to find and their replacements
HARDCODED_PATTERNS = [
    # Home directories
    (r'/home/\w+/', '${HOME}/'),
    (r'${HOME}/', '${HOME}/'),
    
    # Common hardcoded paths
    (r'${TELEGRAM_BOT_DIR:-$HOME/.config/opencode/bots/}/', '${TELEGRAM_BOT_DIR:-$HOME/.config/opencode/bots/}/'),
    (r'/opt/\w+/', '/opt/${PACKAGE_NAME}/'),
    
    # OpenClaw/Hermes specific
    (r'${OPENCLAW_DIR:-~/.openclaw}/', '${OPENCLAW_DIR:-~/.openclaw}/'),
    (r'${HERMES_DIR:-~/.hermes}/', '${HERMES_DIR:-~/.hermes}/'),
    (r'${OPENCODE_DIR:-~/.config/opencode}/', '${OPENCODE_DIR:-~/.config/opencode}/'),
    
    # Temp directories
    (r'/tmp/\w+/', '${TMPDIR:-/tmp}/'),
]

def scan_file(file_path: Path) -> List[Dict]:
    """Scan a file for hardcoded paths."""
    issues = []
    try:
        content = file_path.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            for pattern, replacement in HARDCODED_PATTERNS:
                matches = list(re.finditer(pattern, line))
                if matches:
                    issues.append({
                        'file': str(file_path),
                        'line': line_num,
                        'pattern': pattern,
                        'replacement': replacement,
                        'original': line.strip(),
                        'match': matches[0].group()
                    })
    except Exception as e:
        pass
    
    return issues

def fix_file(file_path: Path, dry_run: bool = True) -> Tuple[bool, str]:
    """Fix hardcoded paths in a file."""
    try:
        content = file_path.read_text(encoding='utf-8')
        original = content
        
        for pattern, replacement in HARDCODED_PATTERNS:
            content = re.sub(pattern, replacement, content)
        
        if content != original:
            if not dry_run:
                file_path.write_text(content, encoding='utf-8')
                return True, f'Fixed {file_path}'
            else:
                return True, f'Would fix {file_path}'
        else:
            return False, f'No changes needed for {file_path}'
    except Exception as e:
        return False, f'Error processing {file_path}: {e}'

def scan_directory(target_dir: Path, dry_run: bool = True) -> Dict:
    """Scan all files in directory for hardcoded paths."""
    results = {
        'target': str(target_dir),
        'timestamp': datetime.now().isoformat(),
        'dry_run': dry_run,
        'files_scanned': 0,
        'files_with_issues': 0,
        'total_issues': 0,
        'issues': [],
        'fixes': []
    }
    
    for file_path in target_dir.rglob('*'):
        if file_path.is_file() and file_path.suffix in ['.md', '.py', '.sh', '.yaml', '.yml', '.json']:
            results['files_scanned'] += 1
            issues = scan_file(file_path)
            
            if issues:
                results['files_with_issues'] += 1
                results['total_issues'] += len(issues)
                results['issues'].extend(issues)
                
                # Try to fix
                fixed, message = fix_file(file_path, dry_run)
                if fixed:
                    results['fixes'].append(message)
    
    return results

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Fix hardcoded paths')
    parser.add_argument('--target', required=True, help='Target directory')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without fixing')
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
        print(f"=== Hardcoded Path Scan ===")
        print(f"Target: {results['target']}")
        print(f"Dry run: {results['dry_run']}")
        print(f"Files scanned: {results['files_scanned']}")
        print(f"Files with issues: {results['files_with_issues']}")
        print(f"Total issues: {results['total_issues']}")
        print()
        
        if results['issues']:
            print("Issues found:")
            for issue in results['issues'][:20]:  # Show first 20
                print(f"  {issue['file']}:{issue['line']} - {issue['match']}")
            if len(results['issues']) > 20:
                print(f"  ... and {len(results['issues']) - 20} more")
            print()
        
        if results['fixes']:
            print("Fixes applied:")
            for fix in results['fixes']:
                print(f"  {fix}")

if __name__ == '__main__':
    main()

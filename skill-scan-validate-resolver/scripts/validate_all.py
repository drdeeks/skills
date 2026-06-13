#!/usr/bin/env python3
"""
Validate all skills in a directory against skill-creator standards.
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime

try:
    import yaml
except ModuleNotFoundError:
    yaml = None

MAX_SKILL_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 1024
ALLOWED_PROPERTIES = {'name', 'description', 'license', 'metadata', 'allowed-tools', 'version'}

def extract_frontmatter(content: str) -> Optional[str]:
    """Extract YAML frontmatter from SKILL.md."""
    lines = content.splitlines()
    if not lines or lines[0].strip() != '---':
        return None
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            return '\n'.join(lines[1:i])
    return None

def validate_frontmatter(frontmatter_text: str) -> Tuple[bool, str, Dict]:
    """Validate YAML frontmatter."""
    if yaml is not None:
        try:
            frontmatter = yaml.safe_load(frontmatter_text)
            if not isinstance(frontmatter, dict):
                return False, "Frontmatter must be a YAML dictionary", {}
        except yaml.YAMLError as e:
            return False, f"Invalid YAML: {e}", {}
    else:
        # Basic validation without PyYAML
        frontmatter = {}
        for line in frontmatter_text.splitlines():
            if ':' in line:
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip()
    
    # Check for unexpected keys
    unexpected = set(frontmatter.keys()) - ALLOWED_PROPERTIES
    if unexpected:
        return False, f"Unexpected keys: {', '.join(sorted(unexpected))}", frontmatter
    
    # Check required keys
    if 'name' not in frontmatter:
        return False, "Missing 'name'", frontmatter
    if 'description' not in frontmatter:
        return False, "Missing 'description'", frontmatter
    
    # Validate name
    name = frontmatter.get('name', '')
    if not isinstance(name, str):
        return False, f"Name must be a string, got {type(name).__name__}", frontmatter
    name = name.strip()
    if name:
        if not re.match(r'^[a-z0-9-]+$', name):
            return False, f"Name '{name}' should be hyphen-case", frontmatter
        if name.startswith('-') or name.endswith('-') or '--' in name:
            return False, f"Name '{name}' invalid format", frontmatter
        if len(name) > MAX_SKILL_NAME_LENGTH:
            return False, f"Name too long ({len(name)} chars)", frontmatter
    
    # Validate description
    desc = frontmatter.get('description', '')
    if not isinstance(desc, str):
        return False, f"Description must be a string", frontmatter
    desc = desc.strip()
    if desc:
        if '<' in desc or '>' in desc:
            return False, "Description cannot contain angle brackets", frontmatter
        if len(desc) > MAX_DESCRIPTION_LENGTH:
            return False, f"Description too long ({len(desc)} chars)", frontmatter
    
    return True, "Valid", frontmatter

def check_hardcoded_paths(skill_dir: Path) -> List[Dict]:
    """Check for hardcoded paths in skill files."""
    issues = []
    hardcoded_patterns = [
        r'/home/\w+/',
        r'${HOME}/',
        r'/opt/\w+/',
        r'/tmp/\w+/',
        r'${OPENCLAW_DIR:-~/.openclaw}/',
        r'${HERMES_DIR:-~/.hermes}/',
        r'${OPENCODE_DIR:-~/.config/opencode}/',
    ]
    
    for file_path in skill_dir.rglob('*'):
        if file_path.is_file() and file_path.suffix in ['.md', '.py', '.sh', '.yaml', '.yml', '.json']:
            # Skip the skill's own scripts (they contain patterns for finding/replacing hardcoded paths)
            try:
                rel_path = file_path.relative_to(skill_dir)
                if str(rel_path).startswith('scripts/') and 'skill-scan-validate-resolver' in str(skill_dir):
                    continue
            except ValueError:
                pass
            try:
                content = file_path.read_text(encoding='utf-8')
                for pattern in hardcoded_patterns:
                    matches = re.findall(pattern, content)
                    if matches:
                        issues.append({
                            'file': str(file_path.relative_to(skill_dir)),
                            'pattern': pattern,
                            'count': len(matches)
                        })
            except Exception:
                pass
    
    return issues

def validate_skill(skill_path: Path) -> Dict:
    """Validate a single skill."""
    result = {
        'name': skill_path.name,
        'path': str(skill_path),
        'valid': False,
        'message': '',
        'frontmatter': {},
        'hardcoded_issues': [],
        'metadata_valid': False,
        'has_skill_file': False,
        'has_init_py': False,
        'files_checked': 0
    }
    
    skill_md = skill_path / 'SKILL.md'
    if not skill_md.exists():
        result['message'] = 'SKILL.md not found'
        return result
    
    # Check for __init__.py
    init_py = skill_path / '__init__.py'
    if init_py.exists():
        result['has_init_py'] = True
    else:
        result['message'] = 'Missing __init__.py (required for production)'
        return result
    
    try:
        content = skill_md.read_text(encoding='utf-8')
        result['files_checked'] = 1
    except Exception as e:
        result['message'] = f'Could not read SKILL.md: {e}'
        return result
    
    frontmatter_text = extract_frontmatter(content)
    if frontmatter_text is None:
        result['message'] = 'Invalid frontmatter format'
        return result
    
    valid, message, frontmatter = validate_frontmatter(frontmatter_text)
    result['valid'] = valid
    result['message'] = message
    result['frontmatter'] = frontmatter
    
    # Check for .skill file and metadata
    skill_file = skill_path / f"{skill_path.name}.skill"
    if skill_file.exists():
        result['has_skill_file'] = True
        # Check for metadata in .skill file
        try:
            import zipfile
            with zipfile.ZipFile(skill_file, 'r') as zf:
                if '__skill_metadata.json' in zf.namelist():
                    with zf.open('__skill_metadata.json') as f:
                        metadata = json.load(f)
                        # Validate metadata structure
                        required_fields = ['skill_name', 'version', 'packaged_at', 'files_count', 'size_bytes']
                        if all(field in metadata for field in required_fields):
                            result['metadata_valid'] = True
                            result['metadata'] = metadata
                        else:
                            result['message'] = f"Invalid metadata structure in {skill_file.name}"
                else:
                    result['message'] = f"Missing __skill_metadata.json in {skill_file.name}"
        except Exception as e:
            result['message'] = f"Error reading .skill file: {e}"
    else:
        result['message'] = f"Missing {skill_path.name}.skill file"
    
    # Check for hardcoded paths
    result['hardcoded_issues'] = check_hardcoded_paths(skill_path)
    
    return result

def validate_all(target_dir: str, fix: bool = False, report: bool = False) -> Dict:
    """Validate all skills in target directory."""
    target_path = Path(target_dir)
    if not target_path.exists():
        return {'error': f'Target directory not found: {target_dir}'}
    
    results = {
        'target': target_dir,
        'timestamp': datetime.now().isoformat(),
        'skills': [],
        'summary': {
            'total': 0,
            'valid': 0,
            'invalid': 0,
            'hardcoded_issues': 0,
            'with_metadata': 0,
            'without_metadata': 0,
            'with_init_py': 0,
            'without_init_py': 0
        }
    }
    
    for skill_dir in sorted(target_path.iterdir()):
        if skill_dir.is_dir() and not skill_dir.name.startswith('.'):
            result = validate_skill(skill_dir)
            results['skills'].append(result)
            results['summary']['total'] += 1
            if result['valid']:
                results['summary']['valid'] += 1
            else:
                results['summary']['invalid'] += 1
            if result['hardcoded_issues']:
                results['summary']['hardcoded_issues'] += 1
            if result['metadata_valid']:
                results['summary']['with_metadata'] += 1
            else:
                results['summary']['without_metadata'] += 1
            if result['has_init_py']:
                results['summary']['with_init_py'] += 1
            else:
                results['summary']['without_init_py'] += 1
    
    return results

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Validate skills')
    parser.add_argument('--target', required=True, help='Target skills directory')
    parser.add_argument('--fix', action='store_true', help='Attempt to fix issues')
    parser.add_argument('--report', action='store_true', help='Generate report')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    args = parser.parse_args()
    
    results = validate_all(args.target, args.fix, args.report)
    
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(f"=== Skill Validation Report ===")
        print(f"Target: {results['target']}")
        print(f"Total skills: {results['summary']['total']}")
        print(f"Valid: {results['summary']['valid']}")
        print(f"Invalid: {results['summary']['invalid']}")
        print(f"With hardcoded issues: {results['summary']['hardcoded_issues']}")
        print(f"With valid metadata: {results['summary']['with_metadata']}")
        print(f"Without valid metadata: {results['summary']['without_metadata']}")
        print(f"With __init__.py: {results['summary']['with_init_py']}")
        print(f"Without __init__.py: {results['summary']['without_init_py']}")
        print()
        
        for skill in results['skills']:
            status = '✓' if skill['valid'] else '✗'
            metadata_status = '✓' if skill['metadata_valid'] else '✗'
            init_status = '✓' if skill['has_init_py'] else '✗'
            print(f"{status} {skill['name']}: {skill['message']} [metadata: {metadata_status}] [init: {init_status}]")
            if skill['hardcoded_issues']:
                for issue in skill['hardcoded_issues']:
                    print(f"    Hardcoded: {issue['file']} ({issue['count']} instances)")

if __name__ == '__main__':
    main()

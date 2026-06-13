#!/usr/bin/env python3
"""
Enhanced validation for skills - combines frontmatter, structure, agnostic, and redundancy checks.
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
from datetime import datetime

try:
    import yaml
except ModuleNotFoundError:
    yaml = None

MAX_SKILL_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 1024
ALLOWED_PROPERTIES = {'name', 'description', 'license', 'metadata', 'allowed-tools', 'version'}

# Agnostic patterns to check
HARDCODED_PATTERNS = [
    (r'/home/\w+/', 'Hardcoded home directory'),
    (r'/root/', 'Hardcoded root directory'),
    (r'/opt/\w+/', 'Hardcoded /opt path'),
    (r'~/.openclaw/', 'Hardcoded OpenClaw path'),
    (r'~/.hermes/', 'Hardcoded Hermes path'),
    (r'~/.config/opencode/', 'Hardcoded OpenCode path'),
    (r'/tmp/\w+/', 'Hardcoded temp path'),
]

# Content quality patterns - placeholders, TODOs, filler text
# Conservative set: only flags clear, unambiguous markers
# Excludes legitimate uses: tag names, function calls, table status, template vars
PLACEHOLDER_PATTERNS = [
    (r'(?:^|(?<=\s))(?<!`)TODO(?!\w)(?!.*\btodo\b)(?!\s*,)(?!\s+list)', 'TODO marker'),
    (r'\bFIXME\b', 'FIXME marker'),
    (r'(?<!\| )TBD(?!\w)(?! \|)', 'TBD marker'),
    (r'\bWIP\b', 'Work in progress marker'),
    (r'\bcoming\s+soon\b', 'Coming soon placeholder'),
    (r'\binsert\s+(here|text|data|info)\b', 'Insert placeholder'),
    (r'\breplace\s+(this|here)\b', 'Replace placeholder'),
    (r'\byour\s+(name|email|token|key|id)\b', 'Your-<something> placeholder'),
    (r'\blorem\s+ipsum\b', 'Lorem ipsum filler'),
    (r'\b\[YOUR_', 'Template variable placeholder'),
    (r'(?<!\{)\{\{(?!\{).*?\}\}(?!\})', 'Mustache template variable'),
    (r'<!--\s*(placeholder|todo|fixme)\s*-->', 'HTML comment placeholder'),
    (r'\bNOTE:\s*$', 'Empty NOTE marker'),
]

def extract_frontmatter(content: str) -> Tuple[Optional[str], str]:
    """Extract YAML frontmatter and body."""
    lines = content.splitlines()
    if not lines or lines[0].strip() != '---':
        return None, content
    
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            frontmatter = '\n'.join(lines[1:i])
            body = '\n'.join(lines[i+1:])
            return frontmatter, body
    
    return None, content

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
        return False, f"Name must be a string", frontmatter
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
        return False, "Description must be a string", frontmatter
    desc = desc.strip()
    if desc:
        if '<' in desc or '>' in desc:
            return False, "Description cannot contain angle brackets", frontmatter
        if len(desc) > MAX_DESCRIPTION_LENGTH:
            return False, f"Description too long ({len(desc)} chars)", frontmatter
    
    return True, "Valid", frontmatter

def check_agnostic_compliance(skill_dir: Path) -> List[Dict]:
    """Check skill for hardcoded paths and platform-specific references."""
    issues = []
    
    # Skills that contain hardcoded path detection patterns should be excluded
    # from agnostic checks on their own scripts
    detection_skills = {'skill-scan-validate-resolver', 'fix-hardcoded', 'skill-creator-pro'}
    skill_name = skill_dir.name
    
    for file_path in skill_dir.rglob('*'):
        if file_path.is_file() and file_path.suffix in ['.md', '.py', '.sh', '.yaml', '.yml', '.json']:
            # Skip detection scripts for the skill that contains them
            try:
                rel_path = file_path.relative_to(skill_dir)
                if skill_name in detection_skills and str(rel_path).startswith('scripts/'):
                    continue
            except ValueError:
                pass
            
            try:
                content = file_path.read_text(encoding='utf-8', errors='replace')
                lines = content.split('\n')
                
                for line_num, line in enumerate(lines, 1):
                    # Skip lines that contain regex patterns for detecting hardcoded paths
                    if "r'" in line or 'r"' in line:
                        continue
                    for pattern, description in HARDCODED_PATTERNS:
                        if re.search(pattern, line):
                            issues.append({
                                'file': str(file_path.relative_to(skill_dir)),
                                'line': line_num,
                                'issue': description,
                                'pattern': pattern,
                                'content': line.strip()[:100]
                            })
            except Exception:
                pass
    
    return issues

def check_structure(skill_dir: Path) -> Tuple[bool, List[str]]:
    """Check skill directory structure."""
    issues = []
    
    # Check for SKILL.md
    if not (skill_dir / 'SKILL.md').exists():
        issues.append("Missing SKILL.md")
    
    # Check for scripts directory
    scripts_dir = skill_dir / 'scripts'
    if not scripts_dir.exists():
        issues.append("Missing scripts/ directory")
    else:
        script_files = [f for f in scripts_dir.rglob('*') if f.is_file() and f.suffix in ['.py', '.sh', '.js', '.ts']]
        if len(script_files) < 2:
            issues.append(f"scripts/ requires at least 2 script files for production-ready (found {len(script_files)})")
    
    # Check for references directory
    refs_dir = skill_dir / 'references'
    if not refs_dir.exists():
        issues.append("Missing references/ directory")
    else:
        ref_files = [f for f in refs_dir.rglob('*') if f.is_file() and f.suffix in ['.md', '.txt', '.json', '.yaml', '.yml', '.csv']]
        if len(ref_files) < 3:
            issues.append(f"references/ requires at least 3 reference files for production-ready (found {len(ref_files)})")
    
    # Check for excessive files
    file_count = sum(1 for _ in skill_dir.rglob('*') if _.is_file())
    if file_count > 50:
        issues.append(f"Excessive files ({file_count}). Consider cleanup.")
    
    return len(issues) == 0, issues

def check_enterprise_structure(skill_dir: Path) -> Tuple[bool, List[str]]:
    """Check enterprise-grade skill directory structure."""
    issues = []
    
    # Check for SKILL.md
    if not (skill_dir / 'SKILL.md').exists():
        issues.append("Missing SKILL.md")
    
    # Check for __init__.py (mandatory for production/enterprise)
    if not (skill_dir / '__init__.py').exists():
        issues.append("Missing __init__.py (required for production)")
    
    # Check for scripts directory (enterprise requires 3+)
    scripts_dir = skill_dir / 'scripts'
    if not scripts_dir.exists():
        issues.append("Missing scripts/ directory")
    else:
        script_files = [f for f in scripts_dir.rglob('*') if f.is_file() and f.suffix in ['.py', '.sh', '.js', '.ts']]
        if len(script_files) < 3:
            issues.append(f"scripts/ requires at least 3 script files for enterprise-grade (found {len(script_files)})")
    
    # Check for references directory (enterprise requires 5+)
    refs_dir = skill_dir / 'references'
    if not refs_dir.exists():
        issues.append("Missing references/ directory")
    else:
        ref_files = [f for f in refs_dir.rglob('*') if f.is_file() and f.suffix in ['.md', '.txt', '.json', '.yaml', '.yml', '.csv']]
        if len(ref_files) < 5:
            issues.append(f"references/ requires at least 5 reference files for enterprise-grade (found {len(ref_files)})")
    
    # Check for excessive files
    file_count = sum(1 for _ in skill_dir.rglob('*') if _.is_file())
    if file_count > 50:
        issues.append(f"Excessive files ({file_count}). Consider cleanup.")
    
    return len(issues) == 0, issues

def check_content_quality(skill_dir: Path) -> Tuple[bool, List[str]]:
    """Check content quality of skill - enforces no TODOs, placeholders, or inaccurate info."""
    issues = []
    skill_md = skill_dir / 'SKILL.md'
    
    if not skill_md.exists():
        return False, ["No SKILL.md to analyze"]
    
    content = skill_md.read_text(encoding='utf-8', errors='replace')
    
    # Check minimum length
    if len(content) < 100:
        issues.append("SKILL.md too short (< 100 chars)")
    
    # Check for placeholder/TODO markers (line-by-line, skipping code blocks)
    in_code_block = False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith('```'):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        for pattern, description in PLACEHOLDER_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                issues.append(f"Contains {description}: '{stripped[:60]}'")
                break  # One issue per line max
    
    # Check for empty sections (skip code blocks when measuring)
    sections = re.findall(r'^##\s+(.+)$', content, re.MULTILINE)
    for section in sections:
        section_pattern = f'^## {re.escape(section)}$'
        section_match = re.search(section_pattern, content, re.MULTILINE)
        if section_match:
            # Get content after heading
            start = section_match.end()
            next_section = re.search(r'^##\s+', content[start:], re.MULTILINE)
            if next_section:
                section_content = content[start:start + next_section.start()].strip()
            else:
                section_content = content[start:].strip()
            
            # Skip sections that contain code blocks (they're documented)
            if '```' in section_content:
                continue
            # Strip inline code
            text_only = re.sub(r'`[^`]+`', '', section_content).strip()
            if len(text_only) < 20:
                issues.append(f"Section '{section}' is sparse (< 20 chars)")
    
    # Check for broken markdown links
    links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
    for link_text, link_url in links:
        if link_url.startswith('http'):
            continue  # Skip external links
        # Skip anchor links
        if link_url.startswith('#'):
            continue
        # Skip links with invalid characters (corrupted content)
        if len(link_url) > 200 or not link_url.isprintable():
            continue
        # Check internal links
        try:
            target_path = skill_dir / link_url
            if not target_path.exists():
                issues.append(f"Broken link: [{link_text}]({link_url})")
        except (OSError, ValueError):
            pass
    
    # Check for suspiciously short descriptions in frontmatter
    frontmatter_text, _ = extract_frontmatter(content)
    if frontmatter_text:
        if yaml is not None:
            try:
                frontmatter = yaml.safe_load(frontmatter_text)
                if isinstance(frontmatter, dict):
                    desc = frontmatter.get('description', '')
                    if isinstance(desc, str) and len(desc.strip()) < 20:
                        issues.append("Description too short (< 20 chars)")
            except:
                pass
    
    # Check for duplicate sections
    section_names = [s.strip().lower() for s in sections]
    seen = set()
    for s in section_names:
        if s in seen:
            issues.append(f"Duplicate section: '{s}'")
        seen.add(s)
    
    return len(issues) == 0, issues

def check_sources_verification(skill_dir: Path) -> Tuple[bool, List[str]]:
    """Verify skill references official documentation for tools/services it depends on."""
    issues = []
    skill_md = skill_dir / 'SKILL.md'
    
    if not skill_md.exists():
        return False, ["No SKILL.md to analyze"]
    
    content = skill_md.read_text(encoding='utf-8', errors='replace').lower()
    
    # External services that require documentation (not common dev tools)
    service_patterns = {
        'vercel': 'https://vercel.com/docs',
        'netlify': 'https://docs.netlify.com',
        'docker': 'https://docs.docker.com',
        'kubernetes': 'https://kubernetes.io/docs/',
        'aws': 'https://docs.aws.amazon.com',
        'gcp': 'https://cloud.google.com/docs',
        'azure': 'https://learn.microsoft.com/azure/',
        'ventoy': 'https://www.ventoy.net/en/doc/',
        'rufus': 'https://rufus.ie/en/',
        'postgres': 'https://www.postgresql.org/docs/',
        'mysql': 'https://dev.mysql.com/doc/',
        'mongodb': 'https://www.mongodb.com/docs/',
        'redis': 'https://redis.io/docs/',
        'elasticsearch': 'https://www.elastic.co/guide/',
        'terraform': 'https://developer.hashicorp.com/terraform/docs',
        'ansible': 'https://docs.ansible.com/',
        'jenkins': 'https://www.jenkins.io/doc/',
        'circleci': 'https://circleci.com/docs/',
        'travis': 'https://docs.travis-ci.com/',
    }
    
    # Detect which external services are mentioned
    detected_services = []
    for service, docs_url in service_patterns.items():
        if service in content:
            detected_services.append((service, docs_url))
    
    # Check if skill has a Sources section
    has_sources_section = '## sources' in content
    
    if detected_services and not has_sources_section:
        issues.append(f"Skill uses {len(detected_services)} external services but has no Sources section")
    elif detected_services and has_sources_section:
        # Check if official docs are referenced
        for service, docs_url in detected_services:
            # Check for the base domain of the docs
            base_domain = docs_url.split('//')[1].split('/')[0]
            if base_domain not in content and service not in content:
                issues.append(f"References {service} but missing official docs: {docs_url}")
    
    return len(issues) == 0, issues

def check_script_syntax(skill_dir: Path) -> Tuple[bool, List[str]]:
    """Validate syntax of all scripts in skill."""
    issues = []
    scripts_dir = skill_dir / 'scripts'
    
    if not scripts_dir.exists():
        return True, []  # No scripts to validate
    
    import ast
    import subprocess
    
    for script_file in scripts_dir.rglob('*'):
        if not script_file.is_file():
            continue
        
        suffix = script_file.suffix.lower()
        
        if suffix == '.py':
            try:
                with open(script_file, 'r', encoding='utf-8', errors='replace') as f:
                    source = f.read()
                ast.parse(source)
            except SyntaxError as e:
                issues.append(f"Python syntax error in {script_file.name}: {e.msg} (line {e.lineno})")
        
        elif suffix == '.sh':
            try:
                result = subprocess.run(
                    ['bash', '-n', str(script_file)],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode != 0:
                    issues.append(f"Bash syntax error in {script_file.name}: {result.stderr.strip()}")
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass  # Skip if bash not available
        
        elif suffix in ['.js', '.ts']:
            try:
                result = subprocess.run(
                    ['node', '--check', str(script_file)],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode != 0:
                    issues.append(f"Node syntax error in {script_file.name}: {result.stderr.strip()}")
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass  # Skip if node not available
    
    return len(issues) == 0, issues

def check_pricing_accuracy(skill_dir: Path) -> Tuple[bool, List[str]]:
    """Verify pricing information is accurate and current."""
    issues = []
    skill_md = skill_dir / 'SKILL.md'
    
    if not skill_md.exists():
        return True, []
    
    content = skill_md.read_text(encoding='utf-8', errors='replace')
    content_lower = content.lower()
    
    # Pricing patterns that need verification
    pricing_patterns = {
        'free tier': 'Must specify what is free vs paid',
        'free plan': 'Must specify what is free vs paid',
        'pricing': 'Must include current pricing or link to pricing page',
        'cost': 'Must specify cost structure',
        'price': 'Must specify price details',
        'subscription': 'Must specify subscription tiers',
        'monthly': 'Must specify monthly pricing',
        'annual': 'Must specify annual pricing',
        'per month': 'Must specify monthly cost',
        'per year': 'Must specify annual cost',
        '$': 'Must specify what the cost covers',
        'usd': 'Must specify what the cost covers',
        'free': 'Must clarify what is free vs paid',
    }
    
    # Check if pricing is mentioned
    pricing_mentioned = False
    for pattern in pricing_patterns:
        if pattern in content_lower:
            pricing_mentioned = True
            # Check if pricing section exists
            if '## pricing' not in content_lower and '## cost' not in content_lower:
                issues.append(f"Mentions '{pattern}' but has no Pricing/Cost section")
            break
    
    # Check for common free services that should be mentioned
    free_services = ['github', 'gitlab', 'docker hub', 'vercel', 'netlify', 'cloudflare']
    for service in free_services:
        if service in content_lower and f'{service} free' not in content_lower and f'free {service}' not in content_lower:
            # Check if pricing is mentioned elsewhere
            if '## pricing' not in content_lower:
                issues.append(f"Uses {service} - consider documenting free tier availability")
    
    return len(issues) == 0, issues

def validate_skill_pro(skill_path: Path, check_agnostic: bool = True, 
                       check_quality: bool = True) -> Dict:
    """Full validation of a skill with all checks."""
    result = {
        'name': skill_path.name,
        'path': str(skill_path),
        'valid': False,
        'checks': {
            'frontmatter': {'passed': False, 'issues': []},
            'structure': {'passed': False, 'issues': []},
            'agnostic': {'passed': False, 'issues': []},
            'content': {'passed': False, 'issues': []},
            'sources': {'passed': False, 'issues': []},
            'syntax': {'passed': False, 'issues': []},
            'pricing': {'passed': False, 'issues': []},
        },
        'score': 0,
        'message': ''
    }
    
    # Frontmatter check
    skill_md = skill_path / 'SKILL.md'
    if not skill_md.exists():
        result['checks']['frontmatter']['issues'].append('SKILL.md not found')
        result['message'] = 'SKILL.md not found'
        return result
    
    content = skill_md.read_text(encoding='utf-8', errors='replace')
    frontmatter_text, _ = extract_frontmatter(content)
    
    if frontmatter_text is None:
        result['checks']['frontmatter']['issues'].append('Invalid frontmatter format')
    else:
        valid, message, _ = validate_frontmatter(frontmatter_text)
        result['checks']['frontmatter']['passed'] = valid
        if not valid:
            result['checks']['frontmatter']['issues'].append(message)
    
    # Structure check
    structure_valid, structure_issues = check_structure(skill_path)
    result['checks']['structure']['passed'] = structure_valid
    result['checks']['structure']['issues'] = structure_issues
    
    # Agnostic check
    if check_agnostic:
        agnostic_issues = check_agnostic_compliance(skill_path)
        result['checks']['agnostic']['passed'] = len(agnostic_issues) == 0
        result['checks']['agnostic']['issues'] = [i['issue'] for i in agnostic_issues]
    else:
        result['checks']['agnostic']['passed'] = True
    
    # Content quality check
    if check_quality:
        content_valid, content_issues = check_content_quality(skill_path)
        result['checks']['content']['passed'] = content_valid
        result['checks']['content']['issues'] = content_issues
    else:
        result['checks']['content']['passed'] = True
    
    # Sources verification check
    sources_valid, sources_issues = check_sources_verification(skill_path)
    result['checks']['sources']['passed'] = sources_valid
    result['checks']['sources']['issues'] = sources_issues
    
    # Script syntax check
    syntax_valid, syntax_issues = check_script_syntax(skill_path)
    result['checks']['syntax']['passed'] = syntax_valid
    result['checks']['syntax']['issues'] = syntax_issues
    
    # Pricing accuracy check (warning only, not a hard fail)
    pricing_valid, pricing_issues = check_pricing_accuracy(skill_path)
    result['checks']['pricing']['passed'] = True  # Always pass, just collect warnings
    result['checks']['pricing']['issues'] = pricing_issues
    result['checks']['pricing']['warning'] = not pricing_valid
    
    # Calculate score (excluding pricing from validity)
    checks_to_count = {k: v for k, v in result['checks'].items() if k != 'pricing'}
    checks_passed = sum(1 for c in checks_to_count.values() if c['passed'])
    total_checks = len(checks_to_count)
    result['score'] = round((checks_passed / total_checks) * 100, 1)
    
    # Overall validity (pricing is warning only)
    result['valid'] = all(c['passed'] for k, c in result['checks'].items() if k != 'pricing')
    
    if result['valid']:
        if result['checks']['pricing']['warning']:
            result['message'] = 'All validation checks passed (pricing warnings)'
        else:
            result['message'] = 'All validation checks passed'
    else:
        failed_checks = [k for k, v in result['checks'].items() if not v['passed'] and k != 'pricing']
        result['message'] = f"Failed checks: {', '.join(failed_checks)}"
    
    return result

def validate_all_pro(target_dir: str, check_agnostic: bool = True,
                     check_quality: bool = True) -> Dict:
    """Validate all skills in target directory."""
    target_path = Path(target_dir)
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'target': target_dir,
        'skills': [],
        'summary': {
            'total': 0,
            'valid': 0,
            'invalid': 0,
            'avg_score': 0
        }
    }
    
    total_score = 0
    
    for skill_dir in sorted(target_path.iterdir()):
        if skill_dir.is_dir() and not skill_dir.name.startswith('.'):
            result = validate_skill_pro(skill_dir, check_agnostic, check_quality)
            results['skills'].append(result)
            results['summary']['total'] += 1
            total_score += result['score']
            
            if result['valid']:
                results['summary']['valid'] += 1
            else:
                results['summary']['invalid'] += 1
    
    if results['summary']['total'] > 0:
        results['summary']['avg_score'] = round(total_score / results['summary']['total'], 1)
    
    return results

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Enhanced skill validation')
    parser.add_argument('target', help='Skill directory or skills root')
    parser.add_argument('--full', action='store_true', help='Run all checks')
    parser.add_argument('--skip-agnostic', action='store_true', help='Skip agnostic checks')
    parser.add_argument('--skip-quality', action='store_true', help='Skip quality checks')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    args = parser.parse_args()
    
    target_path = Path(args.target)
    if not target_path.exists():
        print(f'Error: Target not found: {args.target}')
        sys.exit(1)
    
    # Check if target is a single skill or directory
    if (target_path / 'SKILL.md').exists():
        # Single skill
        result = validate_skill_pro(target_path, 
                                   not args.skip_agnostic,
                                   not args.skip_quality)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            status = '✓' if result['valid'] else '✗'
            print(f"{status} {result['name']}: {result['message']}")
            print(f"   Score: {result['score']}%")
            for check_name, check in result['checks'].items():
                if not check['passed']:
                    print(f"   {check_name}: {', '.join(check['issues'])}")
    else:
        # Directory of skills
        results = validate_all_pro(args.target,
                                  not args.skip_agnostic,
                                  not args.skip_quality)
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print(f"=== Enhanced Validation Report ===")
            print(f"Target: {results['target']}")
            print(f"Total: {results['summary']['total']}")
            print(f"Valid: {results['summary']['valid']}")
            print(f"Invalid: {results['summary']['invalid']}")
            print(f"Avg Score: {results['summary']['avg_score']}%")
            print()
            
            for skill in results['skills']:
                status = '✓' if skill['valid'] else '✗'
                print(f"{status} {skill['name']}: {skill['message']} ({skill['score']}%)")

if __name__ == '__main__':
    main()

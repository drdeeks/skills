#!/usr/bin/env python3
"""
Enterprise skill validator — combines frontmatter, structure, agnostic, content, sources, syntax, pricing, and enterprise pillar checks.
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
MIN_DESCRIPTION_LENGTH = 100
ALLOWED_PROPERTIES = {'name', 'description', 'license', 'metadata', 'allowed-tools', 'version'}

HARDCODED_PATTERNS = [
    (r'/home/\w+/', 'Hardcoded home directory'),
    (r'/root/', 'Hardcoded root directory'),
    (r'/opt/\w+/', 'Hardcoded /opt path'),
    (r'~/.openclaw/', 'Hardcoded OpenClaw path'),
    (r'~/.hermes/', 'Hardcoded Hermes path'),
    (r'~/.config/opencode/', 'Hardcoded OpenCode path'),
    (r'/tmp/\w+/', 'Hardcoded temp path'),
]

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

HARDCODED_SECRETS_PATTERN = re.compile(
    r'(api_key|apikey|secret|password|token)\s*=\s*["\'][a-zA-Z0-9]{10,}',
    re.IGNORECASE
)

STALE_TEMPLATE_NAMES = {"example.py", "api_reference.md", "example_asset.txt"}


def extract_frontmatter(content: str) -> Tuple[Optional[str], str]:
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

    unexpected = set(frontmatter.keys()) - ALLOWED_PROPERTIES
    if unexpected:
        return False, f"Unexpected keys: {', '.join(sorted(unexpected))}", frontmatter

    if 'name' not in frontmatter:
        return False, "Missing 'name'", frontmatter
    if 'description' not in frontmatter:
        return False, "Missing 'description'", frontmatter

    name = frontmatter.get('name', '')
    if not isinstance(name, str):
        return False, "Name must be a string", frontmatter
    name = name.strip()
    if name:
        if not re.match(r'^[a-z0-9-]+$', name):
            return False, f"Name '{name}' should be hyphen-case", frontmatter
        if name.startswith('-') or name.endswith('-') or '--' in name:
            return False, f"Name '{name}' invalid format", frontmatter
        if len(name) > MAX_SKILL_NAME_LENGTH:
            return False, f"Name too long ({len(name)} chars)", frontmatter

    desc = frontmatter.get('description', '')
    if not isinstance(desc, str):
        return False, "Description must be a string", frontmatter
    desc = desc.strip()
    if desc:
        if '<' in desc or '>' in desc:
            return False, "Description cannot contain angle brackets", frontmatter
        if len(desc) > MAX_DESCRIPTION_LENGTH:
            return False, f"Description too long ({len(desc)} chars)", frontmatter
        if len(desc) < MIN_DESCRIPTION_LENGTH:
            return False, f"Description too short ({len(desc)} chars, minimum {MIN_DESCRIPTION_LENGTH})", frontmatter

    return True, "Valid", frontmatter


def check_agnostic_compliance(skill_dir: Path) -> List[Dict]:
    issues = []
    detection_skills = {'skill-scan-validate-resolver', 'fix-hardcoded', 'skill-creator-pro', 'skill-creator'}
    skill_name = skill_dir.name

    for file_path in skill_dir.rglob('*'):
        if file_path.is_file() and file_path.suffix in ['.md', '.py', '.sh', '.yaml', '.yml', '.json']:
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
    issues = []

    if not (skill_dir / 'SKILL.md').exists():
        issues.append("Missing SKILL.md")

    scripts_dir = skill_dir / 'scripts'
    if not scripts_dir.exists():
        issues.append("Missing scripts/ directory")
    else:
        script_files = [f for f in scripts_dir.rglob('*') if f.is_file() and f.suffix in ['.py', '.sh', '.js', '.ts']]
        if len(script_files) < 2:
            issues.append(f"scripts/ requires at least 2 script files (found {len(script_files)})")

    refs_dir = skill_dir / 'references'
    if not refs_dir.exists():
        issues.append("Missing references/ directory")
    else:
        ref_files = [f for f in refs_dir.rglob('*') if f.is_file() and f.suffix in ['.md', '.txt', '.json', '.yaml', '.yml', '.csv']]
        if len(ref_files) < 3:
            issues.append(f"references/ requires at least 3 reference files (found {len(ref_files)})")

    file_count = sum(1 for _ in skill_dir.rglob('*') if _.is_file())
    if file_count > 50:
        issues.append(f"Excessive files ({file_count}). Consider cleanup.")

    return len(issues) == 0, issues


def check_enterprise_structure(skill_dir: Path) -> Tuple[bool, List[str]]:
    """Check enterprise-grade skill directory structure (3+ scripts, 5+ refs)."""
    issues = []

    if not (skill_dir / 'SKILL.md').exists():
        issues.append("Missing SKILL.md")

    scripts_dir = skill_dir / 'scripts'
    if not scripts_dir.exists():
        issues.append("Missing scripts/ directory (enterprise requires 3+)")
    else:
        script_files = [f for f in scripts_dir.rglob('*') if f.is_file() and f.suffix in ['.py', '.sh', '.js', '.ts']]
        if len(script_files) < 3:
            issues.append(f"scripts/ requires at least 3 script files for enterprise (found {len(script_files)})")

    refs_dir = skill_dir / 'references'
    if not refs_dir.exists():
        issues.append("Missing references/ directory (enterprise requires 5+)")
    else:
        ref_files = [f for f in refs_dir.rglob('*') if f.is_file() and f.suffix in ['.md', '.txt', '.json', '.yaml', '.yml', '.csv']]
        if len(ref_files) < 5:
            issues.append(f"references/ requires at least 5 reference files for enterprise (found {len(ref_files)})")

    file_count = sum(1 for _ in skill_dir.rglob('*') if _.is_file())
    if file_count > 50:
        issues.append(f"Excessive files ({file_count}). Consider cleanup.")

    return len(issues) == 0, issues


def check_content_quality(skill_dir: Path) -> Tuple[bool, List[str]]:
    issues = []
    skill_md = skill_dir / 'SKILL.md'

    if not skill_md.exists():
        return False, ["No SKILL.md to analyze"]

    content = skill_md.read_text(encoding='utf-8', errors='replace')

    if len(content) < 100:
        issues.append("SKILL.md too short (< 100 chars)")

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
                break

    sections = re.findall(r'^##\s+(.+)$', content, re.MULTILINE)
    for section in sections:
        section_pattern = f'^## {re.escape(section)}$'
        section_match = re.search(section_pattern, content, re.MULTILINE)
        if section_match:
            start = section_match.end()
            next_section = re.search(r'^##\s+', content[start:], re.MULTILINE)
            if next_section:
                section_content = content[start:start + next_section.start()].strip()
            else:
                section_content = content[start:].strip()

            if '```' in section_content:
                continue
            text_only = re.sub(r'`[^`]+`', '', section_content).strip()
            if len(text_only) < 20:
                issues.append(f"Section '{section}' is sparse (< 20 chars)")

    links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
    for link_text, link_url in links:
        if link_url.startswith('http'):
            continue
        if link_url.startswith('#'):
            continue
        if len(link_url) > 200 or not link_url.isprintable():
            continue
        try:
            target_path = skill_dir / link_url
            if not target_path.exists():
                issues.append(f"Broken link: [{link_text}]({link_url})")
        except (OSError, ValueError):
            pass

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

    section_names = [s.strip().lower() for s in sections]
    seen = set()
    for s in section_names:
        if s in seen:
            issues.append(f"Duplicate section: '{s}'")
        seen.add(s)

    # Check scripts for hardcoded secrets
    scripts_dir = skill_dir / 'scripts'
    if scripts_dir.exists():
        for sf in scripts_dir.rglob('*'):
            if sf.is_file() and sf.suffix in ['.py', '.sh', '.js', '.ts']:
                try:
                    sc = sf.read_text(encoding='utf-8', errors='replace')
                    if HARDCODED_SECRETS_PATTERN.search(sc):
                        issues.append(f"Script '{sf.name}' contains hardcoded secrets")
                except:
                    pass

    # Check for stale template files
    for f in skill_dir.rglob('*'):
        if f.is_file() and f.name in STALE_TEMPLATE_NAMES:
            issues.append(f"Stale template file: '{f.name}'")

    return len(issues) == 0, issues


def check_sources_verification(skill_dir: Path) -> Tuple[bool, List[str]]:
    issues = []
    skill_md = skill_dir / 'SKILL.md'

    if not skill_md.exists():
        return False, ["No SKILL.md to analyze"]

    content = skill_md.read_text(encoding='utf-8', errors='replace').lower()

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

    detected_services = []
    for service, docs_url in service_patterns.items():
        if service in content:
            detected_services.append((service, docs_url))

    has_sources_section = '## sources' in content

    if detected_services and not has_sources_section:
        issues.append(f"Skill uses {len(detected_services)} external services but has no Sources section")
    elif detected_services and has_sources_section:
        for service, docs_url in detected_services:
            base_domain = docs_url.split('//')[1].split('/')[0]
            if base_domain not in content and service not in content:
                issues.append(f"References {service} but missing official docs: {docs_url}")

    return len(issues) == 0, issues


def check_script_syntax(skill_dir: Path) -> Tuple[bool, List[str]]:
    issues = []
    scripts_dir = skill_dir / 'scripts'

    if not scripts_dir.exists():
        return True, []

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
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode != 0:
                    issues.append(f"Bash syntax error in {script_file.name}: {result.stderr.strip()}")
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass

        elif suffix in ['.js', '.ts']:
            try:
                result = subprocess.run(
                    ['node', '--check', str(script_file)],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode != 0:
                    issues.append(f"Node syntax error in {script_file.name}: {result.stderr.strip()}")
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass

    return len(issues) == 0, issues


def check_pricing_accuracy(skill_dir: Path) -> Tuple[bool, List[str]]:
    issues = []
    skill_md = skill_dir / 'SKILL.md'

    if not skill_md.exists():
        return True, []

    content = skill_md.read_text(encoding='utf-8', errors='replace')
    content_lower = content.lower()

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

    pricing_mentioned = False
    for pattern in pricing_patterns:
        if pattern in content_lower:
            pricing_mentioned = True
            if '## pricing' not in content_lower and '## cost' not in content_lower:
                issues.append(f"Mentions '{pattern}' but has no Pricing/Cost section")
            break

    free_services = ['github', 'gitlab', 'docker hub', 'vercel', 'netlify', 'cloudflare']
    for service in free_services:
        if service in content_lower and f'{service} free' not in content_lower and f'free {service}' not in content_lower:
            if '## pricing' not in content_lower:
                issues.append(f"Uses {service} - consider documenting free tier availability")

    return len(issues) == 0, issues


def check_enterprise_pillars(skill_dir: Path) -> Tuple[bool, List[str]]:
    """Check all 8 enterprise pillar requirements."""
    issues = []
    skill_md = skill_dir / 'SKILL.md'

    if not skill_md.exists():
        return False, ["No SKILL.md to analyze"]

    content = skill_md.read_text(encoding='utf-8', errors='replace')
    frontmatter_text, body = extract_frontmatter(content)

    if frontmatter_text is None:
        return False, ["No frontmatter found"]

    if yaml is not None:
        try:
            frontmatter = yaml.safe_load(frontmatter_text)
        except:
            frontmatter = {}
    else:
        frontmatter = {}
        for line in frontmatter_text.splitlines():
            if ':' in line:
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip()

    fm_name = frontmatter.get('name', '')
    dir_name = skill_dir.resolve().name
    if dir_name != fm_name:
        issues.append(f"Directory name '{dir_name}' does not match frontmatter name '{fm_name}'")

    body_lines = len(body.strip().split("\n")) if body.strip() else 0
    if body_lines >= 500:
        issues.append(f"Body too long ({body_lines} lines, max 499 for progressive disclosure)")

    h2_sections = re.findall(r'^## ', body, re.MULTILINE)
    if len(h2_sections) < 6:
        issues.append(f"Only {len(h2_sections)} top-level sections (need 6+)")

    has_provider = bool(re.search(r'(?i)provider.{0,20}compatib', body))
    if not has_provider:
        issues.append("Missing Provider Compatibility section")

    provider_names = ["openai", "claude", "mistral", "gemini", "hermes"]
    provider_count = sum(1 for p in provider_names if p.lower() in body.lower())
    if provider_count < 5:
        issues.append(f"Only {provider_count}/5 providers listed (need openai, claude, mistral, gemini, hermes)")

    has_free = bool(re.search(r'(?i)free.{0,10}first|cost.{0,10}tier|tier\s*0', body))
    if not has_free:
        issues.append("Missing Free-First Strategy section")

    has_free_alt = bool(re.search(r'(?i)free.{0,20}alternative|\$0', body))
    if not has_free_alt:
        issues.append("No free alternatives documented")

    has_output = bool(re.search(r'(?i)output.{0,20}statistic|enforced.{0,20}output|mandatory.{0,20}output', body))
    if not has_output:
        issues.append("Missing Enforced Output Statistics section")

    has_error = bool(re.search(r'(?i)error.{0,20}handl|recovery|retry|fallback', body))
    refs_dir = skill_dir / 'references'
    ref_files = list(refs_dir.glob("*.md")) if refs_dir.exists() else []
    for rf in ref_files:
        try:
            rf_content = rf.read_text(encoding='utf-8', errors='replace')
            if re.search(r'(?i)error.{0,20}handl|recovery|retry', rf_content):
                has_error = True
                break
        except:
            pass
    if not has_error:
        issues.append("No error handling documented (in SKILL.md or references)")

    has_scripts_table = bool(re.search(r'(?i)\|\s*`?scripts/', body))
    if not has_scripts_table:
        issues.append("Missing Scripts table in SKILL.md")

    has_refs = bool(re.search(r'(?i)##.*key\s*reference|##.*reference', body))
    if not has_refs:
        issues.append("Missing Key References section")

    has_enhance = bool(re.search(r'(?i)enhance|complement|expansion|plugin|hook', body))
    if not has_enhance:
        issues.append("No enhancement hooks documented")

    workflows = re.findall(r'(?i)##.*workflow', body)
    if len(workflows) < 1:
        issues.append(f"Found {len(workflows)} Workflow sections (need at least 1)")

    scripts_dir = skill_dir / 'scripts'
    script_files = list(scripts_dir.glob("*.py")) + list(scripts_dir.glob("*.sh")) if scripts_dir.exists() else []
    for sf in script_files:
        try:
            sc = sf.read_text(encoding='utf-8', errors='replace')
            if not sc.startswith("#!/"):
                issues.append(f"Script '{sf.name}' missing shebang line")
            has_python_docstring = '"""' in sc[:500] or "'''" in sc[:500]
            has_bash_docstring = bool(re.search(r'^#[^!].*\n#[^!]', sc[:500], re.MULTILINE))
            if not has_python_docstring and not has_bash_docstring:
                issues.append(f"Script '{sf.name}' missing docstring")
            if HARDCODED_SECRETS_PATTERN.search(sc):
                issues.append(f"Script '{sf.name}' contains hardcoded secrets")
        except:
            pass

    for rf in ref_files:
        try:
            rc = rf.read_text(encoding='utf-8', errors='replace')
            rf_lines = len(rc.strip().split("\n")) if rc.strip() else 0
            if rf_lines > 100:
                has_toc = bool(re.search(r'(?i)table of contents|## contents', rc[:500]))
                if not has_toc:
                    issues.append(f"Reference '{rf.name}' over 100 lines but has no TOC")
        except:
            pass

    found_stale = []
    for p in skill_dir.rglob("*"):
        if p.name in STALE_TEMPLATE_NAMES:
            found_stale.append(p.name)
    if found_stale:
        issues.append(f"Stale template files found: {', '.join(found_stale)}")

    for sf in script_files:
        if sf.name == '__init__.py':
            continue
        try:
            if sf.name in content or sf.stem in content:
                pass
            else:
                issues.append(f"Script '{sf.name}' not referenced in SKILL.md")
        except:
            pass

    for rf in ref_files:
        try:
            if rf.name not in content:
                issues.append(f"Reference '{rf.name}' not referenced in SKILL.md")
        except:
            pass

    lessons_dir = refs_dir / 'lessons'
    if lessons_dir.exists():
        lesson_files = [f for f in lessons_dir.iterdir() if f.is_file()]
        if len(lesson_files) == 0:
            issues.append("references/lessons/ exists but is empty")

    return len(issues) == 0, issues


def check_metadata_openclaw(skill_dir: Path) -> Tuple[bool, List[str]]:
    """Check that metadata has a valid harness section (openclaw, openai, or generic)."""
    issues = []
    skill_md = skill_dir / 'SKILL.md'

    if not skill_md.exists():
        return False, ["No SKILL.md to analyze"]

    content = skill_md.read_text(encoding='utf-8', errors='replace')
    frontmatter_text, _ = extract_frontmatter(content)

    if frontmatter_text is None:
        return False, ["No frontmatter found"]

    if yaml is not None:
        try:
            frontmatter = yaml.safe_load(frontmatter_text)
            if not isinstance(frontmatter, dict):
                return False, ["Frontmatter is not a dictionary"]
        except:
            return False, ["Invalid YAML in frontmatter"]
    else:
        frontmatter = {}
        for line in frontmatter_text.splitlines():
            if ':' in line:
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip()

    metadata = frontmatter.get('metadata', {})
    if not isinstance(metadata, dict):
        issues.append("Missing or invalid 'metadata' in frontmatter")
        return False, issues

    # Accept openclaw, openai, or any provider-specific section
    valid_harnesses = ['openclaw', 'openai', 'hermes', 'anthropic', 'google', 'mistral', 'harness']
    has_harness = any(h in metadata for h in valid_harnesses)
    if not has_harness:
        issues.append(f"Missing metadata harness section (need one of: {', '.join(valid_harnesses)})")

    return len(issues) == 0, issues


def check_placeholder_rejection(skill_dir: Path) -> Tuple[bool, List[str]]:
    """Reject skills with PLACEHOLDER status."""
    issues = []
    skill_md = skill_dir / 'SKILL.md'

    if not skill_md.exists():
        return False, ["No SKILL.md to analyze"]

    content = skill_md.read_text(encoding='utf-8', errors='replace')
    frontmatter_text, _ = extract_frontmatter(content)

    if frontmatter_text is None:
        return False, ["No frontmatter found"]

    if yaml is not None:
        try:
            frontmatter = yaml.safe_load(frontmatter_text)
            if not isinstance(frontmatter, dict):
                return False, ["Frontmatter is not a dictionary"]
        except:
            return False, ["Invalid YAML in frontmatter"]
    else:
        frontmatter = {}
        for line in frontmatter_text.splitlines():
            if ':' in line:
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip()

    status = frontmatter.get('status', '')
    if isinstance(status, str) and status.strip().upper() == 'PLACEHOLDER':
        issues.append("Skill has PLACEHOLDER status — cannot validate placeholder skills")

    return len(issues) == 0, issues


def validate_skill_pro(skill_path: Path, check_agnostic: bool = True,
                       check_quality: bool = True) -> Dict:
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
            'enterprise': {'passed': False, 'issues': []},
        },
        'score': 0,
        'message': ''
    }

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

    structure_valid, structure_issues = check_structure(skill_path)
    result['checks']['structure']['passed'] = structure_valid
    result['checks']['structure']['issues'] = structure_issues

    if check_agnostic:
        agnostic_issues = check_agnostic_compliance(skill_path)
        result['checks']['agnostic']['passed'] = len(agnostic_issues) == 0
        result['checks']['agnostic']['issues'] = [i['issue'] for i in agnostic_issues]
    else:
        result['checks']['agnostic']['passed'] = True

    if check_quality:
        content_valid, content_issues = check_content_quality(skill_path)
        result['checks']['content']['passed'] = content_valid
        result['checks']['content']['issues'] = content_issues
    else:
        result['checks']['content']['passed'] = True

    sources_valid, sources_issues = check_sources_verification(skill_path)
    result['checks']['sources']['passed'] = sources_valid
    result['checks']['sources']['issues'] = sources_issues

    syntax_valid, syntax_issues = check_script_syntax(skill_path)
    result['checks']['syntax']['passed'] = syntax_valid
    result['checks']['syntax']['issues'] = syntax_issues

    pricing_valid, pricing_issues = check_pricing_accuracy(skill_path)
    result['checks']['pricing']['passed'] = True
    result['checks']['pricing']['issues'] = pricing_issues
    result['checks']['pricing']['warning'] = not pricing_valid

    enterprise_valid, enterprise_issues = check_enterprise_pillars(skill_path)
    result['checks']['enterprise']['passed'] = enterprise_valid
    result['checks']['enterprise']['issues'] = enterprise_issues

    metadata_valid, metadata_issues = check_metadata_openclaw(skill_path)
    if not metadata_valid:
        result['checks']['enterprise']['passed'] = False
        result['checks']['enterprise']['issues'].extend(metadata_issues)

    placeholder_valid, placeholder_issues = check_placeholder_rejection(skill_path)
    if not placeholder_valid:
        result['checks']['enterprise']['passed'] = False
        result['checks']['enterprise']['issues'].extend(placeholder_issues)

    checks_to_count = {k: v for k, v in result['checks'].items() if k != 'pricing'}
    checks_passed = sum(1 for c in checks_to_count.values() if c['passed'])
    total_checks = len(checks_to_count)
    result['score'] = round((checks_passed / total_checks) * 100, 1)

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
    parser = argparse.ArgumentParser(description='Enterprise skill validation')
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

    if (target_path / 'SKILL.md').exists():
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
        results = validate_all_pro(args.target,
                                  not args.skip_agnostic,
                                  not args.skip_quality)
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print(f"=== Enterprise Validation Report ===")
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

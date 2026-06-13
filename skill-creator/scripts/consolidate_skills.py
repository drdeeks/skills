#!/usr/bin/env python3
"""
Consolidate redundant skills into a single robust skill.
Merges overlapping functionality while preserving unique features.
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from datetime import datetime

try:
    import yaml
except ModuleNotFoundError:
    yaml = None

def extract_frontmatter(content: str) -> Tuple[Dict, str]:
    """Extract frontmatter and body from SKILL.md."""
    lines = content.splitlines()
    if not lines or lines[0].strip() != '---':
        return {}, content
    
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            frontmatter_text = '\n'.join(lines[1:i])
            body = '\n'.join(lines[i+1:])
            
            if yaml is not None:
                try:
                    frontmatter = yaml.safe_load(frontmatter_text)
                    if not isinstance(frontmatter, dict):
                        frontmatter = {}
                except yaml.YAMLError:
                    frontmatter = {}
            else:
                frontmatter = {}
                for line in frontmatter_text.splitlines():
                    if ':' in line:
                        key, value = line.split(':', 1)
                        frontmatter[key.strip()] = value.strip()
            
            return frontmatter, body
    
    return {}, content

def extract_sections(content: str) -> Dict[str, str]:
    """Extract sections from markdown content."""
    sections = {}
    current_section = "preamble"
    current_content = []
    
    for line in content.splitlines():
        if line.startswith('## '):
            if current_content:
                sections[current_section] = '\n'.join(current_content)
            current_section = line[3:].strip()
            current_content = []
        else:
            current_content.append(line)
    
    if current_content:
        sections[current_section] = '\n'.join(current_content)
    
    return sections

def merge_frontmatters(frontmatters: List[Dict]) -> Dict:
    """Merge multiple frontmatters into one."""
    merged = {
        'name': '',
        'description': '',
        'license': 'MIT',
        'metadata': {}
    }
    
    for fm in frontmatters:
        if not merged['name'] and fm.get('name'):
            merged['name'] = fm['name']
        if not merged['description'] and fm.get('description'):
            merged['description'] = fm['description']
        if fm.get('license'):
            merged['license'] = fm['license']
        if fm.get('metadata'):
            merged['metadata'].update(fm['metadata'])
    
    return merged

def merge_bodies(bodies: List[str], source_skills: List[str]) -> str:
    """Merge multiple skill bodies into one."""
    merged_sections = {}
    all_section_contents = {}
    
    # Extract sections from each body
    for i, body in enumerate(bodies):
        sections = extract_sections(body)
        skill_name = source_skills[i]
        
        for section_name, content in sections.items():
            if section_name not in all_section_contents:
                all_section_contents[section_name] = []
            all_section_contents[section_name].append({
                'skill': skill_name,
                'content': content
            })
    
    # Merge sections
    for section_name, contents in all_section_contents.items():
        if len(contents) == 1:
            # Unique section, keep as-is
            merged_sections[section_name] = contents[0]['content']
        else:
            # Common section, merge and deduplicate
            merged_lines = []
            seen_lines = set()
            
            for content in contents:
                for line in content['content'].splitlines():
                    line_stripped = line.strip()
                    if line_stripped and line_stripped not in seen_lines:
                        merged_lines.append(line)
                        seen_lines.add(line_stripped)
                    elif not line_stripped:
                        merged_lines.append(line)
            
            merged_sections[section_name] = '\n'.join(merged_lines)
    
    # Reconstruct body
    body_parts = []
    for section_name, content in merged_sections.items():
        if section_name == "preamble":
            body_parts.append(content)
        else:
            body_parts.append(f"## {section_name}\n{content}")
    
    return '\n\n'.join(body_parts)

def collect_skill_files(skill_dir: Path) -> Dict[str, Path]:
    """Collect all files in a skill directory."""
    files = {}
    for file_path in skill_dir.rglob('*'):
        if file_path.is_file():
            relative = file_path.relative_to(skill_dir)
            files[str(relative)] = file_path
    return files

def consolidate_skills(skill_dirs: List[Path], output_dir: Path, 
                      primary_name: str = None) -> Dict:
    """Consolidate multiple skills into one."""
    result = {
        'timestamp': datetime.now().isoformat(),
        'source_skills': [d.name for d in skill_dirs],
        'output_skill': None,
        'files_merged': 0,
        'sections_merged': 0,
        'warnings': []
    }
    
    if not skill_dirs:
        result['warnings'].append('No skills to consolidate')
        return result
    
    # Use first skill as primary if not specified
    if not primary_name:
        primary_name = skill_dirs[0].name
    
    result['output_skill'] = primary_name
    
    # Collect all frontmatters and bodies
    frontmatters = []
    bodies = []
    
    for skill_dir in skill_dirs:
        skill_md = skill_dir / 'SKILL.md'
        if skill_md.exists():
            content = skill_md.read_text(encoding='utf-8')
            fm, body = extract_frontmatter(content)
            frontmatters.append(fm)
            bodies.append(body)
    
    # Merge frontmatters
    merged_frontmatter = merge_frontmatters(frontmatters)
    merged_frontmatter['name'] = primary_name
    
    # Merge bodies
    merged_body = merge_bodies(bodies, [d.name for d in skill_dirs])
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Write merged SKILL.md
    if yaml is not None:
        frontmatter_yaml = yaml.dump(merged_frontmatter, default_flow_style=False, allow_unicode=True)
    else:
        frontmatter_yaml = ''
        for key, value in merged_frontmatter.items():
            if isinstance(value, dict):
                frontmatter_yaml += f"{key}:\n"
                for k, v in value.items():
                    frontmatter_yaml += f"  {k}: {v}\n"
            else:
                frontmatter_yaml += f"{key}: {value}\n"
    
    merged_content = f"---\n{frontmatter_yaml}---\n\n{merged_body}"
    (output_dir / 'SKILL.md').write_text(merged_content, encoding='utf-8')
    result['files_merged'] += 1
    
    # Merge scripts directories
    all_scripts = {}
    for skill_dir in skill_dirs:
        scripts_dir = skill_dir / 'scripts'
        if scripts_dir.exists():
            for script in scripts_dir.iterdir():
                if script.is_file():
                    if script.name not in all_scripts:
                        all_scripts[script.name] = script
                    else:
                        result['warnings'].append(f"Script conflict: {script.name} from {skill_dir.name}")
    
    if all_scripts:
        output_scripts = output_dir / 'scripts'
        output_scripts.mkdir(exist_ok=True)
        for script_name, script_path in all_scripts.items():
            (output_scripts / script_name).write_bytes(script_path.read_bytes())
            result['files_merged'] += 1
    
    # Merge references directories
    all_references = {}
    for skill_dir in skill_dirs:
        references_dir = skill_dir / 'references'
        if references_dir.exists():
            for ref in references_dir.rglob('*'):
                if ref.is_file():
                    relative = ref.relative_to(references_dir)
                    if str(relative) not in all_references:
                        all_references[str(relative)] = ref
                    else:
                        result['warnings'].append(f"Reference conflict: {relative} from {skill_dir.name}")
    
    if all_references:
        output_references = output_dir / 'references'
        output_references.mkdir(exist_ok=True)
        for ref_name, ref_path in all_references.items():
            (output_references / ref_name).write_bytes(ref_path.read_bytes())
            result['files_merged'] += 1
    
    return result

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Consolidate skills')
    parser.add_argument('--skills', nargs='+', required=True, help='Skill directories to consolidate')
    parser.add_argument('--output', required=True, help='Output directory')
    parser.add_argument('--primary', help='Primary skill name')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    args = parser.parse_args()
    
    skill_dirs = [Path(s) for s in args.skills]
    output_dir = Path(args.output)
    
    # Validate input
    for skill_dir in skill_dirs:
        if not skill_dir.exists():
            print(f'Error: Skill not found: {skill_dir}')
            sys.exit(1)
    
    result = consolidate_skills(skill_dirs, output_dir, args.primary)
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"=== Consolidation Report ===")
        print(f"Source skills: {', '.join(result['source_skills'])}")
        print(f"Output skill: {result['output_skill']}")
        print(f"Files merged: {result['files_merged']}")
        
        if result['warnings']:
            print("\nWarnings:")
            for warning in result['warnings']:
                print(f"  - {warning}")

if __name__ == '__main__':
    main()

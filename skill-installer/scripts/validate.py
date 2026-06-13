#!/usr/bin/env python3
"""
Basic validation script for skill-installer.
Validates the skill itself against skill-creator-pro standards.
"""

import os
import sys
import json
from pathlib import Path

def validate_skill_installer():
    """Validate the skill-installer skill."""
    skill_dir = Path(__file__).parent.parent
    
    # Check SKILL.md exists
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return {"valid": False, "error": "SKILL.md not found"}
    
    # Check frontmatter
    content = skill_md.read_text(encoding='utf-8')
    lines = content.splitlines()
    
    if not lines or lines[0].strip() != '---':
        return {"valid": False, "error": "Missing frontmatter"}
    
    # Find closing ---
    frontmatter_end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            frontmatter_end = i
            break
    
    if frontmatter_end is None:
        return {"valid": False, "error": "Missing closing ---"}
    
    # Parse frontmatter
    frontmatter_text = '\n'.join(lines[1:frontmatter_end])
    frontmatter = {}
    for line in frontmatter_text.splitlines():
        if ':' in line:
            key, value = line.split(':', 1)
            frontmatter[key.strip()] = value.strip()
    
    # Check required keys
    if 'name' not in frontmatter:
        return {"valid": False, "error": "Missing 'name' in frontmatter"}
    if 'description' not in frontmatter:
        return {"valid": False, "error": "Missing 'description' in frontmatter"}
    
    # Check name format
    name = frontmatter.get('name', '')
    if not name.islower() or not all(c.isalnum() or c == '-' for c in name):
        return {"valid": False, "error": f"Invalid name format: {name}"}
    
    # Check scripts directory
    scripts_dir = skill_dir / "scripts"
    if not scripts_dir.exists():
        return {"valid": False, "error": "Scripts directory not found"}
    
    # Check for required scripts
    required_scripts = ["install_skill.py", "extract_skill.py", "validate_install.py"]
    for script in required_scripts:
        if not (scripts_dir / script).exists():
            return {"valid": False, "error": f"Missing script: {script}"}
    
    # Check references directory
    references_dir = skill_dir / "references"
    if not references_dir.exists():
        return {"valid": False, "error": "References directory not found"}
    
    return {
        "valid": True,
        "skill_name": frontmatter.get('name'),
        "description_length": len(frontmatter.get('description', '')),
        "scripts_count": len(list(scripts_dir.glob("*.py"))),
        "references_count": len(list(references_dir.glob("*.md")))
    }

def main():
    result = validate_skill_installer()
    
    if result["valid"]:
        print("✓ skill-installer is valid")
        print(f"  Name: {result['skill_name']}")
        print(f"  Description length: {result['description_length']} chars")
        print(f"  Scripts: {result['scripts_count']}")
        print(f"  References: {result['references_count']}")
        sys.exit(0)
    else:
        print(f"✗ skill-installer validation failed: {result['error']}")
        sys.exit(1)

if __name__ == "__main__":
    main()

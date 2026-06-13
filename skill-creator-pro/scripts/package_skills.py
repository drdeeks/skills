#!/usr/bin/env python3
"""
Skill Packager - Creates/updates .skill files (ZIP archives) from skill directories.
"""

import sys
import json
import argparse
import zipfile
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class SkillPackager:
    def __init__(self, skills_root: Path, output_dir: Optional[Path] = None):
        self.skills_root = skills_root.resolve()
        self.output_dir = (output_dir or skills_root).resolve()
        self.results = {
            "operation": "package_skills",
            "timestamp": datetime.now().isoformat(),
            "status": "success",
            "details": {}
        }

    def should_include(self, file_path: Path, skill_dir: Path) -> bool:
        """Determine if file should be included in package."""
        excluded_dirs = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".tox", "node_modules", ".venv", "venv", "dist", "build", "*.egg-info"}
        excluded_suffixes = {".pyc", ".pyo", ".pyd", ".so", ".dll", ".exe", ".class", ".log", ".cache", ".tmp", ".swp", ".swo", "~"}
        
        # Check excluded directories
        for part in file_path.relative_to(skill_dir).parts:
            if part in excluded_dirs:
                return False
        
        # Check excluded suffixes
        if file_path.suffix.lower() in excluded_suffixes:
            return False
        
        # Skip hidden files except .gitignore
        if file_path.name.startswith(".") and file_path.name != ".gitignore":
            return False
        
        return True

    def package_skill(self, skill_name: str, overwrite: bool = True) -> Dict:
        """Package a single skill into .skill file."""
        skill_dir = self.skills_root / skill_name
        
        if not skill_dir.exists():
            return {"skill": skill_name, "status": "failed", "error": "Skill directory not found"}
        
        if not (skill_dir / "SKILL.md").exists():
            return {"skill": skill_name, "status": "failed", "error": "No SKILL.md found"}
        
        # Output .skill file
        skill_file = self.output_dir / f"{skill_name}.skill"
        
        if skill_file.exists() and not overwrite:
            return {"skill": skill_name, "status": "skipped", "reason": "File exists, use --overwrite"}
        
        files_added = 0
        total_size = 0
        
        try:
            with zipfile.ZipFile(skill_file, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
                for file_path in skill_dir.rglob("*"):
                    if file_path.is_file() and self.should_include(file_path, skill_dir):
                        # Archive path: skill_name/relative_path
                        archive_path = f"{skill_name}/{file_path.relative_to(skill_dir)}"
                        zf.write(file_path, archive_path)
                        files_added += 1
                        total_size += file_path.stat().st_size
            
            return {
                "skill": skill_name,
                "status": "success",
                "output": str(skill_file),
                "files": files_added,
                "size_bytes": total_size,
                "size_kb": round(total_size / 1024, 1)
            }
            
        except Exception as e:
            if skill_file.exists():
                skill_file.unlink()
            return {"skill": skill_name, "status": "failed", "error": str(e)}

    def package_all(self, overwrite: bool = True, filter_names: Optional[List[str]] = None) -> Dict:
        """Package all skills in the skills root."""
        results = {
            "timestamp": datetime.now().isoformat(),
            "skills_root": str(self.skills_root),
            "output_dir": str(self.output_dir),
            "packaged": [],
            "skipped": [],
            "failed": [],
            "total_files": 0,
            "total_size_bytes": 0
        }
        
        # Get skill directories
        skill_dirs = []
        for item in self.skills_root.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                if (item / "SKILL.md").exists():
                    skill_dirs.append(item.name)
        
        if filter_names:
            skill_dirs = [s for s in skill_dirs if s in filter_names]
        
        for skill_name in sorted(skill_dirs):
            result = self.package_skill(skill_name, overwrite=overwrite)
            
            if result["status"] == "success":
                results["packaged"].append(result)
                results["total_files"] += result["files"]
                results["total_size_bytes"] += result["size_bytes"]
            elif result["status"] == "skipped":
                results["skipped"].append(result)
            else:
                results["failed"].append(result)
        
        self.results["details"] = results
        
        if results["failed"]:
            self.results["status"] = "partial"
        
        return self.results


def main():
    parser = argparse.ArgumentParser(description="Package skills into .skill files (ZIP archives)")
    parser.add_argument("--skills-root", required=True, help="Root directory containing skill directories")
    parser.add_argument("--output-dir", help="Output directory for .skill files (default: skills-root)")
    parser.add_argument("--skill", help="Package specific skill only")
    parser.add_argument("--skills", nargs="+", help="Package specific skills only")
    parser.add_argument("--overwrite", action="store_true", default=True, help="Overwrite existing .skill files")
    parser.add_argument("--no-overwrite", action="store_false", dest="overwrite", help="Don't overwrite existing")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    
    args = parser.parse_args()
    
    packager = SkillPackager(Path(args.skills_root), Path(args.output_dir) if args.output_dir else None)
    
    if args.skill:
        result = packager.package_skill(args.skill, overwrite=args.overwrite)
        results = {"skills": [result]}
    elif args.skills:
        result = packager.package_all(overwrite=args.overwrite, filter_names=args.skills)
        results = result
    else:
        result = packager.package_all(overwrite=args.overwrite)
        results = result
    
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(f"=== Skill Packaging Report ===")
        print(f"Skills root: {results.get('skills_root', args.skills_root)}")
        print(f"Output dir: {results.get('output_dir', args.skills_root)}")
        print(f"Packaged: {len(results.get('packaged', []))}")
        print(f"Skipped: {len(results.get('skipped', []))}")
        print(f"Failed: {len(results.get('failed', []))}")
        print(f"Total files: {results.get('total_files', 0)}")
        print(f"Total size: {results.get('total_size_bytes', 0) / 1024:.1f} KB")
        print()
        
        for r in results.get("packaged", []):
            print(f"  ✓ {r['skill']}: {r['files']} files, {r['size_kb']} KB -> {r['output']}")
        
        for r in results.get("skipped", []):
            print(f"  ⊘ {r['skill']}: {r.get('reason', 'skipped')}")
        
        for r in results.get("failed", []):
            print(f"  ✗ {r['skill']}: {r.get('error', 'failed')}")
    
    # Exit code
    has_failures = bool(results.get("failed", []))
    sys.exit(1 if has_failures else 0)


if __name__ == "__main__":
    main()
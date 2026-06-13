---
name: skill-installer
description: "Graceful skill installation and lifecycle manager. Handles .skill zip archives, directory-based skills, and remote packages with automatic validation against skill-creator. Use when: installing new skills, updating skills, extracting .skill files, importing skill packages, or validating skill integrity before deployment."
license: MIT
metadata:
  openclaw:
    version: "1.0"
    category: infrastructure
    complexity: enterprise
  openai:
    type: function
  version: "1.0.0"
  author: "skill-creator"
  category: "skill-management"
version: 0.0.7
---

# Skill Installer

Graceful skill installation and lifecycle manager that handles all skill formats with automatic validation.

## When to Use

- Installing new skills from .skill zip archives
- Importing skill packages from remote sources
- Updating existing skills with newer versions
- Extracting and integrating bundled skill packages
- Validating skill integrity before deployment
- Batch installing multiple skills from a directory

## Features

- **Multi-format support**: .skill zip archives, directory-based skills, remote packages
- **Automatic extraction**: Graceful handling of nested zip structures
- **Metadata validation**: Verifies `__skill_metadata.json` in .skill files with version tracking
- **Validation-first**: Every skill validated against skill-creator before installation
- **Rollback support**: Failed installations automatically reverted
- **Duplicate detection**: Prevents overwriting without explicit confirmation
- **Batch operations**: Install/update entire skill packages at once
- **Integrity checks**: Verify checksums and signatures when available

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENCODE_SKILLS_DIR` | `${SKILLS_DIR}` | Skills installation directory |
| `SKILL_TEMP_DIR` | System temp | Temporary extraction directory |

## Skill Format Handling

### .skill Zip Archives

.skill files are zip archives containing the full skill directory structure:

```bash
# Single skill installation
python3 scripts/install_skill.py /path/to/skill.skill --target "${OPENCODE_SKILLS_DIR}"

# With validation
python3 scripts/install_skill.py /path/to/skill.skill --target "${OPENCODE_SKILLS_DIR}" --validate
```

### Directory-Based Skills

Skills structured as directories with SKILL.md:

```bash
# Install from directory
python3 scripts/install_skill.py /path/to/skill-directory/ --target "${OPENCODE_SKILLS_DIR}"

# Install with all subdirectories
python3 scripts/install_skill.py /path/to/skills/ --target "${OPENCODE_SKILLS_DIR}" --recursive
```

### Remote Packages

```bash
# Install from URL
python3 scripts/install_skill.py https://example.com/skill.skill --target "${OPENCODE_SKILLS_DIR}"

# Install from git repository
python3 scripts/install_skill.py git@github.com:user/repo.git --target "${OPENCODE_SKILLS_DIR}"
```

## Installation Workflow

### Step 1: Detect Format

```bash
python3 scripts/detect_format.py /path/to/skill-or-package
```

Output:
```json
{
  "format": "skill-zip | directory | remote",
  "path": "/path/to/source",
  "skills_found": ["skill-name"],
  "size_bytes": 12345
}
```

### Step 2: Extract (if needed)

```bash
python3 scripts/extract_skill.py /path/to/skill.skill --output "${SKILL_TEMP_DIR}/skill-extract/"
```

Handles:
- Nested zip archives
- Multiple skills in single package
- Preserves directory structure
- Extracts SKILL.md, scripts/, references/, assets/

### Step 3: Validate

```bash
python3 scripts/validate_install.py /path/to/extracted-skill/ --source skill-creator
```

Validation checks:
- Frontmatter validity (YAML parsing, required keys)
- Structure compliance (SKILL.md, scripts/, references/, assets/)
- Content quality (no placeholders, no hardcoded paths)
- Platform agnosticism (cross-platform compatible)
- Redundancy check (overlap with existing skills)

### Step 4: Install

```bash
python3 scripts/install_validated.py /path/to/validated-skill/ --target "${OPENCODE_SKILLS_DIR}"
```

Actions:
- Creates skill directory
- Copies all files
- Preserves existing scripts/references
- Updates skill manifest
- Generates installation receipt

### Step 5: Post-Install Validation

```bash
python3 scripts/post_install_check.py "${OPENCODE_SKILLS_DIR}/skill-name/"
```

Verifies:
- All files copied correctly
- SKILL.md readable and valid
- Scripts executable (if present)
- No broken references

## Batch Installation

### From Package Directory

```bash
python3 scripts/batch_install.py /path/to/skill-package/ --target "${OPENCODE_SKILLS_DIR}" --validate-all
```

Process:
1. Scan package for all .skill files and directories
2. Detect format for each
3. Extract if needed
4. Validate each against skill-creator
5. Install validated skills
6. Report successes and failures

### From Zip Archive

```bash
python3 scripts/batch_install.py /path/to/all-skills.zip --target "${OPENCODE_SKILLS_DIR}"
```

Handles:
- Multiple .skill files in single archive
- Nested skill directories
- Mixed formats within archive

## Validation Integration

All installations automatically validate against skill-creator:

### Validation Pipeline

```
Input → Format Detection → Extraction → Validation → Installation → Post-Check
                              ↓              ↓
                         skill-creator  skill-creator
                         validate_pro.py   validate_pro.py
```

### Validation Rules

| Check | Rule | Action on Failure |
|-------|------|-------------------|
| Frontmatter | Valid YAML, required keys | Reject skill |
| Name | Lowercase hyphen-case, ≤64 chars | Auto-fix if possible |
| Description | 100-1024 chars, includes triggers | Flag for review |
| Structure | SKILL.md present, proper layout | Reject skill |
| Content | No placeholders, no TODOs | Flag for review |
| Agnostic | No hardcoded paths | Auto-fix paths |
| Scripts | Use stdlib only | Flag for review |
| Redundancy | No major overlap (<0.7) | Suggest consolidation |
| Metadata | `__skill_metadata.json` present in .skill files | Reject skill |
| Version | Semver format (X.Y.Z) | Reject skill |
| __init__.py | Must be present in skill root | Reject skill (production requirement) |

### Validation Output

```json
{
  "operation": "validate",
  "timestamp": "2026-06-12T19:00:00Z",
  "status": "success | failed | warning",
  "skill_name": "skill-name",
  "checks": {
    "frontmatter": {"status": "pass", "score": 1.0},
    "structure": {"status": "pass", "score": 1.0},
    "content": {"status": "warning", "score": 0.8, "issues": ["TODO marker found"]},
    "agnostic": {"status": "pass", "score": 1.0},
    "redundancy": {"status": "pass", "score": 0.2},
    "metadata": {"status": "pass", "score": 1.0, "version": "1.0.0"}
  },
  "overall_score": 0.92,
  "recommendation": "install | reject | review"
}
```

## Rollback Support

If installation fails validation:

```bash
# Automatic rollback
python3 scripts/install_skill.py /path/to/skill.skill --target "${OPENCODE_SKILLS_DIR}" --rollback-on-failure

# Manual rollback
python3 scripts/rollback_install.py "${OPENCODE_SKILLS_DIR}/skill-name/" --receipt /path/to/receipt.json
```

## Installation Receipts

Every installation generates a receipt:

```json
{
  "receipt_id": "uuid",
  "skill_name": "skill-name",
  "version": "1.0.0",
  "installed_at": "2026-06-12T19:00:00Z",
  "source": "/path/to/skill.skill",
  "format": "skill-zip",
  "validation_score": 0.95,
  "files_installed": [
    "SKILL.md",
    "scripts/main.py",
    "references/overview.md"
  ],
  "skill_metadata": {
    "skill_name": "skill-name",
    "version": "1.0.0",
    "previous_version": "0.9.0",
    "packaged_at": "2026-06-12T18:00:00Z",
    "files_count": 18,
    "size_bytes": 175041
  },
  "rollback_path": "/path/to/backup/"
}
```

## Scripts Reference

| Script | Purpose | Usage |
|--------|---------|-------|
| `scripts/install_skill.py` | Main installer | `source --target dir [--validate]` |
| `scripts/detect_format.py` | Detect skill format | `path` |
| `scripts/extract_skill.py` | Extract .skill archives | `archive --output dir` |
| `scripts/validate_install.py` | Validate before install | `skill-dir --source skill-creator` |
| `scripts/batch_install.py` | Batch installation | `package-dir --target dir` |
| `scripts/post_install_check.py` | Post-install verification | `installed-skill-dir` |
| `scripts/rollback_install.py` | Rollback failed install | `skill-dir --receipt file` |

## Provider Compatibility

| Provider | Compatibility | Notes |
|----------|---------------|-------|
| Claude (Anthropic) | Full | MCP servers, tool use |
| OpenAI / ChatGPT | Full | Function calling, Actions |
| Mistral / Le Chat | Full | Tool calling, script execution |
| Gemini (Google) | Full | Extensions, Vertex AI |
| Hermes (Nous) | Full | Tool-use fine-tuned |
| GitHub Copilot | Partial | Code generation; use external runner for scripts |
| Any LLM + tools | Full | Scripts are plain Python, provider-independent |

## Free-First Strategy

| Tier | Cost | Stack | Escalation Criteria |
|---|---|---|---|
| **Tier 0** | $0/mo | Python 3.8+ stdlib | Default — covers all individual use |
| **Tier 1** | $0-5/mo | + CI/CD automated validation | When installing 10+ skills automatically |
| **Tier 2** | $5-20/mo | + Hosted skill registry | When distributing across a team or org |

## Enforced Output Statistics

Every installation produces structured output:

```json
{
  "operation": "install",
  "timestamp": "ISO8601",
  "status": "success | failed",
  "skill_name": "the-skill-name",
  "version": "1.0.0",
  "validation_score": 0.95,
  "files_installed": 18,
  "cost": {"tier": 0, "amount_usd": 0.0, "service": "local"}
}
```

## Error Handling

| Error | Response |
|-------|----------|
| Invalid .skill archive | Report format error, skip |
| Missing SKILL.md | Reject skill, log error |
| Validation failed | Rollback, report issues |
| Already exists | Prompt for overwrite confirmation |
| Permission denied | Report, suggest sudo |
| Disk full | Clean temp files, retry |
| Network error (remote) | Retry with exponential backoff |

## Enterprise Validation Pillars

| Pillar | Weight | Description |
|--------|--------|-------------|
| Frontmatter | 20% | Valid YAML, required keys, naming |
| Structure | 15% | Directory layout, file organization |
| Content | 20% | Accuracy, completeness, no placeholders |
| Agnostic | 15% | No hardcoded paths, cross-platform |
| Redundancy | 10% | No overlap with existing skills |
| Sources | 10% | Documented, verified, current |
| Scripts | 5% | Working, tested, documented |
| Accessibility | 5% | Clear triggers, good descriptions |

## Enhancement Hooks

| Skill | Enhancement | When to Add |
|-------|-------------|-------------|
| `skill-creator` | Validation before install | When validating skill quality |
| `skill-scan-validate-resolver` | Batch scanning | When scanning multiple directories |
| `backup-protocol` | Backup before install | When installing production skills |

## Key References

- **Skill anatomy**: [references/skill-anatomy.md](references/skill-anatomy.md)
- **Format detection**: [references/format-detection.md](references/format-detection.md)
- **Validation rules**: [references/validation-rules.md](references/validation-rules.md)
- **Rollback procedures**: [references/rollback-procedures.md](references/rollback-procedures.md)

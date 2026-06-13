---
name: skill-scan-validate-resolver
description: "Scan, validate, and resolve skills across multiple directories. Ensures all skills are agnostic, complete, and compliant with skill-creator standards."
version: 0.0.5
metadata:
  openclaw:
    version: "1.0"
    category: infrastructure
    complexity: enterprise
  openai:
    type: function
---

# Skill Scan, Validate & Resolver

Comprehensive skill management system that scans multiple directories, validates against standards, and resolves issues including hardcoded paths, missing frontmatter, and structural problems.

## Features

- **Multi-source scanning**: Scan .openclaw, .hermes, and custom directories
- **Hardcoded path detection**: Find and fix hardcoded system paths
- **Frontmatter validation**: Ensure SKILL.md has valid YAML frontmatter
- **Agnostic enforcement**: Verify no platform-specific references
- **Metadata validation**: Verify .skill files contain proper `__skill_metadata.json` with version tracking
- **Auto-resolution**: Fix common issues automatically
- **Reporting**: Generate comprehensive audit reports with metadata status

## Usage

### Quick Scan
```bash
python3 scripts/scan_skills.py --sources ${OPENCLAW_DIR:-~/.openclaw}/agents/.skills/ ${HERMES_DIR:-~/.hermes}/skills/ --target ${OPENCODE_DIR:-~/.config/opencode}/skills/
```

### Full Validation
```bash
python3 scripts/validate_all.py --target ${OPENCODE_DIR:-~/.config/opencode}/skills/ --fix --report
```

### Fix Hardcoded Paths
```bash
python3 scripts/fix_hardcoded.py --target ${OPENCODE_DIR:-~/.config/opencode}/skills/ --dry-run
```

## Workflow

1. **Scan** - Identify skills across all source directories
2. **Diff** - Find skills not in target directory
3. **Copy** - Duplicate missing skills to target
4. **Validate** - Run skill-creator validation on all skills
5. **Fix** - Resolve hardcoded paths and frontmatter issues
6. **Report** - Generate comprehensive audit report

## Scripts

| Script | Purpose |
|--------|---------|
| `validate_pro.py` | Enterprise validation (copied from skill-creator) |
| `scan_skills.py` | Scan directories for skills |
| `validate_all.py` | Validate all skills using validate_pro.py |
| `fix_hardcoded.py` | Detect and fix hardcoded paths |
| `fix_frontmatter.py` | Fix SKILL.md frontmatter issues |
| `generate_report.py` | Generate audit reports |

### Validation Compatibility

This skill includes its own copy of `validate_pro.py` from skill-creator to ensure:
- **Compatibility**: Same validation logic across all skill management tools
- **Robustness**: Standalone operation without external dependencies
- **Consistency**: Unified scoring and reporting standards

When skill-creator updates its validation script, copy the new version here:
```bash
cp ${OPENCODE_DIR}skills/skill-creator/scripts/validate_pro.py \
   ${OPENCODE_DIR}skills/skill-scan-validate-resolver/scripts/validate_pro.py
```


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

| Tier | Cost | Stack |
|------|------|-------|
| **Tier 0** | $0/mo | Python 3.8+ (all scripts use stdlib only) |
| **Tier 1** | $0-5/mo | + CI/CD for automated validation |
| **Tier 2** | $5-20/mo | + Hosted skill registry for team distribution |

The entire core toolchain is permanently $0.


## Enforced Output Statistics

Every script produces structured output on completion:

```json
{
  "operation": "script_name",
  "timestamp": "ISO8601",
  "status": "success | failed",
  "skill_name": "the-skill-name",
  "details": {},
  "cost": {"tier": 0, "amount_usd": 0.0, "service": "local"}
}
```


## Error Handling

| Error | Response |
|-------|----------|
| Invalid input | Validate and report with guidance |
| Missing dependency | Auto-install or report requirement |
| Network failure | Retry with exponential backoff |
| Permission denied | Report and suggest alternatives |
| Resource not found | Report with available options |


## Enhancement Hooks

| Skill | Enhancement | When to Add |
|-------|-------------|-------------|
| `skill-creator` | Enterprise validation | When upgrading to enterprise |
| `html-report` | Visual validation dashboard | When auditing many skills |
| `xlsx` | Export validation results | When tracking skill quality metrics |


## Scripts Reference

| Script | Purpose | Usage |
|--------|---------|-------|
| `scripts/validate_pro.py` | Enterprise validation (from skill-creator) | Core validation engine |
| `scripts/validate_all.py` | Batch validation using validate_pro.py | `--target /path/to/skills/` |
| `scripts/scan_skills.py` | Scan directories for skills | `--sources dir1 dir2 --target dir` |
| `scripts/fix_frontmatter.py` | Fix SKILL.md frontmatter issues | `--target /path/to/skills/` |
| `scripts/fix_hardcoded.py` | Fix hardcoded paths | `--target /path/to/skills/ --dry-run` |
| `scripts/generate_report.py` | Generate audit reports | `--target /path/to/skills/ --output report.json` |

## Key References

- **Overview**: [references/overview.md](references/overview.md)
- **Resolution strategies**: [references/resolution-strategies.md](references/resolution-strategies.md)
- **Validation rules**: [references/validation-rules.md](references/validation-rules.md)
## Validation Rules

### Frontmatter Requirements
- Must start with `---`
- Required keys: `name`, `description`
- Allowed keys: `name`, `description`, `license`, `metadata`, `allowed-tools`
- Name must be hyphen-case, ≤64 chars
- Description must be ≤1024 chars, no angle brackets

### Agnostic Requirements
- No hardcoded paths (use env vars like HOME, OPENCODE_DIR, etc.)
- No hardcoded hostnames or IPs
- No hardcoded API keys or tokens
- Use environment variables for configurable paths
- Support multiple platforms

### Metadata Requirements
- Each skill must have a nested `.skill` file (e.g., `skill-name/skill-name.skill`)
- `.skill` files must contain `__skill_metadata.json`
- Metadata must include: `skill_name`, `version`, `packaged_at`, `files_count`, `size_bytes`
- Version tracking enables validation of up-to-date skillsets

### Production Requirements
- `__init__.py` must be present in skill root directory (mandatory for production/enterprise)
- Required for Python module imports and enterprise status checks

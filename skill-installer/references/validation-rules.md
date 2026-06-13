# Validation Rules Reference

## Table of Contents

- [Validation Overview](#validation-overview)
- [Frontmatter Validation](#frontmatter-validation)
- [Structure Validation](#structure-validation)
- [Content Validation](#content-validation)
- [Script Validation](#script-validation)
- [Platform Agnostic Checks](#platform-agnostic-checks)
- [Scoring System](#scoring-system)

## Validation Overview

All skills are validated against skill-creator-pro standards before installation.

### Validation Pipeline

```
Input → Format Detection → Extraction → Validation → Installation → Post-Check
                              ↓              ↓
                         skill-creator-pro  skill-creator-pro
                         validate_pro.py   validate_pro.py
```

### Validation Levels

| Level | Description | Actions |
|-------|-------------|---------|
| **Strict** | All checks must pass | Reject on any failure |
| **Standard** | Critical checks must pass | Allow warnings |
| **Lenient** | Only fatal errors reject | Ignore warnings |

## Frontmatter Validation

### Required Keys

| Key | Type | Description |
|-----|------|-------------|
| `name` | string | Skill identifier (lowercase hyphen-case) |
| `description` | string | What/when/triggers (100-1024 chars) |

### Optional Keys

| Key | Type | Description |
|-----|------|-------------|
| `license` | string | License identifier |
| `metadata` | object | Arbitrary metadata |
| `allowed-tools` | string | Tool permissions |

### Name Validation

```yaml
# Valid names
name: my-skill
name: skill-creator-pro
name: 8004scan

# Invalid names
name: My-Skill      # No uppercase
name: my_skill      # No underscores
name: my skill      # No spaces
name: a             # Too short
```

**Rules:**
- Lowercase letters, numbers, hyphens only
- Maximum 64 characters
- Must start with letter or number

### Description Validation

```yaml
# Valid description
description: "Enterprise-grade skill lifecycle manager. Creates, validates, consolidates, and maintains skills with redundancy detection. Use when: creating skills, updating skills, auditing skills."

# Invalid description
description: "A skill"  # Too short (<100 chars)
```

**Rules:**
- Minimum 100 characters
- Maximum 1024 characters
- Should include: what it does, when to use, specific triggers

## Structure Validation

### Required Files

| File | Required | Description |
|------|----------|-------------|
| `SKILL.md` | Yes | Main skill documentation |

### Optional Directories

| Directory | Purpose |
|-----------|---------|
| `scripts/` | Executable Python/Bash scripts |
| `references/` | Deep documentation |
| `assets/` | Templates, images, fonts |

### Directory Structure

```
skill-name/
├── SKILL.md              (required)
├── scripts/              (optional)
│   ├── main.py
│   └── validate.py
├── references/           (optional)
│   └── overview.md
└── assets/               (optional)
    └── template.txt
```

## Content Validation

### Line Count

- **Recommended**: ≤500 lines
- **Warning**: >500 lines
- **Critical**: >1000 lines

### Placeholder Detection

| Pattern | Status | Auto-fix |
|---------|--------|----------|
| `TODO` | Reject | No |
| `FIXME` | Reject | No |
| `TBD` | Reject | No |
| `WIP` | Reject | No |
| `coming soon` | Reject | No |
| `lorem ipsum` | Reject | No |
| `insert here` | Reject | No |
| `your name` | Reject | No |

### Hardcoded Path Detection

| Pattern | Status | Auto-fix |
|---------|--------|----------|
| Hardcoded home directory | Reject | Yes |
| Hardcoded root directory | Reject | Yes |
| Hardcoded /opt path | Reject | Yes |
| Hardcoded OpenClaw path | Reject | Yes |
| Hardcoded Hermes path | Reject | Yes |
| Hardcoded OpenCode path | Reject | Yes |
| Hardcoded temp path | Reject | Yes |

### Auto-fix Rules

```python
# Hardcoded to environment variable
"Hardcoded home directory" → "${HOME}/"
"Hardcoded root directory" → "${HOME}/"
"Hardcoded OpenCode path" → "${XDG_CONFIG_HOME:-$HOME/.config}/opencode/"
```

## Script Validation

### Shebang Line

All scripts should have shebang line:

```python
#!/usr/bin/env python3
```

```bash
#!/bin/bash
```

### Dependencies

- **Required**: Python 3.8+ stdlib only
- **Forbidden**: External packages (pip install)

### Error Handling

Scripts should handle errors gracefully:

```python
try:
    # Operation
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
```

## Platform Agnostic Checks

### Required Checks

1. **No hardcoded paths** (use env vars)
2. **No hardcoded hostnames** or IP addresses
3. **No hardcoded API keys** or tokens
4. **Environment variables** for configurable paths
5. **Cross-platform compatibility** (Linux, macOS, Windows)

### Agnostic Patterns

```bash
# Bad
PATH="APP_HOME/config"

# Good
PATH="${HOME}/.config/app"
PATH="${XDG_CONFIG_HOME:-$HOME/.config}/app"
```

## Scoring System

### Score Calculation

```python
weights = {
    "frontmatter": 0.25,
    "structure": 0.20,
    "content": 0.25,
    "scripts": 0.10,
    "skill_creator_pro": 0.20
}

# Score per check
if status == "pass":
    score = 1.0
elif status == "warning":
    score = 0.5
else:  # fail
    score = 0.0

# Weighted sum
total_score = sum(scores[check] * weights[check] for check in scores)
```

### Score Thresholds

| Score | Status | Action |
|-------|--------|--------|
| 0.9-1.0 | Pass | Install |
| 0.7-0.89 | Warning | Review recommended |
| 0.0-0.69 | Fail | Reject |

## Validation Output

### JSON Format

```json
{
  "operation": "validate",
  "timestamp": "2026-06-09T15:53:00Z",
  "status": "pass | warning | fail",
  "skill_name": "skill-name",
  "score": 0.95,
  "checks": {
    "frontmatter": {"status": "pass", "score": 1.0},
    "structure": {"status": "pass", "score": 1.0},
    "content": {"status": "warning", "score": 0.8},
    "scripts": {"status": "pass", "score": 1.0},
    "skill_creator_pro": {"status": "pass", "score": 1.0}
  },
  "issues": [],
  "warnings": ["SKILL.md too long: 520 lines"],
  "recommendation": "install"
}
```

## References

- **Skill Anatomy**: [skill-anatomy.md](skill-anatomy.md)
- **Platform Agnostic Rules**: [agnostic-rules.md](agnostic-rules.md)
- **Enterprise Standard**: [enterprise-standard.md](enterprise-standard.md)

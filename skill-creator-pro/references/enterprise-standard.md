# Enterprise Standard Reference

## Table of Contents

- [8 Pillars of Enterprise Skills](#8-pillars-of-enterprise-skills)
- [Scoring System](#scoring-system)
- [Validation Workflow](#validation-workflow)
- [Enterprise Skill Template](#enterprise-skill-template)

## 8 Pillars of Enterprise Skills

### Pillar 1: Frontmatter (20%)
**Requirements:**
- Valid YAML frontmatter
- Required keys: `name`, `description`
- Name: lowercase hyphen-case, ≤64 chars
- Description: 100-1024 chars, includes what + when + triggers
- No angle brackets in description
- Allowed keys only: name, description, license, metadata, allowed-tools

### Pillar 2: Structure (15%)
**Requirements:**
- SKILL.md present and well-formed
- scripts/ directory for executable code
- references/ directory for deep docs
- Clear file organization
- No excessive files (>50)

### Pillar 3: Content (20%)
**Requirements:**
- Comprehensive coverage of topic
- Clear, actionable instructions
- Appropriate level of detail
- No TODO/FIXME markers
- All sections have content
- Under 500 lines in SKILL.md

### Pillar 4: Agnostic (15%)
**Requirements:**
- No hardcoded paths
- No hardcoded hostnames/IPs
- Environment variables for config
- Cross-platform compatibility
- Portable file operations

### Pillar 5: Redundancy (10%)
**Requirements:**
- No significant overlap with existing skills
- Unique value proposition
- Consolidated if redundant
- Clear differentiation

### Pillar 6: Sources (10%)
**Requirements:**
- Documentation URLs verified
- API endpoints checked
- Version numbers current
- Sources documented
- Last verification date

### Pillar 7: Scripts (5%)
**Requirements:**
- Working code
- Proper error handling
- Documentation
- Uses stdlib only (free-first)
- Tested

### Pillar 8: Accessibility (5%)
**Requirements:**
- Clear trigger conditions
- Good description for activation
- Progressive disclosure
- References for deep docs

## Scoring System

| Pillar | Weight | Pass Criteria |
|--------|--------|---------------|
| Frontmatter | 20% | Valid YAML, required keys, naming |
| Structure | 15% | Proper directory layout |
| Content | 20% | Comprehensive, accurate, clear |
| Agnostic | 15% | No hardcoded paths |
| Redundancy | 10% | No significant overlap |
| Sources | 10% | Verified, documented |
| Scripts | 5% | Working, tested |
| Accessibility | 5% | Clear triggers, good description |

**Total Score:** Sum of (pillar_score × weight)

| Rating | Score Range |
|--------|-------------|
| Enterprise Grade | 90-100% |
| Production Ready | 75-89% |
| Needs Hardening | 60-74% |
| Not Enterprise | <60% |

## Validation Workflow

### 1. Automated Validation
```bash
python3 scripts/validate_pro.py /path/to/skill --verbose
```

### 2. Manual Review
- [ ] Content accuracy
- [ ] Use case coverage
- [ ] Example quality
- [ ] Reference completeness

### 3. Source Verification
```bash
python3 scripts/verify_sources.py /path/to/skill --check-urls
```

### 4. Agnostic Check
```bash
python3 scripts/fix_hardcoded.py /path/to/skill --dry-run
```

## Enterprise Skill Template

```markdown
---
name: enterprise-skill
description: "Complete enterprise solution for [use case]. When: [triggers]. Covers: [features]."
license: MIT
metadata:
  category: infrastructure
  complexity: enterprise
---

# Enterprise Skill

Brief overview.

## When to Use

- Trigger 1
- Trigger 2

## Features

- Feature 1 with details
- Feature 2 with details

## Quick Start

```bash
# Quick start command
```

## Advanced Usage

```bash
# Advanced command
```

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/main.py` | Main entry point |

## References

- **Deep dive**: [references/deep-dive.md](references/deep-dive.md)

## Sources

| Source | URL | Last Verified |
|--------|-----|---------------|
| Docs | https://... | 2026-06-05 |
```

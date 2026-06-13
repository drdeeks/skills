---
name: skill-creator
description: "Enterprise-grade skill lifecycle manager. Creates, validates, consolidates, and maintains skills with redundancy detection, source verification, and platform-agnostic enforcement. Use when: creating skills, updating skills, auditing skills, consolidating redundant skills, verifying skill accuracy against official sources, or ensuring provider-agnostic operation."
version: 0.0.3
license: MIT
metadata:
  openclaw:
    version: "1.0"
    category: infrastructure
    complexity: enterprise
---

# Skill Creator

Unified skill creation system for building both standard and enterprise-grade skills. Standard skills are lightweight and fast to create. Enterprise skills enforce 8 production pillars for autonomous, provider-agnostic, self-sufficient operation. Both tiers use the same toolchain.

## Provider Compatibility

| Provider | Compatibility | Notes |
|----------|---------------|-------|
| MuleRun | Full | Native session, compute, drive support |
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

The entire core toolchain is permanently $0. No external dependencies required.

## Pricing

This skill is **free and open-source**. All validation scripts use Python standard library only - no paid dependencies required.

**External Services Used:**
- GitHub (free tier): Repository hosting for skill distribution
- Python 3.8+ (free): Script execution environment
- No API keys required for core functionality

**Cost Breakdown:**
- Core validation: $0 (local execution only)
- Optional CI/CD: $0-5/mo (GitHub Actions free tier available)
- Optional hosting: $5-20/mo (for team skill registry)

## Core Concepts

### Skill Anatomy

```
skill-name/
├── SKILL.md              (required — frontmatter + instructions)
├── scripts/              (optional — executable Python/Bash)
├── references/           (optional — docs loaded on demand)
│   └── lessons/          (optional — operational lessons learned)
└── assets/               (optional — templates, images, fonts for output)
```

### Standard vs Enterprise

| Aspect | Standard | Enterprise |
|---|---|---|
| Use case | Simple tools, quick workflows | Production autonomous systems |
| SKILL.md only? | Yes (+ optional resources) | No — requires scripts/ + references/ |
| Provider table | Optional | Required |
| Free-first docs | Optional | Required |
| Output statistics | Optional | Required (every operation) |
| Error handling | Optional | Required (full catalog) |
| Validation | `validate.py` | `validate_pro.py` (8 pillars) |

Choose **standard** for focused, single-purpose skills. Choose **enterprise** when the skill will run autonomously, handle failures, track costs, or scale across providers.

## Enforced Output Statistics

Every script produces structured output on completion:

```json
{
  "operation": "validate | consolidate | verify | scan",
  "timestamp": "ISO8601",
  "status": "success | failed",
  "skill_name": "the-skill-name",
  "details": {},
  "cost": {"tier": 0, "amount_usd": 0.0, "service": "local"}
}
```

## Core Capabilities

| Capability | Description |
|------------|-------------|
| **Create** | Build new skills from scratch with enterprise-grade structure |
| **Validate** | Multi-layer validation (frontmatter, structure, agnostic, redundancy) |
| **Scan** | Multi-source directory scanning for skill discovery |
| **Consolidate** | Merge redundant/overlapping skills into robust singular skills |
| **Verify** | Source verification against official documentation |
| **Update** | Intelligent skill updates with change tracking |
| **Report** | Comprehensive audit reports with recommendations |

## When to Use

| Trigger | Action |
|---------|--------|
| Creating a new skill | Full creation workflow with validation |
| Updating an existing skill | Analyze, validate, consolidate if needed |
| Auditing skill directory | Scan, validate, detect redundancy |
| Skill feels incomplete | Consolidate with related skills |
| Verifying skill accuracy | Source verification workflow |
| Before deployment | Full validation pass |

## Workflow: Create New Skill

### Step 1: Gather Requirements
- What should this skill do?
- What triggers it?
- What does it NOT do?
- Official documentation URLs?

### Step 2: Check for Redundancy
```bash
python3 scripts/detect_redundancy.py --skill-name "my-skill" --target /path/to/skills/
```
- Scans existing skills for overlapping functionality
- Identifies potential consolidation candidates
- Reports similarity scores

### Step 3: Initialize Skill

```bash
# Standard skill
python3 scripts/init_skill.py my-skill --path /target/dir
python3 scripts/init_skill.py my-skill --path /target/dir --resources scripts,references,references/lessons

# Enterprise skill (all 8 pillars pre-scaffolded)
python3 scripts/init_skill.py my-skill --path /target/dir --enterprise

# Preview without creating files
python3 scripts/init_skill.py my-skill --path /target/dir --enterprise --dry-run
```

### Step 4: Build Content
- Scripts in `scripts/` (deterministic backbone)
- References in `references/` (deep docs)
- References in `references/lessons/` (operational lessons learned)
- Assets in `assets/` (templates, images)
- SKILL.md last (under 500 lines)

### Step 5: Validate
```bash
# Quick validation (frontmatter, structure)
python3 scripts/validate.py /path/to/skill

# Enterprise validation (all 8 pillars, scored)
python3 scripts/validate_pro.py /path/to/skill --verbose
```

### Step 6: Package
```bash
python3 scripts/package_skills.py --skills-root /path/to/skills --skill my-skill --output-dir /path/to/output
```

Refer to [references/packaging.md](references/packaging.md) for full packaging workflow.

## Workflow: Update Existing Skill

### Step 1: Analyze Current State
```bash
python3 scripts/analyze_skill.py /path/to/skill --deep
```
- Frontmatter validation
- Content accuracy check
- Redundancy detection against other skills
- Source verification

### Step 2: Identify Issues
The analyzer reports:
- **Frontmatter issues**: Invalid keys, missing fields
- **Content issues**: Outdated information, broken references
- **Redundancy issues**: Overlapping skills that could be consolidated
- **Agnostic issues**: Hardcoded paths or platform-specific references
- **Source issues**: Unverified claims, missing citations

### Step 3: Consolidate (if needed)
```bash
python3 scripts/consolidate_skills.py --skills skill-a skill-b skill-c --output merged-skill
```
- Merges overlapping functionality
- Preserves unique features from each
- Eliminates duplication
- Creates single robust skill

### Step 4: Verify Sources
```bash
python3 scripts/verify_sources.py /path/to/skill --check-urls --check-apis
```
- Validates all documentation URLs
- Checks API endpoints
- Verifies version numbers
- Reports outdated information

### Step 5: Re-validate
```bash
python3 scripts/validate_pro.py /path/to/skill --full
```

## Workflow: Upgrade Standard to Enterprise

1. Run `validate_pro.py` on the existing skill to see gaps
2. Add missing components (scripts, references, enterprise sections)
3. Re-validate until 0 FAIL, 0 WARN
4. Re-package

## Workflow: Audit Skill Directory

### Full Audit
```bash
python3 scripts/validate_pro.py /path/to/skills/ --json
```

Produces report with:
- Total skills scanned
- Validation status per skill
- Redundancy matrix
- Source verification status
- Recommendations

### Quick Health Check
```bash
python3 scripts/validate.py /path/to/skill
```

## Redundancy Detection

### How It Works

1. **Keyword Analysis**: Extracts keywords from SKILL.md
2. **Functionality Mapping**: Maps what each skill does
3. **Overlap Scoring**: Calculates similarity between skills
4. **Consolidation Recommendations**: Suggests merges

### Redundancy Thresholds

| Score | Action |
|-------|--------|
| 0.0-0.3 | No overlap |
| 0.3-0.5 | Minor overlap (review) |
| 0.5-0.7 | Significant overlap (consolidate) |
| 0.7-1.0 | Major overlap (merge required) |

### Consolidation Rules

1. **Preserve unique features** from each skill
2. **Merge common functionality** into shared modules
3. **Update all references** to point to new skill
4. **Maintain backward compatibility** where possible
5. **Document changes** in changelog

## Source Verification

### Verification Types

| Type | Description |
|------|-------------|
| **URL Check** | Validates documentation URLs are reachable |
| **API Check** | Verifies API endpoints are active |
| **Version Check** | Ensures version numbers are current |
| **Content Check** | Validates technical accuracy |
| **License Check** | Verifies license compatibility |

### Source Documentation Format

Every skill should document:

```markdown
## Sources

| Source | URL | Last Verified | Status |
|--------|-----|---------------|--------|
| Official Docs | https://... | 2026-06-05 | Active |
| API Reference | https://... | 2026-06-05 | Active |
| GitHub Repo | https://... | 2026-06-05 | Active |

### Verification Quick Check
- Docs URL responds with 200: ✓
- API endpoint returns valid JSON: ✓
- GitHub repo has recent commits: ✓
```

## Platform-Agnostic Enforcement

### Required Checks

1. **No hardcoded paths** (use env vars like HOME, APP_DIR, etc.)
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

## Scripts Reference

| Script | Purpose | Usage |
|--------|---------|-------|
| `scripts/init_skill.py` | Initialize new skills (standard or enterprise) | `name --path dir --enterprise` |
| `scripts/validate.py` | Quick validation (frontmatter, structure) | `skill-dir` |
| `scripts/validate_pro.py` | Full validation suite (8 pillars) | `skill-dir --verbose` |
| `scripts/analyze_skill.py` | Deep skill analysis | `skill-dir --deep` |
| `scripts/consolidate_skills.py` | Merge redundant skills | `--skills a b c --output dir` |
| `scripts/detect_redundancy.py` | Find overlapping skills | `--skill-name name --target dir` |
| `scripts/verify_sources.py` | Verify documentation | `skill-dir --check-urls` |
| `scripts/upgrade_to_enterprise.py` | Upgrade standard to enterprise | `skill-dir` |
| `scripts/package_skills.py` | Package skills as .skill files | `--skills-root dir --skill name` |

## Enterprise Validation Pillars

| Pillar | Weight | Description |
|--------|--------|-------------|
| Frontmatter | 20% | Valid YAML, required keys, naming conventions |
| Structure | 15% | Directory layout, file organization |
| Content | 20% | Accuracy, completeness, clarity |
| Agnostic | 15% | No hardcoded paths, cross-platform |
| Sources | 10% | Documented, verified, current |
| Syntax | 10% | Working code, proper error handling |
| Enterprise | 15% | Provider compat, free-first, output stats |
| Accessibility | 5% | Clear triggers, good descriptions |

See [references/standards.md](references/standards.md) for full scoring system, validation levels, and quality checklist.

## Permissions Validation

### Required Standards

| Type | Permission | Description |
|------|------------|-------------|
| Directories | `755` (rwxr-xr-x) | Owner write, all read/execute |
| Files | `644` (rw-r--r--) | Owner write, all read |
| Secrets dir | `755` (NOT 700) | Group-accessible for collaboration |

### Forbidden Permissions

| Permission | Reason |
|------------|--------|
| `700` on directories | Locks out co-developers and group members |
| `777` on anything | World-writable, security risk |
| `600` on non-secrets | Blocks group access unnecessarily |

## Information Quality Validation

### Completeness Checks

| Check | Description |
|-------|-------------|
| **API Endpoints** | All endpoints documented with method, path, body, response |
| **Code Examples** | Every function has at least one working example |
| **Error States** | All error conditions documented with codes and messages |
| **Configuration** | All env vars, config files, and options listed |
| **Prerequisites** | Dependencies, versions, and setup steps documented |

### Robustness Checks

| Check | Description |
|-------|-------------|
| **Edge Cases** | Boundary conditions and error handling covered |
| **Idempotency** | Repeated operations don't cause side effects |
| **Rollback** | Every state change has a documented reversal |
| **Timeout** | Long operations have timeout and retry behavior |
| **Graceful Degradation** | Fallback behavior when dependencies unavailable |

### Accuracy Checks

| Check | Description |
|-------|-------------|
| **API URLs** | Endpoints respond with expected status codes |
| **Code Syntax** | All code examples parse without errors |
| **Version Numbers** | Match current releases |
| **No Placeholder Secrets** | Example keys clearly marked as examples |

## Consolidation Precision Protocol

### When Merging Skills

1. **Read ALL source files completely** before writing anything
2. **Map content to sections** — identify where each piece belongs
3. **Deduplicate** — same information in multiple sources, keep one copy
4. **Preserve unique features** — never drop skill-specific functionality
5. **Merge common modules** — shared code goes in shared location
6. **Update all references** — internal links point to new structure
7. **Verify completeness** — every source file's content appears somewhere
8. **Test consolidated skill** — validate structure and content

### Consolidation Checklist

- [ ] All source SKILL.md files read completely
- [ ] All reference files copied (no duplicates)
- [ ] All scripts merged (no conflicts)
- [ ] YAML frontmatter merged with combined description
- [ ] Content organized logically (not just appended)
- [ ] Duplicate sections removed
- [ ] Internal cross-references updated
- [ ] No information lost from any source
- [ ] Permissions set correctly (755/644)
- [ ] Validation passes on consolidated skill

## Error Handling

| Error | Response |
|-------|----------|
| Redundancy detected | Report overlap, suggest consolidation |
| Source unreachable | Flag for manual verification |
| Invalid frontmatter | Auto-fix if possible, report if not |
| Hardcoded path found | Replace with environment variable |
| Missing required field | Prompt for content |

See [references/error-handling.md](references/error-handling.md) for full error catalog, common validation failures, and recovery procedures.

## Enhancement Hooks

| Skill | Enhancement | When to Add |
|-------|-------------|-------------|
| `skill-scan-validate-resolver` | Multi-source scanning | When auditing skill directories |
| `html-report` | Visual validation dashboard | When auditing many skills |
| `xlsx` | Export validation results | When tracking skill quality metrics |
| `skill-finder` | Discover complementary skills | When building enterprise skills |
| `frontend-design` | Premium UI for documentation | When skills need user-facing docs |

## Key References

- **Enterprise standards, scoring, validation levels**: [references/standards.md](references/standards.md) — Read when building or auditing enterprise-grade skills
- **Skill anatomy**: [references/skill-anatomy.md](references/skill-anatomy.md) — Read when structuring skill directories
- **Consolidation patterns**: [references/consolidation-patterns.md](references/consolidation-patterns.md) — Read when merging redundant skills
- **Source verification guide**: [references/source-verification.md](references/source-verification.md) — Read when verifying skill accuracy
- **Agnostic enforcement rules**: [references/agnostic-rules.md](references/agnostic-rules.md) — Read when ensuring cross-platform compatibility
- **Packaging workflow**: [references/packaging.md](references/packaging.md) — Read when packaging skills for distribution
- **Error catalog and recovery**: [references/error-handling.md](references/error-handling.md) — Read when diagnosing validation or packaging failures
- **Free-first cost analysis**: [references/free-first-strategy.md](references/free-first-strategy.md) — Read when evaluating toolchain costs
- **Output patterns**: [references/output-patterns.md](references/output-patterns.md) — Read when defining skill output formats
- **Workflow design patterns**: [references/workflows.md](references/workflows.md) — Read when structuring multi-step skill workflows

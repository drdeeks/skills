---
name: enterprise-organization
description: "Enterprise-grade organization management for AI agent systems. Enforces modular file tree, security hardening, gitignore standards, task-driven task validation, zero-placeholder code policy, rigorous self-validation with rollback, append-only CHANGELOG.md with decision rationale, phase-tagged workflow, semantic versioning with automated releases, and robust git control. When: setting up new agent workspaces, auditing existing projects, enforcing enterprise standards, scaling agent infrastructure, managing phased development, releasing versions, controlling git operations. Triggers: 'enterprise setup', 'workspace audit', 'security hardening', 'modular enforcement', 'CHANGELOG enforcement', 'placeholder removal', 'phase management', 'version release', 'git control'."
license: MIT
metadata:
  category: infrastructure
  complexity: enterprise
  tags:
    - enterprise
    - organization
    - security
    - gitignore
    - modular
    - validation
    - changelog
    - standards
    - phase-management
    - semantic-versioning
    - git-control
    - release-management
version: 0.0.4
---

# Enterprise Organization

Enterprise-grade organization management for multi-agent AI systems. Provides standardized workspace structure, security hardening, modular file tree enforcement, task-driven task validation, rigorous self-validation with rollback capabilities, phase-tagged workflow, semantic versioning with automated releases, and robust git control.

## When to Use

- Setting up new agent workspaces with enterprise standards
- Auditing existing projects for compliance
- Enforcing security hardening and gitignore standards
- Modular file tree enforcement across agents
- Zero-placeholder code policy enforcement
- Rigorous self-validation with rollback capabilities
- Append-only CHANGELOG.md with decision rationale tracking
- Phase-tagged development workflow
- Semantic versioning with automated release management
- Robust git control with hooks, branching, and sync

## Features

### Modular File Tree Enforcement
- Standardized directory structure per agent/project
- Role-based workspace layouts (Hermes/Titan/Avery/Allman)
- Automatic validation of file tree compliance
- Auto-correction of structural deviations

### Security Hardening & Gitignore Standards
- Comprehensive .gitignore templates per project type
- Secrets detection and prevention
- Permission auditing (700/600 enforcement)
- Supply chain security checks

### Task-Driven Task Validation
- Mandatory task plans for all work
- Thorough validation of task completion
- No task marked complete without verification evidence
- Automatic rollback on validation failure

### Zero-Placeholder Code Policy
- Detects TASK_MARKER/TASK_MARKER/TASK_MARKER/work in progress markers
- Rejects stub implementations
- Enforces real, wholesome, valid code only
- Validates against templates and patterns

### Rigorous Self-Validation
- Modular design verification
- Rollback option verification
- Performance benchmarking
- Cross-reference validation

### Append-Only CHANGELOG.md
- Every phase/task auto-updates CHANGELOG
- Includes: datetime, author, changes, method, validation, reasoning
- Immutable history with cryptographic hash chain
- Query by phase, author, date range

### Phase-Tagged Workflow (NEW)
- Define phases with metadata and tags
- Start phases with git tags and CHANGELOG entries
- Complete phases with summary and validation
- List and show phase history
- Tag files per phase for traceability
- Phase tags: `phase-<name>-start`, `phase-<name>-complete`

### Semantic Versioning & Release Management (NEW)
- Get, set, bump (major/minor/patch) versions
- Create annotated release tags
- Generate release notes from git log and CHANGELOG
- Version persisted in VERSION file, pyproject.toml, package.json
- Prerelease support
- List all versions from git tags

### Robust Git Control (NEW)
- Status, add, commit with signing/amend
- Push/pull with rebase and tag support
- Branch management (create, delete, list, merge)
- Merge with no-ff and squash options
- Log with filtering (limit, since, author)
- Diff (staged/unstaged, per file)
- Stash management (push, pop, drop, list)
- Git hooks setup (pre-commit, commit-msg, pre-push)
- Full sync (pull + push + tags)
- Enterprise pre-commit validation (placeholder, security)

### Combined Release Workflow (NEW)
- One-command release: bump version, tag, generate notes, update CHANGELOG, push
- Configurable bump type (major/minor/patch)
- Automatic phase tagging for releases
- Release notes from commits and CHANGELOG

## Quick Start

```bash
# Initialize enterprise organization for a project
python3 scripts/enterprise-org.py init --project my-agent --role hermes

# Validate existing workspace
python3 scripts/enterprise-org.py validate --workspace /path/to/workspace

# Enforce standards
python3 scripts/enterprise-org.py enforce --workspace /path/to/workspace --fix

# Generate CHANGELOG entry
python3 scripts/enterprise-org.py changelog --phase "security-hardening" --author "agent-name" --reason "Applied enterprise gitignore"

# Phase management
python3 scripts/enterprise-org.py phase --action start --phase "feature-development" --no-commit
python3 scripts/enterprise-org.py phase --action complete --phase "feature-development" --summary "Implemented user auth"
python3 scripts/enterprise-org.py phase --work plan

# Version management
python3 scripts/enterprise-org.py version --action bump --bump-type patch
python3 scripts/enterprise-org.py version --action release --version-arg 1.2.0 --push
python3 scripts/enterprise-org.py version --action notes --version-arg 1.2.0

# Git operations
python3 scripts/enterprise-org.py git --git-action status
python3 scripts/enterprise-org.py git --git-action commit --commit-message "feat: add feature"
python3 scripts/enterprise-org.py git --git-action push --remote origin --branch main --tags
python3 scripts/enterprise-org.py git --git-action sync

# Full release workflow
python3 scripts/enterprise-org.py release --bump patch --release-message "Patch release with bug fixes"
```

## Advanced Usage

```bash
# Full audit with report
python3 scripts/enterprise-org.py audit --workspace /path/to/workspace --report enterprise-audit.json

# Validate todo completion
python3 scripts/enterprise-org.py validate-todos --workspace /path/to/workspace --strict

# Check for placeholders
python3 scripts/enterprise-org.py scan-placeholders --workspace /path/to/workspace --fail-on-found

# Verify rollback capability
python3 scripts/enterprise-org.py verify-rollback --workspace /path/to/workspace

# Phase tagging files
python3 scripts/enterprise-org.py phase --action tag-files --phase "release-prep" --pattern "scripts/*.py" --message "Release prep scripts"

# Git hooks setup
python3 scripts/enterprise-org.py git --git-action hooks

# Branch management
python3 scripts/enterprise-org.py git --git-action branch --name feature/auth --create
python3 scripts/enterprise-org.py git --git-action merge --source feature/auth --target main --no-ff

# View version history
python3 scripts/enterprise-org.py version --work plan
```

## Scripts Reference

| Script | Purpose | Usage |
|--------|---------|-------|
| `scripts/enterprise-org.py` | Main entry point - init, validate, enforce, audit, changelog, phase, version, git, release | `python3 scripts/enterprise-org.py --help` |
| `scripts/main.py` | Standardized entry point with skill metadata | `python3 scripts/main.py` |
| `scripts/validate.py` | Skill structure validation | `python3 scripts/validate.py` |
| `scripts/validate_structure.py` | Modular file tree validation | `python3 scripts/validate_structure.py --workspace /path` |
| `scripts/security_hardening.py` | Security & gitignore enforcement | `python3 scripts/security_hardening.py --workspace /path --fix` |
| `scripts/todo_validator.py` | task completion validation | `python3 scripts/todo_validator.py --workspace /path --strict` |
| `scripts/placeholder_scanner.py` | Zero-placeholder enforcement | `python3 scripts/placeholder_scanner.py --workspace /path --fail-on-found` |
| `scripts/self_validator.py` | Rigorous self-validation with rollback | `python3 scripts/self_validator.py --workspace /path --verify-rollback` |
| `scripts/changelog_manager.py` | Append-only CHANGELOG management | `python3 scripts/changelog_manager.py --action add --phase "phase" --author "agent" --reason "..."` |
| `scripts/version_manager.py` | Semantic versioning & releases | `python3 scripts/version_manager.py --help` |
| `scripts/git_control.py` | Robust git operations | `python3 scripts/git_control.py --help` |
| `scripts/phase_tagger.py` | Phase tagging & tracking | `python3 scripts/phase_tagger.py --help` |

## Key References

- **Modular File Tree Standard**: [references/modular-file-tree.md](references/modular-file-tree.md)
- **Security & Gitignore Standards**: [references/security-gitignore.md](references/security-gitignore.md)
- **task Validation Protocol**: [references/todo-validation.md](references/todo-validation.md)
- **Zero-Placeholder Policy**: [references/zero-placeholder.md](references/zero-placeholder.md)
- **Self-Validation Framework**: [references/self-validation.md](references/self-validation.md)
- **CHANGELOG Protocol**: [references/changelog-protocol.md](references/changelog-protocol.md)
- **Rollback Procedures**: [references/rollback-procedures.md](references/rollback-procedures.md)
- **Phase Management**: [references/phase-management.md](references/phase-management.md)
- **Semantic Versioning**: [references/semantic-versioning.md](references/semantic-versioning.md)
- **Git Control**: [references/git-control.md](references/git-control.md)
- **Release Workflow**: [references/release-workflow.md](references/release-workflow.md)

## Sources

| Source | URL | Last Verified |
|--------|-----|---------------|
| Gitignore Templates | https://github.com/github/gitignore | 2026-06-09 |
| OpenSSF Scorecard | https://github.com/ossf/scorecard | 2026-06-09 |
| NIST SSDF | https://csrc.nist.gov/Projects/ssdf | 2026-06-09 |
| Semantic Versioning | https://semver.org | 2026-06-09 |
| Keep a Changelog | https://keepachangelog.com | 2026-06-09 |
| Git SCM | https://git-scm.com | 2026-06-09 |
| Conventional Commits | https://www.conventionalcommits.org | 2026-06-09 |


## Workflow

### Step 1: Installation

```bash
# No external dependencies - all scripts use Python stdlib only
# Free-First Strategy Tier 0: $0/mo
```

### Step 2: Initialize Workspace

```bash
python3 scripts/enterprise-org.py init --project my-agent --role hermes
```

### Step 3: Development Workflow

```bash
# Start a development phase
python3 scripts/enterprise-org.py phase --action start --phase "feature-x"

# Work on feature...

# Complete phase with validation
python3 scripts/enterprise-org.py phase --action complete --phase "feature-x" \
  --summary "Implemented feature X with tests"

# Release when ready
python3 scripts/enterprise-org.py release --bump minor --release-message "New feature X"
```

### Step 4: Validation

```bash
# Continuous validation
python3 scripts/enterprise-org.py validate --workspace .

# Full audit before release
python3 scripts/enterprise-org.py audit --workspace . --report audit.json
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
| `skill-creator` | Basic skill creation | When creating simple skills |
| `skill-creator-pro` | Enterprise upgrade | When upgrading to enterprise |
| `html-report` | Visual validation dashboard | When auditing many skills |
| `xlsx` | Export validation results | When tracking skill quality metrics |
| `agent-bootstrap-manager` | Agent workspace creation | When bootstrapping new agents |

## Enforcement Rules

1. **Every task requires a work plan**
2. **No task marked complete without validation evidence** - Verification artifacts required
3. **No placeholders/TASK_MARKERs/TASK_MARKERs in production code** - Zero tolerance
4. **Every change logged to CHANGELOG.md** - Immutable, append-only with rationale
5. **Modular file tree enforced at all times** - Auto-correction on deviation
6. **Security standards non-negotiable** - .gitignore, permissions, secrets
7. **Rollback capability verified before deployment** - Test rollback pre-commit
8. **Self-validation runs on every operation** - Continuous compliance
9. **Phases tagged in git** - Every phase start/complete creates git tag
10. **Versions follow semver** - Automated bumping and tagging
11. **Git hooks enforce standards** - Pre-commit validation, commit-msg format, pre-push checks

## Phase Management Details

### Phase Lifecycle
```
define → start → (work) → complete → tag files
```

### Phase Tags in Git
- Start: `phase-<name>-<timestamp>` (annotated)
- Complete: `phase-<name>-complete-<timestamp>` (annotated)
- Files: `phase-<name>-files-<timestamp>` (annotated)

### Phase Storage
- Definitions: `.phases.json` (machine-readable)
- CHANGELOG: Human-readable entries per phase
- Tasks.md: Phase-based task tracking

## Version Management Details

### Version Sources (priority order)
1. Git tags (`v*`)
2. VERSION file
3. pyproject.toml
4. package.json
5. setup.py

### Release Tags
- Format: `v<major>.<minor>.<patch>` (e.g., `v1.2.3`)
- Annotated with message
- Pushed with `--tags` option

### Release Notes
Generated from:
- Commits since last tag
- CHANGELOG entries for version
- Formatted as Markdown

## Git Control Details

### Pre-commit Hook
Runs:
- Placeholder scanner (fail on found)
- Security hardening check

### Commit-msg Hook
Validates conventional commit format:
```
type(scope): description
e.g., feat(auth): add OAuth2 login
```

### Pre-push Hook
Runs full validation:
- `enterprise-org.py validate`

### Branch Strategy
- Main branch: `main` (protected)
- Feature branches: `feature/*`
- Release branches: `release/*`
- Hotfix branches: `hotfix/*`

### Merge Options
- `--no-ff`: Preserve branch history
- `--squash`: Single commit for feature

## Verification

```bash
# Full diagnostic scan
python3 scripts/enterprise-org.py audit --workspace .

# Test phase workflow
python3 scripts/enterprise-org.py phase --action start --phase test-phase
python3 scripts/enterprise-org.py phase --action complete --phase test-phase --summary "Test done"

# Test version workflow
python3 scripts/enterprise-org.py version --action bump --bump-type patch
python3 scripts/enterprise-org.py version --action release --version-arg 1.0.1

# Test git hooks
python3 scripts/enterprise-org.py git --git-action hooks

# Verify rollback
python3 scripts/self_validator.py --workspace . --verify-rollback
```

## Dry-Run Pattern (Reusable)

For any bash script with mutating operations:

```bash
# Parse flag before main logic
DRY_RUN=false
for arg in "$@"; do
    case "$arg" in
        --dry-run|-n) DRY_RUN=true; shift ;;
    esac
done

# Wrapper function
run() {
    if [ "$DRY_RUN" = true ]; then
        echo "[dry-run] $*"
        return 0
    fi
    "$@"
}

# Wrap all mutating commands
run mkdir -p "$dir"
run rm -f "$file"
run ln -sf "$src" "$dst"
run chmod 600 "$file"
run git -C "$dir" init

# For heredoc file writes, guard with if-block
if [ "$DRY_RUN" = false ]; then
    { echo "content"; } > "$file"
else
    echo "[dry-run] Write → $file"
fi
```
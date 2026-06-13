---
description: Scan filesystems for "skills" directories, index files into SQLite, search,
  diff, deduplicate by content hash, and canonicalize by version. Handles large trees,
  symlinks, and node_modules bloat.
name: filesystem-skill-scanner
version: 0.0.5
---

# Filesystem Skill Scanner

Python CLI tool for scanning, searching, diffing, and deduplicating files inside `skills/` directories across multiple agent profiles.

## When to Use

- Inventorying skills across multiple agent workspaces
- Finding duplicate skills between agent profiles
- Detecting content-duplicate files (same hash, different paths)
- Canonicalizing versioned skill copies into a single clean directory
- Comparing what changed between scans over time

## Commands

```bash
python skill_scanner.py scan --root /path/to/agent --db skills.sqlite
python skill_scanner.py find SKILL.md .yaml agent --db skills.sqlite
python skill_scanner.py diff --db skills.sqlite
python skill_scanner.py dedup --db skills.sqlite
python skill_scanner.py canonicalize --db skills.sqlite --out /tmp/canonical
python skill_scanner.py prune --keep 5 --db skills.sqlite
```

## Key Design Decisions (Lessons Learned)

### 1. SKIP_DIRS pruning is critical
Without pruning `node_modules`, `.git`, `venv`, `__pycache__`, etc., a single skills dir can contain 100k+ files (skill dependencies). Always prune these at the `os.walk` level by modifying `dirs[:]` in-place.

```python
SKIP_DIRS = {
    "node_modules", ".git", ".svn", ".hg",
    "__pycache__", ".pytest_cache", ".mypy_cache",
    "venv", ".venv", "env", ".env",
    ".cache", ".tox", ".eggs", "dist", "build",
    ".next", ".nuxt", ".output",
}

for base, dirs, files in os.walk(root, followlinks=False):
    dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
```

### 2. EXCLUDES must use exact path prefix matching
Naive `startswith("/proc")` matches `/procedure`. Use exact set membership per path segment:

```python
def is_excluded(path):
    parts = Path(path).parts
    for i in range(1, len(parts) + 1):
        if os.sep.join(parts[:i]) in EXCLUDES:
            return True
    return False
```

### 3. Symlinked target directories need explicit handling
`os.walk(followlinks=False)` skips symlinked dirs entirely. If your target dir name (`skills/`) is a symlink, pre-check and resolve it before the walk:

```python
if os.path.islink(full_entry):
    resolved = os.path.realpath(full_entry)
    if os.path.isdir(resolved):
        # manually walk the resolved path
```

### 4. Deduplicate by realpath to handle symlinked content
Multiple agent profiles often symlink to the same skills dir (e.g., `.avery.gateway/skills` -> `.hermes/skills`). Track `os.realpath()` in a set to avoid indexing the same file twice:

```python
seen_real = set()
real = os.path.realpath(full)
if real in seen_real:
    continue
seen_real.add(real)
```

### 5. Version extraction needs word-boundary anchoring
Regex `[vV]\d+` false-positives on words like "overview". Require a separator before `v`:

```python
re.findall(r'(?:^|[-_/.\s])[vV][-_]?(\d+(?:\.\d+)*)', name)
```

### 6. Use `except (OSError, IOError)` not bare `except:`
Bare except catches `KeyboardInterrupt`, `SystemExit`, `MemoryError`. Only catch filesystem errors.


## Workflow

### Step 1: Installation

```bash
# Install dependencies if needed
```

### Step 2: Configuration

```bash
# Configure the skill
```

### Step 3: Usage

```bash
# Use the skill
python3 scripts/main.py
```

### Step 4: Validation

```bash
# Validate the skill
python3 scripts/validate.py
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


## Scripts Reference

| Script | Purpose | Usage |
|--------|---------|-------|
| `scripts/skill_scanner.py` | filesystem-skill-scanner script | Run with python3 |
| `scripts/validate.py` | filesystem-skill-scanner script | Run with python3 |

## Key References

- **Overview**: [references/overview.md](references/overview.md)
## Pitfalls

- **Full `/` or `/home` scans are too slow** — always scope to specific agent roots
- **Symlink loops** can hang `os.walk` even with `followlinks=False` on some OS — `realpath` dedup prevents this
- **Hash column stored but unused** is a common oversight — `dedup` command uses it, make sure both exist
- **DB grows unbounded** without `prune` — always pair scans with periodic pruning
- **WAL mode** (`PRAGMA journal_mode=WAL`) is important for concurrent read performance on SQLite
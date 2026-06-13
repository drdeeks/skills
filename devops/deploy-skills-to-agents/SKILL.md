---
name: deploy-skills-to-agents
category: devops
description: Deploy global skills to all OpenClaw agent workspaces without symlinks.
---

# Deploy Skills to Agents

Deploy global skills to all OpenClaw agent workspaces.

## Problem
OpenClaw rejects skill paths that resolve outside the agent's configured workspace root. Symlinking `<agent>/skills/<name>` → `${OPENCLAW_DIR:-~/.openclaw}/agents/.skills/<name>` causes:
- 4899+ log warnings ("Skipping skill path that resolves outside its configured root")
- Gateway log flood drowning out real errors
- Bots not responding to messages

**Key finding: NEVER symlink. Copy instead.**

## Steps

### 1. Build canonical set in .skills/

```bash
python3 -c "
from pathlib import Path
import shutil

TARGET = Path.home() / '.openclaw' / 'agents' / '.skills'
TARGET.mkdir(parents=True, exist_ok=True)

all_skills = {}

def collect(root):
    if not root.exists(): return
    for item in root.iterdir():
        if item.name.startswith('.') or item.name in ('__pycache__','node_modules','venv'): continue
        if not item.is_dir(): continue
        if (item / 'SKILL.md').exists() and item.name not in all_skills:
            all_skills[item.name] = item
        collect(item)

for src in [
    Path.home() / '.hermes' / 'hermes-agent' / 'skills',
    Path.home() / '.hermes' / 'hermes-agent' / 'optional-skills',
    Path.home() / '.openclaw' / 'agents' / '.skills',
    Path.home() / '.hermes' / 'skills',
]:
    collect(src)

for name, src in sorted(all_skills.items()):
    dst = TARGET / name
    if dst.exists() and (dst / 'SKILL.md').exists(): continue
    if dst.exists(): shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns('__pycache__','*.pyc','.git','node_modules','venv'))

print(f'Done: {len(all_skills)} skills in {TARGET}')
"
```

### 2. Copy to each agent (NOT symlink)

```bash
python3 -c "
import shutil
from pathlib import Path

GLOBAL = Path.home() / '.openclaw' / 'agents' / '.skills'
AGENTS = Path.home() / '.openclaw' / 'agents'

for agent in ['allman','aton','avery','guard','main','mort','titan','tom','hermes']:
    skills_dir = AGENTS / agent / 'skills'
    skills_dir.mkdir(parents=True, exist_ok=True)
    copied = 0
    for skill in GLOBAL.iterdir():
        if not skill.is_dir() or skill.name.startswith('.'): continue
        dst = skills_dir / skill.name
        if dst.exists() and dst.is_dir() and not dst.is_symlink(): continue
        if dst.is_symlink(): dst.unlink()
        if dst.exists(): shutil.rmtree(dst)
        shutil.copytree(skill, dst, ignore=shutil.ignore_patterns('__pycache__','*.pyc','.git','node_modules','venv'))
        copied += 1
    total = len([d for d in skills_dir.iterdir() if d.is_dir() and not d.name.startswith('.')])
    print(f'{agent}: copied {copied}, total {total}')
"
```

### 3. Restart gateway

```bash
systemctl --user restart openclaw-gateway
```

## Pitfalls
- **NEVER symlink** — OpenClaw resolves symlinks and rejects paths outside agent root
- Agent-owned skills (created by the agent) take priority — don't overwrite them
- Optional skills are nested in categories (mlops/, research/, etc.) — must flatten
- Restart gateway after deployment — old log flood needs clearing
- Skills with broken symlinks inside them fail to copy — skip them

## Verification
```bash
# No "Skipping skill path" warnings
tail -100 ${TMPDIR:-/tmp}/openclaw-*.log | grep -c "Skipping skill path"  # should be 0

# Agents responding
journalctl --user -u openclaw-gateway -f | grep -v "skill\|Skipping"
```

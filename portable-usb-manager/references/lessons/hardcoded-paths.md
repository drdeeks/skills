---
title: Hardcoded Paths Break Portability
category: portability
date: 2026-06-10
failure: >
  A script hardcoded a developer-machine-specific path and username
  ($USER-based log file), so it worked in development but failed the
  moment it ran on a different machine or as a different user.
root_cause: >
  Path and username assumptions were baked in as literals instead of
  resolved at runtime from the script's own location and the environment.
resolution: >
  Derived the script directory from BASH_SOURCE[0] instead of a literal
  path, and used mktemp for log files instead of a $USER-suffixed literal.
prevention: >
  Never hardcode user paths or usernames; resolve script location via
  BASH_SOURCE[0] and use mktemp for anything temporary. Test on a clean
  environment before deploying.
verified: true
---

# Lesson: Hardcoded Paths Break Portability

## Context
Script developed on one machine, deployed to another.

## What Happened
```bash
# BROKEN — hardcoded path
local script_dir="/path/to/your/project/scripts"

# BROKEN — assumes specific user
LOG_FILE="/tmp/usb-setup-$USER.log"
```
Script worked on development machine but failed on production.

## Resolution
```bash
# CORRECT — derive from script location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# CORRECT — use system temp directory
LOG_FILE="$(mktemp /tmp/usb-setup-XXXXXX.log)"
```

## Prevention
- Never hardcode user paths or usernames
- Use `BASH_SOURCE[0]` for script directory
- Use `mktemp` for temporary files
- Test on a clean environment before deploying

## Date: 2026-06-10
## Verified: yes

---
title: Ventoy2Disk.sh Has No -y Flag
category: usb-hardware
date: 2026-06-10
failure: >
  An automated Ventoy install script crashed immediately with no visible
  error after passing an assumed -y flag — Ventoy2Disk.sh treated -y as an
  unrecognized flag and interpreted it as a (nonexistent) device path.
root_cause: >
  The script assumed a common convention flag (-y/--yes) existed without
  checking Ventoy2Disk.sh's actual supported flag list, and the ERR trap
  swallowed the resulting error before it could be diagnosed.
resolution: >
  Removed the -y flag entirely and instead piped two "y" answers into
  Ventoy2Disk.sh's two real interactive confirmation prompts.
prevention: >
  Always check `command --help` before assuming a CLI flag exists — never
  assume -y/--yes/--force are universally supported. Ventoy2Disk.sh's real
  flags: -i, -I, -u, -l, -r, -s, -S, -g, -L, -n.
verified: true
---

# Lesson: Ventoy2Disk.sh Has No `-y` Flag

## Context
Building an automated USB setup script that installs Ventoy non-interactively. The script used `set -euo pipefail` with an ERR trap for error handling.

## What Happened
Script crashed immediately after user confirmed installation. No error message visible. The command:
```bash
"$ventoy_script" -i -y /dev/sdX
```
Failed because `-y` is not a valid Ventoy2Disk.sh flag. Ventoy treats unrecognized flags as device paths, so `-y` was interpreted as a non-existent block device.

With `set -euo pipefail`, the error was swallowed by the ERR trap before the if/else could catch it.

## Resolution
Removed `-y` flag. Piped two `y` answers to Ventoy's two confirmation prompts:
```bash
echo -e "y\ny" | "$ventoy_script" -i /dev/sdX
```

## Prevention
- Always check `command --help` before assuming CLI flags exist
- Never assume common flags like `-y`, `--yes`, `--force` are supported
- Ventoy2Disk.sh valid flags: `-i`, `-I`, `-u`, `-l`, `-r`, `-s`, `-S`, `-g`, `-L`, `-n`

## Date: 2026-06-10
## Verified: yes

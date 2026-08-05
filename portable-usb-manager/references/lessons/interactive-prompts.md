---
title: Interactive Prompts Block Automated Scripts
category: automation
date: 2026-06-10
failure: >
  Automating disk utilities (Ventoy2Disk.sh, parted, fdisk) that have
  interactive read -p confirmation prompts caused the automating script to
  hang waiting for input, or crash on empty stdin.
root_cause: >
  Many disk utilities have no non-interactive flag and instead expect
  answers typed at a real prompt, which an automated/piped script never
  provides unless explicitly fed.
resolution: >
  Piped literal answers into tools with read -p prompts (Ventoy needs two
  "y" answers for its two separate prompts); used -y/--yes flags where a
  tool actually supports them instead of assuming one exists.
prevention: >
  Always check `command --help` for a non-interactive/yes/force/batch flag
  first; if none exists, test the exact answer sequence with
  `echo -e "y\ny" | command` before automating it.
verified: true
---

# Lesson: Interactive Prompts Block Automated Scripts

## Context
Automating disk utilities that have interactive confirmation prompts (`read -p 'Continue? (y/n)'`).

## What Happened
Script hung waiting for input, or crashed because stdin was empty. Many disk utilities have interactive prompts:
- Ventoy2Disk.sh: two `read -p 'Continue? (y/n)'` prompts
- `parted`: interactive mode
- `fdisk`: interactive mode

## Resolution
For tools with `read -p` prompts (like Ventoy), pipe answers:
```bash
echo -e "y\ny" | "$ventoy_script" -i /dev/sdX
```

For tools with `-y`/`--yes` flags:
```bash
apt-get install -y package
parted -s /dev/sdX mklabel gpt
```

For tools that read from stdin:
```bash
yes | dangerous_command [args]
```

## Prevention
- Always check `command --help 2>&1 | grep -i -E 'yes|force|non-interactive|batch|auto'`
- For Ventoy: must pipe TWO `y` answers (two separate prompts)
- Test with `echo -e "y\ny" | command` before automating

## Date: 2026-06-10
## Verified: yes

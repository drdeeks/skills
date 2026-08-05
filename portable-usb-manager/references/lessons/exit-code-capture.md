---
title: Exit Code Capture Bug in if/else
category: bash-error-handling
date: 2026-06-10
failure: >
  An error branch always reported "exit code: 1" regardless of the actual
  failure, because $? inside the else branch reflects the if condition's
  own failure, not the piped command's real exit code.
root_cause: >
  $? is overwritten by every command evaluated, including the implicit
  evaluation of the if condition itself, so reading it inside else no
  longer reflects the original piped command's exit status.
resolution: >
  Capture the exit code explicitly before the if, via
  `output=$(cmd 2>&1) || exit_code=$?`, and branch on the captured
  variable instead of a bare $? read inside if/else.
prevention: >
  Never rely on $? inside an if/else block for a command that ran as the
  if condition — always capture output and exit code together up front.
verified: true
---

# Lesson: Exit Code Capture Bug in `if/else`

## Context
Capturing exit codes from piped commands for error handling.

## What Happened
Error branch always showed "exit code: 1" regardless of actual failure:
```bash
# BROKEN — $? is always 1 (from if condition failing)
if echo -e "y\ny" | "$ventoy_script" -i "$DEVICE"; then
    echo "Success"
else
    echo "Exit code: $?"  # Always 1, not Ventoy's actual code
fi
```

## Resolution
Capture exit code before the if:
```bash
# CORRECT — capture exit code explicitly
local ventoy_exit=0
ventoy_output=$(echo -e "y\ny" | "$ventoy_script" -i "$DEVICE" 2>&1) || ventoy_exit=$?

if [[ $ventoy_exit -eq 0 ]]; then
    echo "Success"
else
    echo "Exit code: $ventoy_exit"  # This is Ventoy's actual exit code
fi
```

## Prevention
- Always use `command || exit_code=$?` pattern for exit code capture
- Never rely on `$?` inside `if/else` blocks
- Capture output and exit code together: `output=$(cmd 2>&1) || exit_code=$?`

## Date: 2026-06-10
## Verified: yes

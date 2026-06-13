# OpenClaw Migration - Migration Guide

## Default Workflow

1. Inspect first with a dry run.
2. Present a simple summary of what can be migrated, what cannot be migrated, and what would be archived.
3. If the `clarify` tool is available, use it for user decisions instead of asking for a free-form prose reply.
4. If the dry run finds imported skill directory conflicts, ask how those should be handled before executing.
5. Ask the user to choose between the two supported migration modes before executing.
6. Ask for a target workspace path only if the user wants the workspace instructions file brought over.
7. Execute the migration with the matching preset and flags.
8. Summarize the results, especially:
   - what was migrated
   - what was archived for manual review
   - what was skipped and why

## Migration Presets

### user-data
Includes: soul, workspace-agents, memory, user-profile, messaging-settings, command-allowlist, skills, tts-assets, archive

### full
Includes everything in `user-data` plus: secret-settings

# Enforcement Rules

## Permissions
- NEVER: chmod 700 or chmod 000 anywhere
- ALWAYS: chmod 755 (dirs), chmod 644 (files)
- EXCEPTION: .secrets/ encryption key may be 600

## media/ Is Sacred
- Contains files the user sent to agents
- Never archive, compress, or delete

## Forbidden Directories
- memories/ → memory/
- archives/ → .archive/
- cache/ → media/

## Runtime Artifacts to Archive
- cron/, docs/, platforms/, logs/, metrics/, reports/, state/, telemetry/, tests/, vendor/

## Required Files
- SOUL.md, USER.md, AGENTS.md, agent.json, config.yaml

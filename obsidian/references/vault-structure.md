# Obsidian Vault Structure

## Default Location
Set via `OBSIDIAN_VAULT_PATH` environment variable (e.g. in `${HERMES_DIR:-~/.hermes}/.env`).

If unset, defaults to `~/Documents/Obsidian Vault`.

Note: Vault paths may contain spaces - always quote them.

## Recommended Structure
```
vault/
├── 00-Inbox/           # Quick capture
├── 10-Projects/        # Active projects
├── 20-Areas/           # Ongoing responsibilities
├── 30-Resources/       # Reference material
├── 40-Archive/         # Completed/inactive
├── Templates/          # Note templates
└── Scripts/            # Automation scripts
```

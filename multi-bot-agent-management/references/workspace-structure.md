# Multi-Bot Agent Management - Workspace Structure

## Standardized Directory Layout

```
[agent-workspace]/
├── agent/                      # Agent identity (SOUL.md, AGENTS.md)
├── archives/                   # Archived content
├── assets/                     # Static resources
│   ├── data/                   # Data files
│   ├── documents/              # PDFs, docs
│   └── images/                 # Images
├── backups/                    # Workup backups
├── cache/                      # Cached data
├── knowledge/                  # Knowledge base
│   ├── api/                    # API documentation
│   ├── examples/               # Code examples
│   ├── guides/                 # How-to guides
│   └── research/               # Research notes
├── logs/                       # Agent logs
│   ├── errors/
│   ├── performance/
│   └── submissions/
├── memory/                     # Daily logs
├── projects/                   # Active projects
├── sessions/                   # Session transcripts
├── submissions/                # Received content
│   ├── code/                   # Programming code
│   ├── configs/                # Configuration files
│   ├── data/                   # Data files
│   ├── documents/              # Documentation
│   ├── misc/                   # Other content
│   ├── notes/                  # Notes
│   └── scripts/                # Shell scripts
├── temp/                       # Temporary files
├── tools/                      # Tools and utilities
│   ├── configs/
│   ├── scripts/
│   └── templates/
└── workflows/                  # Workflow definitions
```

## File Type Mapping

- Code (.py, .js, .ts, .html, .css) → submissions/code
- Scripts (.sh, .bash) → submissions/scripts
- Config (.json, .yaml, .yml, .env) → submissions/configs
- Documents (.md, .txt) → submissions/documents
- Data (.csv, .xml) → submissions/data
- Images (.png, .jpg) → assets/images

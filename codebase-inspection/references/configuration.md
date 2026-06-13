# Codebase Inspection Configuration

Configuration for pygount-based codebase analysis.

## Folder Exclusions

### Python Projects
```
.git,venv,.venv,__pycache__,.cache,dist,build,.tox,.eggs,.mypy_cache
```

### JavaScript/TypeScript Projects
```
.git,node_modules,dist,build,.next,.cache,.turbo,coverage
```

### General Catch-All
```
.git,node_modules,venv,.venv,__pycache__,.cache,dist,build,.next,.tox,vendor,third_party
```

## Output Formats

- `summary` - Aggregated by language (default)
- `json` - Machine-readable JSON
- Default - Per-file breakdown

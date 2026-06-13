# Codebase Inspection Reference

Quick reference for codebase analysis with pygount.

## Basic Command

```bash
pygount --format=summary \
  --folders-to-skip=".git,node_modules,venv,.venv,__pycache__,.cache,dist,build,.next" \
  .
```

## Output Columns

| Column | Description |
|--------|-------------|
| Language | Detected language |
| Files | File count |
| Code | Lines of code |
| Comment | Comment lines |
| % | Percentage of total |

## Filter by Language

```bash
pygount --suffix=py,yaml,yml --format=summary .
```

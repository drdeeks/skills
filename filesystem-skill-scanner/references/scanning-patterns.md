# Filesystem Scanning Patterns

## Directory Traversal

```python
import os

def scan_directory(path):
    for root, dirs, files in os.walk(path):
        for file in files:
            yield os.path.join(root, file)
```

## Pattern Matching

```python
from pathlib import Path

# Find all SKILL.md files
skills = list(Path('.').rglob('SKILL.md'))

# Find all Python scripts
scripts = list(Path('.').rglob('*.py'))

# Find all markdown files
docs = list(Path('.').rglob('*.md'))
```

## Filtering

| Pattern | Description |
|---------|-------------|
| `*.py` | Python files |
| `*.md` | Markdown files |
| `*.json` | JSON files |
| `**/*.test.*` | Test files |
| `*/scripts/*` | Script files |

## Performance Tips

1. Use generators for large directories
2. Filter early to reduce processing
3. Cache results for repeated scans
4. Use `os.scandir()` for better performance

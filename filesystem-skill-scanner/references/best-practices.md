# Filesystem Scanner Best Practices

## Performance Optimization

1. **Use generators** for memory efficiency
2. **Filter early** to reduce processing
3. **Cache results** for repeated scans
4. **Use os.scandir()** for better performance

## Error Handling

```python
import os
from pathlib import Path

def safe_scan(path):
    try:
        for item in Path(path).iterdir():
            try:
                yield item
            except PermissionError:
                print(f"Permission denied: {item}")
            except OSError as e:
                print(f"Error accessing {item}: {e}")
    except FileNotFoundError:
        print(f"Directory not found: {path}")
```

## Filtering Patterns

| Pattern | Use Case |
|---------|----------|
| `*.py` | Python files |
| `*.md` | Documentation |
| `**/` | Recursive search |
| `!node_modules` | Exclude directories |

## Output Formatting

```python
def format_results(results):
    for path in sorted(results):
        size = path.stat().st_size
        print(f"{path}: {size} bytes")
```

## Security Considerations

- Validate input paths
- Prevent directory traversal
- Respect file permissions
- Handle symlinks carefully

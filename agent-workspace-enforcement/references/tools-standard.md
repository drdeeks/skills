# Tools Standard

## Directory Structure
```
tools/
├── tool-name/
│   ├── README.md
│   ├── script.py
│   └── config.yaml
```

## Requirements
- Each tool must have a README.md
- Scripts must be executable (chmod 755)
- Config files must be chmod 644
- No hardcoded paths (use environment variables)

## Tool Naming
- Use lowercase with hyphens: my-tool-name
- Be descriptive: not "tool1" but "market-scanner"

## Tool Dependencies
- Document all dependencies in README.md
- Use virtual environments for Python tools
- Pin versions in requirements.txt

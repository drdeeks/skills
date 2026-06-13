# Bin Troubleshooting

Common issues with bin utilities.

## Script Not Found

Ensure you are in the skill directory:
```bash
cd /path/to/skills/bin
python3 scripts/bin_util.py
```

## Permission Denied

Make scripts executable:
```bash
chmod +x scripts/*.py
```

## Python Version

All scripts require Python 3.8+.
Check version: `python3 --version`

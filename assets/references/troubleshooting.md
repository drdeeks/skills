# Assets Troubleshooting

Common issues with asset management.

## Missing Assets

Ensure the asset file exists in the expected location:
```bash
ls -la references/
```

## Permission Issues

Check file permissions:
```bash
chmod 644 references/*.md
```

## Encoding Issues

All assets should be UTF-8 encoded:
```bash
file --mime-encoding references/*.md
```

# Codebase Inspection Troubleshooting

Common issues with codebase inspection.

## pygount Hangs or Slow

**Cause:** Crawling dependency directories
**Solution:** Always use `--folders-to-skip` to exclude `.git`, `node_modules`, `venv`

## Markdown Shows 0 Code

**Expected:** pygount classifies Markdown content as comments, not code.

## JSON Low Counts

**Expected:** pygount counts JSON lines conservatively. Use `wc -l` for accurate counts.

## Large Monorepos

Use `--suffix` to target specific languages instead of scanning everything:
```bash
pygount --suffix=py --format=summary .
```

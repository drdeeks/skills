# Jupyter Notebook Guide

## Getting Started

```bash
# Install Jupyter
pip install jupyterlab

# Start JupyterLab
jupyter lab
```

## Cell Types

| Type | Use Case |
|------|----------|
| Code | Execute Python code |
| Markdown | Documentation, explanations |
| Raw | Unformatted text |

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Shift+Enter | Run cell and move to next |
| Ctrl+Enter | Run cell in place |
| Esc+A | Insert cell above |
| Esc+B | Insert cell below |
| Esc+M | Convert to Markdown |
| Esc+Y | Convert to code |

## Magic Commands

```python
%timeit statement     # Time execution
%matplotlib inline    # Show plots inline
%load file.py         # Load file into cell
%who                  # List variables
```

## Best Practices

1. Keep notebooks modular — one topic per notebook
2. Use markdown cells for documentation
3. Restart kernel and run all before sharing
4. Clear output before committing to git

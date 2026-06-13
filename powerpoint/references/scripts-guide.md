# PowerPoint - Scripts Guide

## add_slide.py
Adds a new slide to a PowerPoint presentation.

```bash
python3 scripts/add_slide.py --presentation presentation.pptx --layout "Title and Content" --title "Slide Title" --content "Slide content"
```

**Options:**
- `--presentation` - Path to .pptx file
- `--layout` - Slide layout name (e.g., "Title and Content", "Blank", "Title Only")
- `--title` - Slide title text
- `--content` - Slide content text
- `--position` - Slide position (default: end)

## clean.py
Cleans up a PowerPoint presentation by removing unused layouts, masters, and optimizing file size.

```bash
python3 scripts/clean.py --input presentation.pptx --output presentation-clean.pptx
```

**Options:**
- `--input` - Input .pptx file
- `--output` - Output .pptx file
- `--remove-unused-layouts` - Remove unused slide layouts (default: true)
- `--remove-unused-masters` - Remove unused slide masters (default: true)

## all-office-scripts.py
Combined utility for Office document manipulation (PowerPoint, Word, Excel).

```bash
python3 scripts/all-office-scripts.py --help
```

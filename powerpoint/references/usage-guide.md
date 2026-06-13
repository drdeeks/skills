# PowerPoint - Usage Guide

## Scripts

### add_slide.py
Adds a new slide to a PowerPoint presentation.

```bash
python3 scripts/add_slide.py --presentation presentation.pptx --layout "Title and Content" --title "Slide Title" --content "Slide content"
```

### clean.py
Cleans up a PowerPoint presentation by removing unused layouts, masters, and optimizing file size.

```bash
python3 scripts/clean.py --input presentation.pptx --output presentation-clean.pptx
```

### all-office-scripts.py
Combined utility for Office document manipulation (PowerPoint, Word, Excel).

## Schemas

Office Open XML schemas are available in `references/office-schemas/` and `references/all-office-schemas.xsd`.

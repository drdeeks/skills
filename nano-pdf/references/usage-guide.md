# nano-pdf Usage Guide

## Quick Start

```bash
nano-pdf edit deck.pdf 1 "Change the title to 'Q3 Results' and fix the typo in the subtitle"
```

## Notes

- Page numbers are 0-based or 1-based depending on the tool's version/config
- If the result looks off by one, retry with the other
- Always sanity-check the output PDF before sending it out

## Common Operations

### Edit a specific page
```bash
nano-pdf edit input.pdf 1 "Add a new section about Q4 projections"
```

### Multiple edits
```bash
nano-pdf edit input.pdf 1 "Change title" --edit 2 "Add bullet points"
```

### Preview changes
```bash
nano-pdf preview input.pdf 1 "Change font to Arial"
```

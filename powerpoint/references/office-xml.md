# PowerPoint - Office Open XML Reference

## Presentation Structure

A PowerPoint (.pptx) file is a ZIP archive containing XML files:

```
presentation.pptx
├── [Content_Types].xml
├── _rels/
│   └── .rels
├── docProps/
│   ├── core.xml
│   └── app.xml
├── ppt/
│   ├── presentation.xml
│   ├── _rels/
│   │   └── presentation.xml.rels
│   ├── slideLayouts/
│   ├── slideMasters/
│   ├── slides/
│   ├── theme/
│   ├── viewProps.xml
│   └── presProps.xml
```

## Key XML Files

### presentation.xml
Root element defining slide list, slide masters, and settings.

### Slide XML (slides/slideN.xml)
Each slide contains shapes, text, and formatting.

### Slide Layouts (slideLayouts/slideLayoutN.xml)
Define placeholder arrangements for slide types.

### Slide Masters (slideMasters/slideMasterN.xml)
Master slides defining theme, background, and default formatting.

## Common Namespaces
- `p:` - PresentationML (main)
- `a:` - DrawingML (shapes, text, formatting)
- `r:` - Relationships (links, references)

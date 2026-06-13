# GIF Processing Guide

## Overview

This reference covers processing and manipulating GIF files, including conversion, editing, and optimization.

## File Formats

### GIF (Graphics Interchange Format)
- **Colors**: Max 256 colors (8-bit)
- **Transparency**: 1-bit transparency
- **Animation**: Frame-by-frame animation
- **Compression**: LZW compression

### Alternatives
- **APNG**: Better quality, larger files
- **WebM**: Modern, smaller files, better quality
- **MP4**: Universal support, good compression

## Conversion Tools

### FFmpeg
```bash
# Convert GIF to MP4
ffmpeg -i input.gif -movflags +faststart -pix_fmt yuv420p -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" output.mp4

# Convert MP4 to GIF
ffmpeg -i input.mp4 -vf "fps=10,scale=480:-1:flags=lanczos" -c:v gif output.gif

# Optimize GIF
ffmpeg -i input.gif -vf "fps=15,scale=320:-1:flags=lanczos" output.gif
```

### ImageMagick
```bash
# Resize GIF
convert input.gif -resize 300x300 output.gif

# Optimize GIF
convert input.gif -layers Optimize output.gif

# Add delay between frames
convert input.gif -delay 100 output.gif

# Remove frames
convert input.gif -delete 0-5 output.gif
```

### PIL/Pillow (Python)
```python
from PIL import Image

# Open GIF
img = Image.open("input.gif")

# Resize
img = img.resize((300, 300))

# Save optimized
img.save("output.gif", optimize=True)
```

## Optimization Techniques

### Color Reduction
```bash
# Reduce colors to 64
convert input.gif -colors 64 output.gif

# Dithering
convert input.gif -dither Riemersma output.gif
```

### Frame Optimization
```bash
# Remove duplicate frames
convert input.gif -layers RemoveDups output.gif

# Optimize layer order
convert input.gif -layers OptimizeFrame output.gif
```

### File Size Reduction
```bash
# Reduce dimensions
convert input.gif -resize 50% output.gif

# Lower frame rate
convert input.gif -delay 50 output.gif

# Strip metadata
convert input.gif -strip output.gif
```

## Animation Editing

### Extract Frames
```bash
# Extract all frames
convert input.gif frame_%03d.png

# Extract specific frame
convert input.gif[0] frame_0.png
```

### Combine Frames
```bash
# Create GIF from frames
convert frame_*.png output.gif

# Set frame delay
convert frame_*.png -delay 100 output.gif
```

### Modify Animation
```bash
# Reverse animation
convert input.gif -reverse output.gif

# Loop count
convert input.gif -loop 0 output.gif  # Infinite loop

# Remove frames
convert input.gif -delete 0-2 output.gif  # Remove first 3 frames
```

## Quality Considerations

### Frame Rate
- **10 fps**: Smooth animation
- **15 fps**: Very smooth
- **20+ fps**: Overkill for most GIFs

### Color Palette
- **32 colors**: Very small files, visible banding
- **64 colors**: Good balance
- **128 colors**: Good quality
- **256 colors**: Best quality, largest files

### Dimensions
- **200px**: Good for thumbnails
- **320px**: Good for messaging
- **480px**: Good for web
- **600px+**: High quality, large files

## Best Practices

1. **Test on target platform** - Different platforms handle GIFs differently
2. **Consider alternatives** - WebM/MP4 may be better for long animations
3. **Optimize for use case** - Messaging vs web vs social media
4. **Respect file size limits** - Most platforms have limits
5. **Provide fallbacks** - Static image for non-supporting browsers
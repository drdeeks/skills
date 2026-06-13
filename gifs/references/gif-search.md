# GIF Search Guide

## Overview

This reference covers searching for GIFs across various platforms and APIs.

## Search Platforms

### Giphy API
```bash
# Search GIFs
curl "https://api.giphy.com/v1/gifs/search?api_key=YOUR_KEY&q=cats&limit=10"

# Trending GIFs
curl "https://api.giphy.com/v1/gifs/trending?api_key=YOUR_KEY&limit=10"

# Random GIF
curl "https://api.giphy.com/v1/gifs/random?api_key=YOUR_KEY&tag=cats"
```

### Tenor API
```bash
# Search GIFs
curl "https://tenor.googleapis.com/search?q=funny&key=YOUR_KEY&limit=10"

# Trending GIFs
curl "https://tenor.googleapis.com/featured?key=YOUR_KEY&limit=10"
```

### Imgur API
```bash
# Search GIFs
curl "https://api.imgur.com/3/gallery/search?q=cats" \
  -H "Authorization: Client-ID YOUR_CLIENT_ID"
```

## Search Techniques

### Keyword Optimization
- Use specific terms: "funny cat" vs "cat"
- Add context: "celebration dance" vs "dance"
- Use synonyms: "happy" vs "joyful" vs "excited"

### Filtering
- **Rating**: G, PG, PG-13, R
- **Format**: GIF, MP4, WebM
- **Size**: Small, Medium, Large
- **Duration**: Short (<5s), Medium (5-15s), Long (>15s)

### Pagination
```bash
# Offset for pagination
curl "https://api.giphy.com/v1/gifs/search?api_key=KEY&q=cats&offset=20&limit=10"
```

## Result Processing

### Extract GIF URLs
```json
{
  "data": [
    {
      "images": {
        "original": {
          "url": "https://media.giphy.com/media/xxx/giphy.gif",
          "width": "480",
          "height": "480"
        },
        "fixed_height": {
          "url": "https://media.giphy.com/media/xxx/200.gif",
          "width": "200",
          "height": "200"
        }
      }
    }
  ]
}
```

### Quality Selection
- **Original**: Full quality, large file size
- **Fixed Height**: 200px height, good for messaging
- **Fixed Width**: 200px width, good for layouts
- **Preview**: Lower quality, faster loading

## Best Practices

1. **Cache results** - Avoid repeated API calls
2. **Handle rate limits** - Most APIs have request limits
3. **Validate URLs** - Ensure GIFs are accessible
4. **Respect licenses** - Check attribution requirements
5. **Optimize for use case** - Choose appropriate quality/size
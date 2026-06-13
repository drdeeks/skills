# YouTube Content Skill Overview

## Purpose
Extract transcripts from YouTube videos and convert them into structured content formats.

## Capabilities
- Fetch transcripts from any public YouTube video
- Support for multiple languages with fallback
- Transform into: chapters, summaries, threads, blog posts, quotes
- Handle videos with disabled transcripts gracefully

## Usage
```bash
# Fetch transcript
python3 scripts/fetch_transcript.py "https://youtube.com/watch?v=VIDEO_ID"

# Format transcript
python3 scripts/format_transcript.py "transcript.txt" --format summary
```

## Dependencies
- youtube-transcript-api (pip install youtube-transcript-api)

## Supported Formats
- Standard YouTube URLs
- Short links (youtu.be)
- Shorts
- Embeds
- Live links
- Raw 11-character video IDs

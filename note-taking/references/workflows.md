# Note Taking - Workflows

## Quick Capture
```bash
# Append to daily note
echo "- $(date '+%H:%M'): Quick thought" >> ~/notes/daily/$(date '+%Y-%m-%d').md
```

## Research Notes
```bash
# Create structured research note
cat > ~/notes/research/topic-$(date '+%Y%m%d').md << 'EOF'
---
topic: Research Topic
sources: []
tags: [research]
---

# Research: Topic

## Summary

## Key Findings

## Sources
EOF
```

## Meeting Notes
```bash
# Template for meeting notes
cat > ~/notes/meetings/meeting-$(date '+%Y%m%d-%H%M').md << 'EOF'
---
meeting: Meeting Title
attendees: []
date: 2026-01-15 10:00
tags: [meeting]
---

# Meeting: Title

## Agenda

## Discussion

## Action Items
- [ ] Item 1
- [ ] Item 2

## Decisions
EOF
```
# Validation Rules

## Structure Checks
- SKILL.md with valid YAML frontmatter
- scripts/ directory with 2+ script files
- references/ directory with 3+ reference files
- Sources section for external services

## Quality Checks
- No hardcoded paths (use ${HOME}, ${OPENCLAW_DIR})
- No TODO/FIXME markers
- No duplicate sections
- Valid markdown formatting

## Agnostic Checks
- Provider compatibility table
- Free-first strategy
- Error handling table
- Enhancement hooks

## Scoring
- Structure: 40%
- Quality: 30%
- Agnostic: 30%
- Minimum passing score: 80%

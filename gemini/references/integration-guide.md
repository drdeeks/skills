# Gemini Integration Guide

## Overview

This guide covers integrating Gemini CLI into automated workflows and scripts.

## Script Integration

### Basic Script Example
```bash
#!/bin/bash
# Simple Gemini integration script

PROMPT="Summarize the following text: $1"
RESULT=$(gemini "$PROMPT")
echo "$RESULT"
```

### Python Integration
```python
import subprocess
import json

def query_gemini(prompt, model="gemini-pro"):
    """Query Gemini CLI from Python."""
    cmd = ["gemini", "--model", model, "--output-format", json]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(result.stdout)
```

## CI/CD Integration

### GitHub Actions
```yaml
- name: Query Gemini
  run: |
    gemini --output-format json "Analyze code changes" > analysis.json
```

### GitLab CI
```yaml
gemini-analysis:
  script:
    - gemini "Review merge request"
```

## Automation Patterns

### Batch Processing
```bash
while IFS= read -r line; do
  gemini "Process: $line" >> results.txt
done < input.txt
```

### Parallel Execution
```bash
for prompt in "${prompts[@]}"; do
  gemini "$prompt" &
done
wait
```

## Error Handling

### Retry Logic
```bash
retry_gemini() {
  local prompt="$1"
  local max_attempts=3
  local attempt=1
  
  while [ $attempt -le $max_attempts ]; do
    if result=$(gemini "$prompt" 2>/dev/null); then
      echo "$result"
      return 0
    fi
    attempt=$((attempt + 1))
    sleep 2
  done
  
  return 1
}
```

## Best Practices

1. **Use structured output**: `--output-format json` for parsing
2. **Set appropriate timeouts**: Gemini may take time for complex queries
3. **Handle rate limits**: Implement backoff for repeated calls
4. **Cache results**: Store frequently used responses
5. **Validate output**: Check response format before processing
# gh-issues Workflow Guide

## Overview

This guide covers the complete workflow for using gh-issues to automatically fix GitHub issues with parallel sub-agents.

## Workflow Phases

### Phase 1: Argument Parsing
- Parse command-line arguments
- Detect repository from git remote
- Set up fork mode if specified

### Phase 2: Issue Fetching
- Authenticate with GitHub API
- Fetch issues with filters
- Filter out pull requests
- Handle pagination

### Phase 3: Presentation & Confirmation
- Display issues in markdown table
- Ask for user confirmation
- Support dry-run mode

### Phase 4: Pre-flight Checks
- Verify clean working tree
- Check remote access
- Validate GitHub token
- Check for existing PRs
- Check for in-progress branches

### Phase 5: Sub-agent Spawning
- Create feature branches
- Implement fixes
- Run tests
- Create pull requests
- Handle timeouts

### Phase 6: PR Review Handler
- Monitor open PRs
- Fetch review comments
- Analyze comment actionability
- Address review feedback
- Update PRs with fixes

## Fork Mode

### Setup
```bash
# Add fork remote
git remote add fork https://x-access-token:$GH_TOKEN@github.com/{fork_repo}.git

# Push to fork
git push fork fix/issue-{number}

# Create PR from fork to source
curl -X POST \
  -H "Authorization: Bearer $GH_TOKEN" \
  https://api.github.com/repos/{source_repo}/pulls \
  -d '{"head": "{fork_owner}:fix/issue-{number}", "base": "main"}'
```

### Benefits
- Keep source repo clean
- Isolate changes
- Easier code review

## Watch Mode

### Continuous Monitoring
```bash
# Start watch mode
/gh-issues owner/repo --watch --interval 5

# Process new issues every 5 minutes
# Address PR review comments
# Track processed issues
```

### State Management
- **PROCESSED_ISSUES** - Set of handled issue numbers
- **ADDRESSED_COMMENTS** - Set of addressed comment IDs
- **OPEN_PRS** - List of tracked pull requests

## Cron Mode

### Automated Processing
```bash
# Process one issue per run
/gh-issues owner/repo --cron

# Use with CI/CD
# - GitHub Actions
# - GitLab CI
# - Jenkins
```

### Cursor Tracking
```json
{
  "last_processed": 42,
  "in_progress": null
}
```

## Error Handling

### Common Issues

#### Authentication Failures
```bash
# Check token
echo $GH_TOKEN

# Verify token validity
curl -H "Authorization: Bearer $GH_TOKEN" \
  https://api.github.com/user
```

#### Rate Limiting
```bash
# Check rate limit
curl -H "Authorization: Bearer $GH_TOKEN" \
  https://api.github.com/rate_limit
```

#### Network Errors
```bash
# Retry with backoff
retry_curl() {
  local url="$1"
  local max_attempts=3
  local attempt=1
  
  while [ $attempt -le $max_attempts ]; do
    if result=$(curl -s "$url" 2>/dev/null); then
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

1. **Use descriptive branch names** - `fix/issue-{number}` format
2. **Write clear commit messages** - Reference issue numbers
3. **Test changes** - Run existing test suite
4. **Keep PRs focused** - One issue per PR
5. **Respond to reviews** - Address feedback promptly
6. **Monitor watch mode** - Check for new issues regularly
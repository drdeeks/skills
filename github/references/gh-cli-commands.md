# GitHub CLI (gh) Commands Reference

## Authentication

### Login
```bash
# Interactive login
gh auth login

# Login with token
gh auth login --with-token < token.txt

# Check auth status
gh auth status
```

### Token Management
```bash
# Create token
gh auth token

# Refresh token
gh auth refresh
```

## Repository Operations

### Clone
```bash
# Clone repository
gh repo clone owner/repo

# Clone with specific branch
gh repo clone owner/repo --branch branch-name
```

### Create
```bash
# Create new repository
gh repo create repo-name

# Create from template
gh repo create --template owner/template-repo repo-name

# Create with description
gh repo create repo-name --description "Repository description"
```

### List
```bash
# List your repositories
gh repo list

# List user's repositories
gh repo list username

# List with limit
gh repo list --limit 10
```

## Pull Requests

### Create
```bash
# Create pull request
gh pr create --title "PR title" --body "PR description"

# Create from current branch
gh pr create

# Create with reviewers
gh pr create --reviewer user1,user2
```

### List
```bash
# List open PRs
gh pr list

# List closed PRs
gh pr list --state closed

# List with specific branch
gh pr list --head branch-name
```

### Review
```bash
# View PR
gh pr view 123

# Checkout PR
gh pr checkout 123

# Merge PR
gh pr merge 123

# Approve PR
gh pr review 123 --approve

# Request changes
gh pr review 123 --request-changes --body "Please fix..."
```

## Issues

### Create
```bash
# Create issue
gh issue create --title "Issue title" --body "Issue description"

# Create with labels
gh issue create --label bug,enhancement
```

### List
```bash
# List open issues
gh issue list

# List closed issues
gh issue list --state closed

# List with label
gh issue list --label bug
```

### Manage
```bash
# View issue
gh issue view 123

# Close issue
gh issue close 123

# Reopen issue
gh issue reopen 123

# Add comment
gh issue comment 123 --body "Comment text"
```

## CI/CD

### Actions
```bash
# List workflows
gh workflow list

# View workflow run
gh run view 123

# List runs
gh run list

# Watch run
gh run watch 123
```

### Variables
```bash
# List variables
gh variable list

# Set variable
gh variable set VARIABLE_NAME --body "value"

# Delete variable
gh variable delete VARIABLE_NAME
```

## Gists

### Create
```bash
# Create gist
gh gist create file.txt

# Create with description
gh gist create file.txt --desc "Gist description"

# Create public gist
gh gist create file.txt --public
```

### List
```bash
# List your gists
gh gist list

# List public gists
gh gist list --public
```

## Best Practices

1. **Use aliases** - Create shortcuts for common commands
2. **Set defaults** - Configure default values for options
3. **Use JSON output** - Parse with `jq` for scripting
4. **Handle errors** - Check exit codes and error messages
5. **Respect rate limits** - Monitor API usage
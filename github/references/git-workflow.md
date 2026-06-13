# Git Workflow Guide

## Overview

This reference covers Git workflows and best practices for GitHub collaboration.

## Branching Strategies

### GitHub Flow
```
main (production)
  └── feature-branch (development)
        └── pull request → merge → deploy
```

**Steps:**
1. Create feature branch from main
2. Make changes and commit
3. Push to remote
4. Create pull request
5. Review and merge
6. Deploy

### Git Flow
```
main (production)
  ├── develop (integration)
  │     ├── feature-1
  │     └── feature-2
  └── release
```

**Branches:**
- `main` - Production code
- `develop` - Integration branch
- `feature/*` - New features
- `release/*` - Release preparation
- `hotfix/*` - Emergency fixes

### Trunk-Based Development
```
main (trunk)
  ├── feature-flag-1
  └── feature-flag-2
```

**Practices:**
- Short-lived branches (< 1 day)
- Feature flags for incomplete work
- Continuous integration

## Commit Messages

### Conventional Commits
```
type(scope): description

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

**Examples:**
```
feat(auth): add OAuth2 login support

fix(api): handle null response from server

docs(readme): update installation instructions

refactor(utils): simplify date formatting
```

### Commit Best Practices
1. **Atomic commits** - One logical change per commit
2. **Descriptive messages** - Explain what and why
3. **Reference issues** - Link to issue tracker
4. **Test before commit** - Ensure code works

## Pull Request Workflow

### Creating PRs
```bash
# Create branch
git checkout -b feature/new-feature

# Make changes
git add .
git commit -m "feat: add new feature"

# Push
git push origin feature/new-feature

# Create PR
gh pr create --title "Add new feature" --body "Description"
```

### PR Description Template
```markdown
## Summary
Brief description of changes

## Changes
- Change 1
- Change 2

## Testing
How to test these changes

## Related Issues
Fixes #123
```

### Review Process
1. **Self-review** - Check your own changes
2. **Automated checks** - CI/CD must pass
3. **Code review** - At least one approval
4. **Address feedback** - Make requested changes
5. **Merge** - Squash, merge, or rebase

## Merge Strategies

### Squash Merge
```bash
# Combine all commits into one
gh pr merge --squash
```

**When to use:**
- Feature has many small commits
- Want clean history
- Single logical change

### Merge Commit
```bash
# Keep all commits
gh pr merge --merge
```

**When to use:**
- Want to preserve commit history
- Multiple logical changes
- Large features

### Rebase
```bash
# Rebase onto main
git rebase main
git push --force-with-lease
```

**When to use:**
- Want linear history
- Clean up commit history
- Before merging

## Conflict Resolution

### Identify Conflicts
```bash
# Check for conflicts
git status

# View conflict markers
grep -rn "<<<<<<" .
```

### Resolve Conflicts
1. **Edit files** - Remove conflict markers
2. **Test changes** - Ensure code works
3. **Stage resolved files**
   ```bash
   git add <resolved-files>
   ```
4. **Continue rebase/merge**
   ```bash
   git rebase --continue
   # or
   git merge --continue
   ```

### Prevent Conflicts
1. **Pull frequently** - Stay up to date
2. **Small PRs** - Reduce conflict surface
3. **Communicate** - Coordinate with team
4. **Feature flags** - Isolate changes

## Best Practices

1. **Keep branches short-lived** - Merge within a day
2. **Use meaningful names** - `feature/user-auth` not `fix-1`
3. **Write good commit messages** - Explain context
4. **Review thoroughly** - Catch issues early
5. **Test before merging** - Ensure quality
6. **Document changes** - Update README/changelog
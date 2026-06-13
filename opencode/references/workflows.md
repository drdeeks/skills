# OpenCode Workflows

## Procedure

1. Verify tool readiness:
   - `opencode --version`
   - `opencode auth list`

2. For bounded tasks, use `opencode run '...'` (no pty needed).

3. For iterative tasks, start `opencode` with `background=true, pty=true`.

4. Monitor long tasks with `process(action="poll"|"log")`.

5. If OpenCode asks for input, respond via `process(action="submit", ...)`.

6. Exit with `process(action="write", data="\x03")` or `process(action="kill")`.

7. Summarize file changes, test results, and next steps back to user.

## PR Review Workflow

```bash
# Direct review
opencode pr 42

# Isolated review in temp clone
REVIEW=$(mktemp -d) && git clone https://github.com/user/repo.git $REVIEW && cd $REVIEW && opencode run 'Review this PR vs main. Report bugs, security risks, test gaps, and style issues.' -f $(git diff origin/main --name-only | head -20 | tr '\n' ' ')
```

## Parallel Work Pattern

```bash
# Separate workdirs to avoid collisions
opencode run 'Fix issue #101 and commit' --workdir /tmp/issue-101
opencode run 'Add parser regression tests and commit' --workdir /tmp/issue-102
```

## Verification

### Smoke Test
```bash
opencode run 'Respond with exactly: OPENCODE_SMOKE_OK'
```

Success criteria:
- Output includes `OPENCODE_SMOKE_OK`
- Command exits without provider/model errors
- For code tasks: expected files changed and tests pass

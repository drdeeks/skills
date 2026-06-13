# Plan Writing Best Practices

## Task Granularity
- Each task: 2-5 minutes of work
- One logical action per task
- If task takes > 10 min, split it

## File Paths
- Always use exact paths: `src/auth/login.py`
- Include line numbers for modifications: `src/config.py:45-50`
- Specify test files: `tests/auth/test_login.py`

## Code Examples
- Complete, copy-pasteable code
- Include imports
- Handle edge cases
- No `...` or `pass` placeholders

## Commands
- Exact command to run
- Expected output (PASS/FAIL/error message)
- Include flags and arguments

## Verification
- Every task needs verification step
- Test command with expected result
- Manual verification if no test

## Principles
- **DRY**: Extract common patterns
- **YAGNI**: No speculative features
- **TDD**: Test first, then implement
- **Commit often**: After each task

## Review Checklist
- [ ] Tasks sequential and logical
- [ ] Each task bite-sized
- [ ] File paths exact
- [ ] Code complete
- [ ] Commands exact
- [ ] Verification included
- [ ] No missing context

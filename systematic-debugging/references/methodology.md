# Systematic Debugging Methodology

## Phase 1: Reproduce
1. Create minimal reproduction case
2. Document exact steps
3. Verify consistency

## Phase 2: Isolate
1. Binary search the codebase
2. Disable half the system
3. Narrow to specific module

## Phase 3: Diagnose
1. Add logging/breakpoints
2. Trace execution flow
3. Check assumptions

## Phase 4: Fix
1. Implement minimal fix
2. Verify reproduction case passes
3. Run full test suite

## Phase 5: Prevent
1. Add regression test
2. Document root cause
3. Improve monitoring

---
description: Automatically fix all linting errors, warnings, and test failures without requiring permissions
argument-hint: (none - runs automatically)
---

# Fix Command

## Purpose
**HANDS-OFF COMMAND**: Automatically fix all linting errors, warnings, and test failures in the codebase without requiring user permissions for the duration of the command. This command will persistently work until all errors AND warnings are resolved, alternating between linting and testing to ensure both pass consistently with zero issues.

## Command Overview
The `/fix` command is a fully autonomous error and warning fixing workflow that:
1. Runs `make lint-fix` to auto-fix formatting issues
2. Iteratively runs `make lint-all` and fixes ALL linting errors AND warnings
3. Runs `make test-all` and fixes any test failures
4. Alternates between linting and testing until both pass with ZERO errors, warnings, or failures
5. Never gives up early, bypasses issues, or skips tests

**CRITICAL**: This is a hands-off command. Once started, it will run to completion without asking for permissions.

## Workflow Steps

### 1. Initial Setup and Validation
```bash
# Verify we're in a valid git repository
git status > /dev/null 2>&1 || exit 1

# Check current branch (warn if on main but continue)
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" = "main" ] || [ "$CURRENT_BRANCH" = "develop" ]; then
    echo "⚠️ WARNING: Running on $CURRENT_BRANCH branch"
fi

# Store initial state for tracking changes
git diff --stat > /tmp/fix_initial_state.txt
```

### 2. Auto-Fix Phase
Run auto-fixable formatting and linting corrections:

```bash
# First attempt auto-fix with make lint-fix
make lint-fix

# Check if changes were made
git diff --stat
```

### 3. Iterative Linting Fix Loop
Continuously run linting and fix errors until clean:

```bash
LINT_ATTEMPTS=0
MAX_LINT_ATTEMPTS=50  # Prevent infinite loops while being persistent

while [ $LINT_ATTEMPTS -lt $MAX_LINT_ATTEMPTS ]; do
    LINT_ATTEMPTS=$((LINT_ATTEMPTS + 1))
    echo "🔍 Linting attempt $LINT_ATTEMPTS"

    # Run lint-all and capture output
    make lint-all 2>&1 | tee /tmp/lint_output.txt

    # Check if linting passed
    if [ $? -eq 0 ]; then
        echo "✅ All linting checks passed!"
        break
    fi

    # Parse lint errors and fix them programmatically
    # This will involve:
    # - Reading the lint output
    # - Identifying specific error types
    # - Applying appropriate fixes
    # - Using Edit/MultiEdit tools to fix issues

    # Continue to next iteration
done
```

### 4. Iterative Test Fix Loop
Continuously run tests and fix failures until all pass:

```bash
TEST_ATTEMPTS=0
MAX_TEST_ATTEMPTS=50  # Prevent infinite loops while being persistent

while [ $TEST_ATTEMPTS -lt $MAX_TEST_ATTEMPTS ]; do
    TEST_ATTEMPTS=$((TEST_ATTEMPTS + 1))
    echo "🧪 Test attempt $TEST_ATTEMPTS"

    # Run test-all and capture output
    make test-all 2>&1 | tee /tmp/test_output.txt

    # Check if tests passed
    if [ $? -eq 0 ]; then
        echo "✅ All tests passed!"
        break
    fi

    # Parse test failures and fix them
    # This will involve:
    # - Reading test output
    # - Identifying failing tests
    # - Analyzing failure reasons
    # - Fixing implementation or test issues
    # - Using Edit/MultiEdit tools to apply fixes

    # Continue to next iteration
done
```

### 5. Alternating Verification Loop
Ensure both linting and tests pass consistently:

```bash
STABLE_PASSES=0
REQUIRED_STABLE_PASSES=2  # Both must pass twice in a row
VERIFICATION_ATTEMPTS=0
MAX_VERIFICATION_ATTEMPTS=20

while [ $STABLE_PASSES -lt $REQUIRED_STABLE_PASSES ] && [ $VERIFICATION_ATTEMPTS -lt $MAX_VERIFICATION_ATTEMPTS ]; do
    VERIFICATION_ATTEMPTS=$((VERIFICATION_ATTEMPTS + 1))
    echo "🔄 Verification attempt $VERIFICATION_ATTEMPTS"

    # Run linting
    make lint-all
    LINT_STATUS=$?

    # Run tests
    make test-all
    TEST_STATUS=$?

    # Check if both passed
    if [ $LINT_STATUS -eq 0 ] && [ $TEST_STATUS -eq 0 ]; then
        STABLE_PASSES=$((STABLE_PASSES + 1))
        echo "✅ Both linting and tests passed ($STABLE_PASSES/$REQUIRED_STABLE_PASSES)"
    else
        STABLE_PASSES=0  # Reset counter if either failed
        echo "❌ Verification failed, fixing issues..."

        # Fix whichever failed
        if [ $LINT_STATUS -ne 0 ]; then
            # Return to linting fix loop
            # Apply fixes for linting issues
        fi

        if [ $TEST_STATUS -ne 0 ]; then
            # Return to test fix loop
            # Apply fixes for test failures
        fi
    fi
done
```

### 6. Final Validation
Confirm everything is working:

```bash
echo "🏁 Running final validation..."

# Final lint check
make lint-all
FINAL_LINT=$?

# Final test check
make test-all
FINAL_TEST=$?

if [ $FINAL_LINT -eq 0 ] && [ $FINAL_TEST -eq 0 ]; then
    echo "🎉 SUCCESS: All linting and tests are passing!"
else
    echo "⚠️ WARNING: Some issues remain after maximum attempts"
fi
```

## Error Fix Strategies

### Linting Error Fixes

#### Python (Flake8, Black, isort, mypy)
- **Import sorting**: Use isort patterns
- **Formatting**: Apply Black formatting
- **Type hints**: Add missing type annotations
- **Unused imports**: Remove them
- **Line length**: Break long lines appropriately
- **Complexity**: Refactor complex functions

#### JavaScript/TypeScript (ESLint, Prettier)
- **Missing semicolons**: Add them
- **Unused variables**: Remove or use them
- **Formatting**: Apply Prettier rules
- **Type errors**: Fix TypeScript types
- **Import ordering**: Reorganize imports

#### SOLID Principles
- **Single Responsibility**: Split large classes/functions
- **Open/Closed**: Use inheritance properly
- **Liskov Substitution**: Fix inheritance violations
- **Interface Segregation**: Split large interfaces
- **Dependency Inversion**: Use abstractions

### Test Failure Fixes

#### Assertion Failures
- Analyze expected vs actual values
- Update test expectations if implementation is correct
- Fix implementation if test expectations are correct

#### Import/Module Errors
- Fix import paths
- Add missing dependencies
- Update module structure

#### Fixture/Setup Issues
- Fix test fixtures
- Update mock configurations
- Correct database setup

#### Coverage Failures
- Add tests for uncovered code
- Remove dead code
- Improve test comprehensiveness

## Implementation Details

### Fix Application Method
The command will use these tools in order of preference:
1. **make lint-fix**: For auto-fixable issues
2. **MultiEdit**: For multiple changes to the same file
3. **Edit**: For single file changes
4. **Write**: For creating missing files

### Error Parsing
Parse error outputs to identify:
- File path
- Line number
- Error type
- Suggested fix (if provided)

### Fix Verification
After each fix:
1. Re-run the specific check
2. Confirm the error is resolved
3. Check for new errors introduced

## Progress Tracking

The command will provide real-time updates:

```
🚀 Starting /fix command - Hands-off mode activated
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Progress Summary:
  Linting:  [████████░░] 80% (40/50 errors fixed)
  Tests:    [██████░░░░] 60% (15/25 failures fixed)
  Status:   🔄 Working on test failures...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔧 Current Action: Fixing TypeError in test_auth.py:45
   Issue: Missing mock for database connection
   Fix: Adding proper mock fixture

📝 Recent Fixes:
  ✅ Fixed import ordering in app/main.py
  ✅ Removed unused variable in utils/helpers.py
  ✅ Added type hints to services/auth.py
  ✅ Fixed assertion in test_user.py

⏱️ Elapsed Time: 4m 32s
💪 Persistence Level: Maximum - Will not give up!
```

## Success Criteria

The command succeeds when:
1. ✅ `make lint-all` passes with zero errors
2. ✅ `make test-all` passes with zero failures
3. ✅ Both commands pass consecutively at least twice
4. ✅ No new errors are introduced during fixing

## Failure Handling

The command will NEVER:
- ❌ Give up early on fixable errors
- ❌ Skip or bypass failing tests
- ❌ Ignore linting violations
- ❌ Comment out problematic code
- ❌ Use `# noqa`, `// eslint-disable`, or similar bypasses
- ❌ Mark tests as skipped or expected failures

The command WILL:
- ✅ Fix the root cause of issues
- ✅ Maintain code functionality
- ✅ Preserve test integrity
- ✅ Apply proper solutions
- ✅ Keep trying until successful

## Command Execution Example

```bash
User: /fix

Assistant Response:
🚀 Starting /fix command - Hands-off mode activated
⚠️ This command will run autonomously without asking for permissions
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 Phase 1: Initial Assessment
Running initial checks to understand the current state...

$ make lint-all
❌ Found 23 linting errors
❌ Found 5 type checking errors
❌ Found 3 SOLID principle violations

$ make test-all
❌ 8 test failures detected
❌ Coverage below threshold (72% < 80%)

📊 Total Issues to Fix: 39
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔧 Phase 2: Auto-Fix Attempt
Running make lint-fix to handle auto-fixable issues...

$ make lint-fix
✅ Fixed 12 formatting issues automatically
✅ Sorted imports in 8 files
✅ Applied Black formatting to all Python files

Remaining issues: 27
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 Phase 3: Iterative Linting Fixes
Fixing remaining linting errors...

[Attempt 1/50]
📝 Fixing: app/services/auth.py:45 - Missing type hint
✅ Added type hint: def authenticate(username: str, password: str) -> Optional[User]

📝 Fixing: app/utils/validators.py:23 - Unused import
✅ Removed unused import: from typing import Dict

[Attempt 2/50]
📝 Fixing: app/models/user.py:67 - Class too complex (complexity: 12)
✅ Refactored into smaller methods

[... continues fixing each error ...]

✅ All linting errors fixed after 4 iterations!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🧪 Phase 4: Iterative Test Fixes
Fixing test failures...

[Attempt 1/50]
📝 Fixing: tests/test_auth.py::test_login - AssertionError
   Expected: {"status": "success"}
   Actual: {"status": "error", "message": "Invalid credentials"}
✅ Fixed mock user data in test fixture

📝 Fixing: tests/test_user.py::test_create - Database connection error
✅ Added proper database mock for test isolation

[Attempt 2/50]
📝 Fixing: tests/test_api.py::test_endpoint - 404 Not Found
✅ Updated test URL to match new route

[... continues fixing each test ...]

✅ All tests passing after 3 iterations!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔄 Phase 5: Alternating Verification
Ensuring both linting and tests pass consistently...

[Verification 1/2]
$ make lint-all
✅ Linting passed!

$ make test-all
❌ New test failure introduced by linting fixes
📝 Fixing: Import order change broke mock patch
✅ Updated mock patch path

[Verification 2/2]
$ make lint-all
✅ Linting passed!

$ make test-all
✅ All tests passed!

✅ Both checks passed consecutively!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏁 Phase 6: Final Validation
Running final checks...

$ make lint-all
✅ All linting checks passed
  - Python: ✅ Flake8, Black, isort, mypy
  - JavaScript: ✅ ESLint, Prettier
  - SOLID: ✅ All principles satisfied

$ make test-all
✅ All tests passed
  - Unit tests: 156/156 passed
  - Integration tests: 23/23 passed
  - Coverage: 85% (exceeds 80% requirement)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎉 SUCCESS: All issues fixed!

📊 Final Summary:
  ✅ Fixed 23 linting errors
  ✅ Fixed 8 test failures
  ✅ Fixed 5 type checking errors
  ✅ Fixed 3 SOLID violations
  ✅ Improved coverage from 72% to 85%

⏱️ Total Time: 7m 23s
📝 Files Modified: 18
🔧 Total Fixes Applied: 39

The codebase is now fully compliant with all quality standards!
```

## Integration Points

### With /done Command
The `/fix` command can be used before `/done` to ensure clean PR:
```bash
/fix        # Fix all issues
/done       # Create PR with confidence
```

### With /solid Command
The `/fix` command handles SOLID principle violations detected by `/solid`:
```bash
/solid      # Analyze SOLID compliance
/fix        # Fix any violations found
```

### With CI/CD Pipeline
The `/fix` command prevents CI/CD failures by fixing issues locally:
- Pre-commit: Run `/fix` before committing
- Pre-push: Run `/fix` before pushing
- Pre-PR: Run `/fix` before creating pull request

## Configuration

The command respects project configuration:
- Uses make targets exclusively (never direct tool calls)
- Follows `.ai/docs/STANDARDS.md` for fixes
- Respects `.flake8`, `.eslintrc`, etc. configurations
- Applies project-specific fix strategies

## Notes

- **Hands-Off Operation**: Once started, runs to completion without user interaction
- **Persistent**: Will not give up on fixable errors
- **Comprehensive**: Fixes root causes, not symptoms
- **Safe**: Creates proper fixes without breaking functionality
- **Thorough**: Alternates between checks to ensure stability
- **Transparent**: Provides clear progress updates throughout

This command embodies the principle of "make it work, make it right" by ensuring all quality checks pass through persistent, automated fixing.

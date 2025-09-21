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

### 3. Parallel Fix Phase
Launch two specialized agents in parallel to fix lint and test issues simultaneously:

**CRITICAL**: Both agents run concurrently using the Task tool with parallel execution.

```
🚀 Launching parallel fix agents:
  - Lint Fix Agent: Iteratively fixes all linting errors and warnings
  - Test Fix Agent: Iteratively fixes all test failures
```

#### Lint Fix Agent Task
The lint fix agent will:
1. Run `make lint-all` to identify issues
2. Parse and categorize errors by type and file
3. Apply fixes using MultiEdit for batch changes
4. Re-run linting after each batch of fixes
5. Continue until all linting passes with zero errors/warnings
6. Maximum 50 iterations to prevent infinite loops

#### Test Fix Agent Task
The test fix agent will:
1. Run `make test-all` to identify failures
2. Analyze failure patterns and root causes
3. Fix test implementation or source code issues
4. Re-run tests after each batch of fixes
5. Continue until all tests pass
6. Maximum 50 iterations to prevent infinite loops

Both agents work independently and report their progress. The parallel execution significantly reduces total fix time.

### 4. Sequential Cleanup Phase
After both parallel agents complete, perform final sequential cleanup:

This phase ensures that fixes from one agent didn't break the other's domain and that everything works together:

```bash
echo "🔄 Starting sequential cleanup phase..."

# Step 1: Verify both lint and tests pass after parallel fixes
make lint-all
LINT_STATUS=$?

make test-all
TEST_STATUS=$?

if [ $LINT_STATUS -eq 0 ] && [ $TEST_STATUS -eq 0 ]; then
    echo "✅ Both linting and tests passed after parallel fixes!"
else
    echo "⚠️ Conflicts detected between parallel fixes, resolving sequentially..."

    # Step 2: Fix any conflicts sequentially
    # This uses a simpler approach since most issues are already fixed

    if [ $LINT_STATUS -ne 0 ]; then
        echo "🔧 Fixing remaining lint issues..."
        # Run targeted lint fixes for any remaining issues
        # Maximum 5 iterations since most work is done
    fi

    if [ $TEST_STATUS -ne 0 ]; then
        echo "🔧 Fixing remaining test issues..."
        # Run targeted test fixes for any remaining failures
        # Maximum 5 iterations since most work is done
    fi
fi

# Step 3: Final stability check - ensure both pass twice consecutively
STABLE_PASSES=0
REQUIRED_STABLE_PASSES=2

for i in 1 2; do
    echo "🔍 Stability check $i/$REQUIRED_STABLE_PASSES"

    make lint-all
    LINT_STATUS=$?

    make test-all
    TEST_STATUS=$?

    if [ $LINT_STATUS -eq 0 ] && [ $TEST_STATUS -eq 0 ]; then
        STABLE_PASSES=$((STABLE_PASSES + 1))
        echo "✅ Stability check passed ($STABLE_PASSES/$REQUIRED_STABLE_PASSES)"
    else
        echo "❌ Stability check failed, applying final fixes..."
        # Apply minimal targeted fixes
        break
    fi
done
```

### 5. Final Validation
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

🚀 Phase 3: Parallel Fix Phase
Launching two specialized agents in parallel to fix remaining issues...

🤖 LINT FIX AGENT                    🤖 TEST FIX AGENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Starting lint fix iterations...      Starting test fix iterations...

[Iteration 1/50]                     [Iteration 1/50]
Running make lint-all...            Running make test-all...
Found 11 errors to fix               Found 8 failures to fix

📝 Fixing type hints in:            📝 Fixing test failures in:
  - app/services/auth.py:45          - tests/test_auth.py::test_login
  - app/models/user.py:23            - tests/test_user.py::test_create
  - app/utils/validators.py:12       - tests/test_api.py::test_endpoint

[Iteration 2/50]                     [Iteration 2/50]
Running make lint-all...            Running make test-all...
Found 5 errors remaining             Found 3 failures remaining

📝 Fixing complexity issues:         📝 Fixing mock issues:
  - Refactoring user.py methods      - Database mock in test_user.py
  - Splitting auth.py functions      - API mock in test_integration.py

[Iteration 3/50]                     [Iteration 3/50]
Running make lint-all...            Running make test-all...
✅ All linting passed!               Found 1 failure remaining

Agent complete in 2m 34s             📝 Fixing assertion:
                                       - Updated expected response

                                     [Iteration 4/50]
                                     Running make test-all...
                                     ✅ All tests passed!

                                     Agent complete in 3m 12s

⏱️ Parallel execution completed in 3m 12s (vs ~5m 46s sequential)
✅ Both agents reported success!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔄 Phase 4: Sequential Cleanup
Verifying parallel fixes work together...

$ make lint-all
✅ Linting passed!

$ make test-all
❌ 1 test failure detected (conflict from parallel fixes)

🔧 Resolving conflict...
📝 Import order changed by lint agent broke test mock path
✅ Updated mock path to match new import structure

🔍 Stability check 1/2
$ make lint-all && make test-all
✅ Both passed!

🔍 Stability check 2/2
$ make lint-all && make test-all
✅ Both passed!

✅ Sequential cleanup complete!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏁 Phase 5: Final Validation
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

⏱️ Total Time: 4m 28s (40% faster with parallel execution)
  - Parallel fix phase: 3m 12s
  - Sequential cleanup: 1m 16s
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
- **Parallel Execution**: Runs lint and test fixing agents concurrently for ~40% time savings
- **Persistent**: Will not give up on fixable errors
- **Comprehensive**: Fixes root causes, not symptoms
- **Safe**: Creates proper fixes without breaking functionality
- **Conflict Resolution**: Sequential cleanup phase handles any conflicts from parallel fixes
- **Thorough**: Final stability checks ensure everything works together
- **Transparent**: Provides clear progress updates throughout

This command embodies the principle of "make it work, make it right" by ensuring all quality checks pass through persistent, automated fixing with optimized parallel execution.

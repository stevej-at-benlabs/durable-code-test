# Done Command

## Purpose
Complete the development workflow by committing all changes, running comprehensive quality checks, creating a pull request, and ensuring all CI/CD checks pass.

## Command Overview
The `/done` command automates the entire completion workflow for a feature branch, ensuring code quality and proper CI/CD integration before marking work as complete.

### Command Variations
- `/done` - Creates PR and waits for manual merge after all checks pass
- `/done with merge` - Automatically merges PR after all checks pass (requires approval settings)

## Workflow Steps

### 1. Pre-Commit Validation
Before committing any code, validate current state:

```bash
# Check working directory status
git status

# Ensure we're on a feature branch (not main/develop)
git branch --show-current

# Check for uncommitted changes
git diff --stat
```

### 2. Code Quality Checks
Run comprehensive quality assurance before committing using established make targets:

**CRITICAL: Always use project make targets. Do not deviate to individual tool calls.**

```bash
# Primary quality check - runs all linting, formatting, and design checks
make lint-all

# Alternative individual targets if lint-all not available:
make lint          # Standard linting
make format-check  # Code formatting validation
make design-lint   # Custom design linters (SOLID principles, etc.)
make security      # Security scanning
```

**Never run individual npm/docker commands directly. Always use make targets.**

### 3. Comprehensive Testing
Run all test suites with coverage requirements using make targets:

**CRITICAL: Always use project make targets for testing. Do not run individual commands.**

```bash
# Primary test command - runs all tests with coverage
make test

# Alternative individual targets if needed:
make test-frontend    # Frontend tests only
make test-backend     # Backend tests only
make test-integration # Integration tests only
make test-coverage    # Coverage reports
```

**Never run individual npm/pytest/docker commands directly. Always use make targets.**

#### Coverage Validation
- Backend: Minimum 80% coverage required
- Frontend: Minimum 70% coverage required
- Critical paths: 95% coverage required

### 4. Build Verification
Ensure production builds work correctly:

```bash
# Backend build verification
docker exec durable-code-backend-dev python -m py_compile $(find /app/app -name "*.py")

# Frontend production build
cd durable-code-app/frontend && npm run build

# Docker image builds (if applicable)
docker-compose build --no-cache
```

### 5. Commit Changes
Create meaningful commit with proper formatting:

#### Commit Message Format
```
<type>(<scope>): <subject>

<body>

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
```

#### Commit Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to build process or auxiliary tools

#### Commit Process
```bash
# Stage all changes
git add .

# Create commit with proper message
git commit -m "$(cat <<'EOF'
feat(api): Add user authentication endpoints

- Implement JWT-based authentication
- Add password hashing with bcrypt
- Create user registration and login endpoints
- Add comprehensive input validation
- Include rate limiting for auth endpoints
- Add unit and integration tests with 95% coverage

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

### 6. Push and Create Pull Request
Push changes and create PR with comprehensive details:

#### Push to Remote
```bash
# Push to remote branch
git push -u origin $(git branch --show-current)
```

#### Create Pull Request
```bash
# Create PR using GitHub CLI
gh pr create --title "feat: Add user authentication system" --body "$(cat <<'EOF'
## Summary
- Implement comprehensive user authentication system
- Add JWT token management
- Include password security best practices

## Changes Made
- 🔐 JWT-based authentication endpoints
- 🔒 Password hashing with bcrypt
- ✅ Input validation with Pydantic
- 🛡️ Rate limiting for security
- 🧪 Comprehensive test coverage (95%)

## Test Plan
- [x] Unit tests for all auth functions
- [x] Integration tests for auth flow
- [x] Security tests for edge cases
- [x] Performance tests for token generation
- [x] Manual testing of complete auth flow

## Quality Assurance
- [x] All linters pass
- [x] Type checking passes
- [x] SOLID principles compliance verified
- [x] Security scan clean
- [x] Test coverage exceeds requirements (95%)
- [x] Documentation updated

## Breaking Changes
None - this is additive functionality

## Deployment Notes
- Requires environment variables for JWT secret
- Database migration needed for user table
- Update API documentation

🤖 Generated with Claude Code
EOF
)"
```

### 7. CI/CD Verification
Monitor and ensure all automated checks pass:

#### GitHub Actions Monitoring
```bash
# Watch CI/CD pipeline status
gh pr checks $(gh pr view --json number -q .number)

# View detailed check results
gh run list --branch $(git branch --show-current)

# Monitor specific check
gh run watch $(gh run list --branch $(git branch --show-current) --json databaseId -q .[0].databaseId)
```

#### Required Checks
- ✅ Build passes
- ✅ All tests pass
- ✅ Linting passes
- ✅ Type checking passes
- ✅ Security scan passes
- ✅ SOLID principles check passes
- ✅ Coverage requirements met
- ✅ Performance benchmarks met

### 8. Auto-Merge Decision (if 'with merge' specified)
If the `with merge` argument was provided, proceed with automatic merge:

#### Pre-Merge Validation
```bash
# Verify all required checks are passing
gh pr checks $(gh pr view --json number -q .number) --required

# Check if PR is ready for merge
gh pr view --json mergeable,mergeStateStatus -q '.mergeable,.mergeStateStatus'

# Verify no merge conflicts
git fetch origin
git merge-base --is-ancestor HEAD origin/main || echo "Merge conflicts detected"
```

#### Branch Protection Compliance
```bash
# Check branch protection rules
gh api repos/:owner/:repo/branches/main/protection

# Verify required reviews (if configured)
gh pr view --json reviewDecision -q .reviewDecision

# Check required status checks
gh pr checks --required
```

#### Auto-Merge Execution
```bash
# Enable auto-merge if all conditions met
gh pr merge $(gh pr view --json number -q .number) \
  --auto \
  --squash \
  --delete-branch \
  --body "$(cat <<'EOF'
✅ Automated merge after successful CI/CD pipeline

All quality checks passed:
- Build: ✅ Passed
- Tests: ✅ Passed
- Linting: ✅ Passed
- Security: ✅ Passed
- SOLID Compliance: ✅ Passed

🤖 Merged automatically via /done with merge command
Generated with Claude Code
EOF
)"
```

#### Post-Merge Cleanup
```bash
# Switch back to main branch
git checkout main

# Pull latest changes
git pull origin main

# Clean up local feature branch
git branch -d feature/branch-name

# Update local repository
git fetch --prune
```

### 9. Handle Check Failures
If any checks fail, address them systematically:

#### Failed Build
```bash
# Check build logs
gh run view $(gh run list --branch $(git branch --show-current) --json databaseId -q .[0].databaseId) --log-failed

# Fix build issues locally
make build

# Test fixes
make test

# Commit fixes
git add . && git commit -m "fix: Resolve build issues

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"

# Push fixes
git push
```

#### Failed Tests
```bash
# Run failing tests locally
make test-quick

# Debug specific failures
pytest path/to/failing/test.py -v -s

# Fix test issues
# ... make necessary changes ...

# Verify fixes
make test

# Commit fixes
git add . && git commit -m "fix: Resolve test failures

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"
```

#### Failed Linting
```bash
# Check specific linting errors
make lint

# Auto-fix formatting issues
make format

# Fix remaining issues manually
# ... address linting violations ...

# Verify fixes
make lint

# Commit fixes
git add . && git commit -m "style: Fix linting violations

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"
```

## Error Handling

### Insufficient Test Coverage
```bash
# Generate detailed coverage report
make test-coverage

# Identify uncovered lines
# Add tests for uncovered code
# Re-run coverage check
```

### SOLID Principle Violations
```bash
# Run SOLID analysis
/solid

# Address violations based on report
# Re-run analysis to verify fixes
/solid
```

### Security Issues
```bash
# Run security scan
bandit -r app/

# Address security vulnerabilities
# Re-run security scan
```

## Success Criteria

The `/done` command is considered successful when:

### For `/done` (Standard Mode)
1. **All Quality Checks Pass**
   - ✅ Linting: No violations
   - ✅ Type checking: No errors
   - ✅ Security scan: No vulnerabilities
   - ✅ SOLID principles: No violations

2. **All Tests Pass**
   - ✅ Unit tests: 100% pass rate
   - ✅ Integration tests: 100% pass rate
   - ✅ Coverage: Meets minimum requirements
   - ✅ Performance tests: Within acceptable limits

3. **Build Verification**
   - ✅ Backend: Compiles without errors
   - ✅ Frontend: Builds for production
   - ✅ Docker: Images build successfully

4. **Pull Request Created**
   - ✅ PR created with comprehensive description
   - ✅ All CI/CD checks passing
   - ✅ Ready for code review

### For `/done with merge` (Auto-Merge Mode)
All standard criteria PLUS:

5. **Branch Protection Compliance**
   - ✅ Required status checks passing
   - ✅ Required reviews obtained (if configured)
   - ✅ No merge conflicts detected
   - ✅ Branch is up to date with base branch

6. **Auto-Merge Execution**
   - ✅ PR automatically merged and squashed
   - ✅ Feature branch deleted
   - ✅ Local cleanup completed
   - ✅ Main branch updated

## Command Execution Examples

### Example 1: Standard Mode
```bash
# User runs: /done
# System Response:

"🚀 Starting completion workflow for branch: feature/auth-system"
""
"📋 Step 1/8: Pre-commit validation"
"✅ On feature branch: feature/auth-system"
"✅ Working directory clean"
"✅ Ready to proceed"
""
"🔍 Step 2/8: Code quality checks"
"✅ Backend linting passed"
"✅ Frontend linting passed"
"✅ Type checking passed"
"✅ Security scan clean"
"✅ SOLID principles compliant"
""
"🧪 Step 3/8: Comprehensive testing"
"✅ Backend tests: 247 passed, 95% coverage"
"✅ Frontend tests: 89 passed, 78% coverage"
"✅ Integration tests: 23 passed"
"✅ All coverage requirements met"
""
"🏗️ Step 4/8: Build verification"
"✅ Backend compilation successful"
"✅ Frontend production build successful"
"✅ Docker images built successfully"
""
"💾 Step 5/8: Committing changes"
"✅ Staged 12 files"
"✅ Created commit: feat(auth): Add user authentication system"
""
"📤 Step 6/8: Push and create PR"
"✅ Pushed to origin/feature/auth-system"
"✅ PR created: #42 - feat: Add user authentication system"
""
"🔄 Step 7/8: CI/CD verification"
"✅ Build check passed (2m 14s)"
"✅ Test check passed (3m 45s)"
"✅ Quality check passed (1m 32s)"
"✅ Security check passed (45s)"
""
"🎉 Step 8/8: Completion"
"✅ All checks passed successfully"
"✅ PR ready for review: https://github.com/user/repo/pull/42"
"✅ Workflow completed successfully"
""
"📊 Summary:"
"- Files changed: 12"
"- Tests added: 23"
"- Coverage: 95% backend, 78% frontend"
"- Quality score: A+"
"- Security issues: 0"
"- Ready for merge after review"
```

### Example 2: Auto-Merge Mode
```bash
# User runs: /done with merge
# System Response:

"🚀 Starting completion workflow with auto-merge for branch: feature/auth-system"
""
"📋 Step 1/9: Pre-commit validation"
"✅ On feature branch: feature/auth-system"
"✅ Working directory clean"
"✅ Ready to proceed"
""
"🔍 Step 2/9: Code quality checks"
"✅ Backend linting passed"
"✅ Frontend linting passed"
"✅ Type checking passed"
"✅ Security scan clean"
"✅ SOLID principles compliant"
""
"🧪 Step 3/9: Comprehensive testing"
"✅ Backend tests: 247 passed, 95% coverage"
"✅ Frontend tests: 89 passed, 78% coverage"
"✅ Integration tests: 23 passed"
"✅ All coverage requirements met"
""
"🏗️ Step 4/9: Build verification"
"✅ Backend compilation successful"
"✅ Frontend production build successful"
"✅ Docker images built successfully"
""
"💾 Step 5/9: Committing changes"
"✅ Staged 12 files"
"✅ Created commit: feat(auth): Add user authentication system"
""
"📤 Step 6/9: Push and create PR"
"✅ Pushed to origin/feature/auth-system"
"✅ PR created: #42 - feat: Add user authentication system"
""
"🔄 Step 7/9: CI/CD verification"
"✅ Build check passed (2m 14s)"
"✅ Test check passed (3m 45s)"
"✅ Quality check passed (1m 32s)"
"✅ Security check passed (45s)"
""
"🔍 Step 8/9: Auto-merge validation"
"✅ All required checks passing"
"✅ No merge conflicts detected"
"✅ Branch protection rules satisfied"
"✅ PR is mergeable"
""
"🎯 Step 9/9: Auto-merge execution"
"✅ PR automatically merged and squashed"
"✅ Feature branch deleted from remote"
"✅ Switched to main branch"
"✅ Pulled latest changes"
"✅ Local cleanup completed"
""
"🎉 Workflow completed successfully!"
""
"📊 Summary:"
"- Files changed: 12"
"- Tests added: 23"
"- Coverage: 95% backend, 78% frontend"
"- Quality score: A+"
"- Security issues: 0"
"- Status: Merged and deployed"
"- Commit: feat(auth): Add user authentication system (abc123d)"
```

### Example 3: Auto-Merge Blocked
```bash
# User runs: /done with merge
# System Response:

"🚀 Starting completion workflow with auto-merge for branch: feature/risky-change"
""
[... all steps 1-7 pass successfully ...]
""
"🔍 Step 8/9: Auto-merge validation"
"✅ All required checks passing"
"✅ No merge conflicts detected"
"❌ Required review not obtained"
"❌ Auto-merge blocked by branch protection rules"
""
"⚠️ Auto-merge cannot proceed"
"Reason: Branch protection requires administrator review for this change"
""
"📋 Manual action required:"
"1. Request review from @admin-team"
"2. Once approved, run: gh pr merge 42 --squash --delete-branch"
"3. Or use GitHub web interface to merge"
""
"✅ PR created and ready for review: https://github.com/user/repo/pull/42"
"🔄 Auto-merge will activate once requirements are met"
```

## Integration with Visualization

Results are displayed in the Building tab showing:
- Workflow progress in real-time
- Quality metrics dashboard
- CI/CD pipeline status
- Historical completion trends

## Rollback Strategy

If the workflow fails at any step:

1. **Preserve Work**: All changes remain in working directory
2. **Detailed Error Report**: Specific failure points identified
3. **Recovery Options**: Clear next steps provided
4. **Manual Override**: Option to skip specific checks if justified

## Notes

- Command requires clean working directory to start
- All checks must pass before PR creation
- Integrates with existing make targets and tooling
- Follows established commit message conventions
- Respects branch protection rules
- Can be configured for different quality thresholds

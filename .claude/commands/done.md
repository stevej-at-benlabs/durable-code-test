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

### 4. AI Documentation Update Opportunities

Before committing, analyze changes for AI documentation updates:

#### IMPORTANT: Check Existing AI Documentation First
```bash
# ALWAYS check if .ai directory exists at project root
if [ -d ".ai" ]; then
    echo "Found .ai directory at project root"
else
    echo "ERROR: .ai directory not found - DO NOT create a new one"
    echo "The .ai directory should exist at the project root"
    exit 1
fi

# Read the AI documentation index to understand existing docs
if [ -f ".ai/index.json" ]; then
    # Parse index.json to understand:
    # - Existing feature documentation in .ai/features/
    # - Available templates in .ai/templates/
    # - Documentation standards in .ai/docs/
    # - How-to guides in .ai/howto/
    cat .ai/index.json
else
    echo "WARNING: .ai/index.json not found - cannot verify existing documentation"
fi
```

**CRITICAL**:
- The `.ai` directory MUST already exist at the project root
- NEVER create a new `.ai` directory - it should already be there
- Always read `.ai/index.json` first to understand what's already documented
- Only update existing files or add new ones to the existing structure

#### Automated Analysis of Changes
```bash
# Get list of changed files for analysis
git diff --name-only HEAD

# Check for changes that might require AI documentation updates
git diff --stat HEAD | grep -E "\.(py|tsx?|md|yml|json)$"

# Compare changes against existing documentation from index.json
# to identify what's new vs what's already documented
```

#### Documentation Update Opportunities

**Check for these scenarios and present user with update options:**

1. **New Templates Needed**
   - New file patterns that could benefit from templates
   - New component types not covered by existing templates
   - New API endpoint patterns

2. **Feature Documentation Updates**
   - New features added that should be documented in `.ai/features/`
   - Significant changes to existing features
   - New integration patterns or workflows

3. **Template Updates Required**
   - Changes to existing patterns that templates should reflect
   - New configuration options or parameters
   - Updated best practices or conventions

4. **Standards Updates**
   - New development patterns that should be standardized
   - Changes to coding conventions or style guides
   - Security or performance best practices

5. **Howto Guide Updates**
   - New commands or workflows that need documentation
   - Changes to existing procedures
   - New debugging techniques or troubleshooting steps

#### Implementation Guide for AI Assistant

When executing the `/done` command, the AI assistant MUST:

1. **First check for .ai directory**:
   ```python
   # Pseudo-code for AI implementation
   ai_dir = find_project_root() + "/.ai"
   if not exists(ai_dir):
       error("CRITICAL: .ai directory not found at project root")
       error("DO NOT create a new .ai directory")
       stop_execution()
   ```

2. **Read and parse .ai/index.json**:
   ```python
   index_path = ai_dir + "/index.json"
   if exists(index_path):
       index_data = read_json(index_path)
       existing_features = index_data.get("features", [])
       existing_templates = index_data.get("templates", [])
       # Use this to understand what's already documented
   ```

3. **Analyze changes against existing documentation**:
   ```python
   changed_files = git_diff_files()
   for file in changed_files:
       if is_new_feature(file) and file not in existing_features:
           suggest_feature_doc_update(file)
       if is_new_pattern(file) and pattern not in existing_templates:
           suggest_new_template(file)
   ```

#### Present Update Opportunities

The AI assistant should dynamically analyze the actual changes and present relevant opportunities:

1. **Analyze git diff to identify what changed**
2. **Compare changes against .ai/index.json to see what's already documented**
3. **Identify gaps and opportunities**
4. **Present ONLY relevant suggestions based on actual changes**

Example format (adjust based on actual changes):
```
🤖 AI Documentation Update Analysis

✅ Successfully located .ai directory at project root
✅ Read .ai/index.json (found X features, Y templates)

Based on your changes, I've identified opportunities to update AI documentation:

[Dynamic list based on actual changes - examples:]
- If new component type: Suggest template creation
- If new feature: Suggest feature documentation update
- If new pattern: Suggest standards update
- If nothing needs updating: State "No documentation updates needed"

Would you like me to update any of these?
```

**IMPORTANT**:
- Never suggest updates for things that haven't changed
- Always check if documentation already exists before suggesting creation
- Be specific about what changed and why it needs documentation

#### User Response Handling
```bash
# If user accepts updates, proceed with:
# 1. Update relevant .ai/ files
# 2. Include updates in the commit
# 3. Mention updates in commit message and PR description
```

### 5. Build Verification
Ensure production builds work correctly:

```bash
# Backend build verification
docker exec durable-code-backend-dev python -m py_compile $(find /app/app -name "*.py")

# Frontend production build
cd durable-code-app/frontend && npm run build

# Docker image builds (if applicable)
docker-compose build --no-cache
```

### 6. Commit Changes
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
- Update AI documentation (templates and feature docs)

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

### 7. Push and Create Pull Request
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
- 📚 AI documentation updated (templates, features, guides)

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

### 8. CI/CD Verification
Monitor and ensure all automated checks pass:

#### GitHub Actions Monitoring (Preferred Method - Dashboard)
```bash
# Use the dashboard monitor for real-time check status
make gh-watch-checks

# The dashboard provides:
# - Real-time updates every 5 seconds
# - Color-coded status indicators
# - Summary statistics
# - Non-scrolling display
```

#### Fallback Method (Manual Commands)
If `make gh-watch-checks` is not available, use manual commands:
```bash
# Watch CI/CD pipeline status
gh pr checks $(gh pr view --json number -q .number)

# View detailed check results
gh run list --branch $(git branch --show-current)

# Monitor specific check
gh run watch $(gh run list --branch $(git branch --show-current) --json databaseId -q .[0].databaseId)
```

#### Handling Check Failures
```bash
# Get detailed failure logs using Make target
make gh-check-details

# Or manually if Make target unavailable
gh run view $(gh run list --branch $(git branch --show-current) --json databaseId -q .[0].databaseId) --log-failed
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

### 9. Auto-Merge Decision (if 'with merge' specified)
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

### 10. Handle Check Failures
If any checks fail, address them systematically:

#### Failed Build
```bash
# Check build logs using Make target (preferred)
make gh-check-details

# Or manually if Make target unavailable
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
"🤖 Step 4/9: AI documentation analysis"
"✅ Analyzed 12 changed files"
"✅ Identified 3 documentation opportunities"
"✅ User accepted updates for templates and features"
"✅ Updated .ai/templates/react-hook.template"
"✅ Updated .ai/features/web-application.md"
""
"🏗️ Step 5/9: Build verification"
"✅ Backend compilation successful"
"✅ Frontend production build successful"
"✅ Docker images built successfully"
""
"💾 Step 6/9: Committing changes"
"✅ Staged 12 files"
"✅ Created commit: feat(auth): Add user authentication system"
""
"📤 Step 7/9: Push and create PR"
"✅ Pushed to origin/feature/auth-system"
"✅ PR created: #42 - feat: Add user authentication system"
""
"🔄 Step 8/9: CI/CD verification"
"🚀 Launching GitHub checks dashboard..."
"make gh-watch-checks"
""
"[Dashboard shows real-time check status]"
"✅ Build check passed (2m 14s)"
"✅ Test check passed (3m 45s)"
"✅ Quality check passed (1m 32s)"
"✅ Security check passed (45s)"
""
"🎉 Step 9/9: Completion"
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
"📋 Step 1/10: Pre-commit validation"
"✅ On feature branch: feature/auth-system"
"✅ Working directory clean"
"✅ Ready to proceed"
""
"🔍 Step 2/10: Code quality checks"
"✅ Backend linting passed"
"✅ Frontend linting passed"
"✅ Type checking passed"
"✅ Security scan clean"
"✅ SOLID principles compliant"
""
"🧪 Step 3/10: Comprehensive testing"
"✅ Backend tests: 247 passed, 95% coverage"
"✅ Frontend tests: 89 passed, 78% coverage"
"✅ Integration tests: 23 passed"
"✅ All coverage requirements met"
""
"🤖 Step 4/10: AI documentation analysis"
"✅ Analyzed 12 changed files"
"✅ Identified 2 documentation opportunities"
"✅ User accepted updates for new authentication patterns"
"✅ Updated .ai/features/web-application.md"
""
"🏗️ Step 5/10: Build verification"
"✅ Backend compilation successful"
"✅ Frontend production build successful"
"✅ Docker images built successfully"
""
"💾 Step 6/10: Committing changes"
"✅ Staged 12 files"
"✅ Created commit: feat(auth): Add user authentication system"
""
"📤 Step 7/10: Push and create PR"
"✅ Pushed to origin/feature/auth-system"
"✅ PR created: #42 - feat: Add user authentication system"
""
"🔄 Step 8/10: CI/CD verification"
"🚀 Launching GitHub checks dashboard..."
"make gh-watch-checks"
""
"[Dashboard monitoring all checks in real-time]"
"✅ Build check passed (2m 14s)"
"✅ Test check passed (3m 45s)"
"✅ Quality check passed (1m 32s)"
"✅ Security check passed (45s)"
"✅ Dashboard indicates: All checks passed!"
""
"🔍 Step 9/10: Auto-merge validation"
"✅ All required checks passing"
"✅ No merge conflicts detected"
"✅ Branch protection rules satisfied"
"✅ PR is mergeable"
""
"🎯 Step 10/10: Auto-merge execution"
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
"🔍 Step 9/10: Auto-merge validation"
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

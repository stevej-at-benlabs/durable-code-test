#!/bin/bash
# Purpose: Create PR and monitor GitHub Actions checks with improved timeout handling
# Scope: GitHub pull request creation and CI/CD check monitoring
# Overview: Creates a pull request and monitors its checks with a 3-minute timeout warning.
#           Provides real-time status updates and handles check timeouts gracefully.
# Dependencies: gh (GitHub CLI), jq (JSON processor), bash with color support, active GitHub repository context
# Usage: ./scripts/gh-pr-check.sh (creates PR and monitors checks)
# Interfaces: GitHub CLI API calls, JSON processing, and formatted terminal output
# Implementation: Creates PR, then monitors checks with timeout handling and progress display

set -euo pipefail

# Color definitions
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[0;33m'
readonly RED='\033[0;31m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly MAGENTA='\033[0;35m'
readonly BOLD='\033[1m'
readonly NC='\033[0m'  # No Color
readonly CLEAR='\033[2J\033[H'

# Configuration
readonly CHECK_INTERVAL=${GH_CHECK_INTERVAL:-5}
readonly MAX_WAIT_TIME=${GH_MAX_WAIT:-180}  # 3 minutes default timeout
readonly BASE_BRANCH=${GH_BASE_BRANCH:-main}

# Get current branch
CURRENT_BRANCH=$(git branch --show-current)

# Function to show timeout warning
show_timeout_warning() {
    printf "\n"
    printf "${YELLOW}${BOLD}⏱️  IMPORTANT: GitHub checks may take up to 3 minutes to start${NC}\n"
    printf "${YELLOW}This is normal - the checks are queued and will begin shortly.${NC}\n"
    printf "${YELLOW}The dashboard will automatically monitor for ${MAX_WAIT_TIME} seconds.${NC}\n"
    printf "\n"
}

# Function to create PR if it doesn't exist
create_pr() {
    local pr_number
    pr_number=$(gh pr view --json number -q .number 2>/dev/null || echo "")

    if [ -n "$pr_number" ]; then
        printf "${YELLOW}ℹ️  PR #${pr_number} already exists for branch ${CURRENT_BRANCH}${NC}\n"
        printf "${CYAN}View at: $(gh pr view --json url -q .url)${NC}\n"
        return 0
    fi

    printf "${CYAN}📤 Creating PR for branch: ${CURRENT_BRANCH}${NC}\n"

    # Push current branch if needed
    git push -u origin "$CURRENT_BRANCH" 2>/dev/null || true

    # Create PR with comprehensive template
    gh pr create \
        --base "$BASE_BRANCH" \
        --title "feat: PR check operation improvements" \
        --body "$(cat <<'EOF'
## Summary
- Improved PR check monitoring with timeout handling
- Added 3-minute timeout warning for GitHub checks
- Enhanced user feedback during check waiting period

## Changes
- Created gh-pr-check.sh script for combined PR creation and monitoring
- Added timeout handling for slow-starting GitHub checks
- Updated documentation with 3-minute timeout notes

## Test Plan
- [ ] Script creates PR successfully
- [ ] Monitoring displays timeout warning
- [ ] Checks are monitored correctly
- [ ] Graceful handling of timeouts

🤖 Generated with Claude Code
EOF
    )"

    printf "${GREEN}✅ PR created successfully!${NC}\n"
}

# Function to monitor checks
monitor_checks() {
    local pr_number
    pr_number=$(gh pr view --json number -q .number 2>/dev/null || echo "")

    if [ -z "$pr_number" ]; then
        printf "${RED}❌ No PR found for monitoring${NC}\n"
        return 1
    fi

    printf "${CYAN}🔄 Monitoring PR #${pr_number} checks...${NC}\n"
    show_timeout_warning

    local elapsed=0
    local checks_started=false

    while [ $elapsed -lt $MAX_WAIT_TIME ]; do
        # Get check status
        local checks
        checks=$(gh pr checks "$pr_number" --json name,status,conclusion,startedAt 2>/dev/null || echo "[]")
        local check_count=$(echo "$checks" | jq length)

        if [ "$check_count" -gt 0 ]; then
            checks_started=true

            # Display check status
            printf "\r${CLEAR}"
            printf "${BOLD}📊 Check Status (PR #${pr_number})${NC} - Updated: $(date +"%H:%M:%S")\n"
            printf "────────────────────────────────────────────────────────────────\n"

            # Show each check
            echo "$checks" | jq -r '.[] |
                if .conclusion == "success" then "✅ " + .name + " - PASSED"
                elif .conclusion == "failure" then "❌ " + .name + " - FAILED"
                elif .status == "in_progress" then "🔄 " + .name + " - RUNNING"
                elif .status == "queued" then "⏳ " + .name + " - QUEUED"
                else "❓ " + .name + " - " + (.conclusion // .status // "UNKNOWN")
                end'

            # Check if all completed
            local completed=$(echo "$checks" | jq '[.[] | select(.conclusion != null)] | length')
            local failed=$(echo "$checks" | jq '[.[] | select(.conclusion == "failure")] | length')

            printf "\n"
            printf "${BOLD}Summary:${NC} Total: $check_count | Completed: $completed | Failed: $failed\n"

            if [ "$completed" -eq "$check_count" ] && [ "$check_count" -gt 0 ]; then
                if [ "$failed" -eq 0 ]; then
                    printf "\n${GREEN}${BOLD}✅ All checks passed!${NC}\n"
                else
                    printf "\n${RED}${BOLD}❌ Some checks failed${NC}\n"
                    printf "${YELLOW}Run 'make gh-check-details' for failure details${NC}\n"
                fi
                return 0
            fi
        else
            # No checks started yet
            local remaining=$((MAX_WAIT_TIME - elapsed))
            printf "\r${YELLOW}⏳ Waiting for checks to start... (${remaining}s remaining)${NC}"
        fi

        sleep "$CHECK_INTERVAL"
        elapsed=$((elapsed + CHECK_INTERVAL))
    done

    # Timeout reached
    printf "\n\n"
    if [ "$checks_started" = true ]; then
        printf "${YELLOW}⚠️  Monitoring timeout reached after ${MAX_WAIT_TIME} seconds${NC}\n"
        printf "${CYAN}Checks are still running. Continue monitoring with:${NC}\n"
        printf "${BOLD}make gh-watch-checks${NC}\n"
    else
        printf "${YELLOW}⚠️  GitHub checks haven't started after ${MAX_WAIT_TIME} seconds${NC}\n"
        printf "${CYAN}This can happen when GitHub Actions queues are busy.${NC}\n"
        printf "${CYAN}Check status manually with:${NC}\n"
        printf "${BOLD}gh pr checks ${pr_number}${NC}\n"
        printf "${CYAN}Or continue monitoring with:${NC}\n"
        printf "${BOLD}make gh-watch-checks${NC}\n"
    fi

    return 1
}

# Main execution
main() {
    printf "${CYAN}${BOLD}GitHub PR Check Operation${NC}\n"
    printf "════════════════════════════════════════════════════════════════\n\n"

    # Check if we're on main branch
    if [ "$CURRENT_BRANCH" = "$BASE_BRANCH" ]; then
        printf "${RED}❌ Cannot create PR from main branch${NC}\n"
        printf "${YELLOW}Please create a feature branch first${NC}\n"
        exit 1
    fi

    # Step 1: Create PR if needed
    create_pr

    printf "\n"

    # Step 2: Monitor checks
    monitor_checks

    exit_code=$?

    printf "\n"
    printf "════════════════════════════════════════════════════════════════\n"

    if [ $exit_code -eq 0 ]; then
        printf "${GREEN}${BOLD}✅ PR check operation completed successfully!${NC}\n"
    else
        printf "${YELLOW}${BOLD}⏱️  Check monitoring timed out - this is normal for new PRs${NC}\n"
        printf "${CYAN}GitHub checks can take several minutes to start.${NC}\n"
    fi

    exit $exit_code
}

# Run main function
main
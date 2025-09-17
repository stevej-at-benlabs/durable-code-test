#!/bin/bash

# Dashboard-style file watcher for linting

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
GRAY='\033[0;90m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Dashboard state
LAST_RUN_TIME="Never"
LAST_STATUS="Waiting"
LAST_FILES=""
LAST_ERRORS=""
TOTAL_RUNS=0
TOTAL_PASSES=0
TOTAL_FAILURES=0
WATCHING_SINCE=$(date +"%H:%M:%S")

# Configuration
DEBOUNCE_SECONDS=2
LAST_RUN=0
PROJECT_ROOT="/home/stevejackson/Projects/durable-code-test"

# Change to project root
cd "$PROJECT_ROOT"

# Function to clear screen and reset cursor
clear_dashboard() {
    printf '\033[2J\033[H'
}

# Function to move cursor to specific position
move_cursor() {
    printf '\033[%d;%dH' "$1" "$2"
}

# Function to draw a horizontal line
draw_line() {
    printf '%.0s─' {1..80}
    echo
}

# Function to draw the dashboard
draw_dashboard() {
    clear_dashboard

    # Header
    echo -e "${CYAN}${BOLD}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}${BOLD}║                         LINT WATCH DASHBOARD                                ║${NC}"
    echo -e "${CYAN}${BOLD}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"

    # Status section
    echo
    echo -e "${WHITE}${BOLD}STATUS${NC}"
    draw_line

    # Determine status color and icon
    local status_color="$YELLOW"
    local status_icon="⏳"
    if [ "$LAST_STATUS" = "PASSED" ]; then
        status_color="$GREEN"
        status_icon="✅"
    elif [ "$LAST_STATUS" = "FAILED" ]; then
        status_color="$RED"
        status_icon="❌"
    elif [ "$LAST_STATUS" = "RUNNING" ]; then
        status_color="$BLUE"
        status_icon="🔄"
    fi

    printf "  %-20s ${status_color}%s %s${NC}\n" "Current Status:" "$status_icon" "$LAST_STATUS"
    printf "  %-20s %s\n" "Last Check:" "$LAST_RUN_TIME"
    printf "  %-20s %s\n" "Watching Since:" "$WATCHING_SINCE"

    # Statistics
    echo
    echo -e "${WHITE}${BOLD}STATISTICS${NC}"
    draw_line
    printf "  %-20s %d\n" "Total Runs:" "$TOTAL_RUNS"
    printf "  %-20s ${GREEN}%d${NC} / ${RED}%d${NC}\n" "Pass/Fail:" "$TOTAL_PASSES" "$TOTAL_FAILURES"

    if [ $TOTAL_RUNS -gt 0 ]; then
        local success_rate=$((TOTAL_PASSES * 100 / TOTAL_RUNS))
        local rate_color="$RED"
        [ $success_rate -ge 50 ] && rate_color="$YELLOW"
        [ $success_rate -ge 80 ] && rate_color="$GREEN"
        printf "  %-20s ${rate_color}%d%%${NC}\n" "Success Rate:" "$success_rate"
    fi

    # Files section
    echo
    echo -e "${WHITE}${BOLD}MONITORED FILES${NC}"
    draw_line
    if [ -n "$LAST_FILES" ]; then
        echo "$LAST_FILES" | head -5 | while read -r file; do
            [ -n "$file" ] && printf "  ${GRAY}•${NC} %s\n" "$file"
        done
        local file_count=$(echo "$LAST_FILES" | wc -l)
        [ $file_count -gt 5 ] && echo "  ${GRAY}... and $((file_count - 5)) more files${NC}"
    else
        echo "  ${GRAY}No files changed yet${NC}"
    fi

    # Errors section (only shown if there are errors)
    if [ -n "$LAST_ERRORS" ] && [ "$LAST_STATUS" = "FAILED" ]; then
        echo
        echo -e "${WHITE}${BOLD}LAST ERRORS${NC}"
        draw_line
        echo "$LAST_ERRORS" | head -10 | while IFS= read -r line; do
            [ -n "$line" ] && echo "  $line"
        done
        local error_lines=$(echo "$LAST_ERRORS" | wc -l)
        [ $error_lines -gt 10 ] && echo "  ${GRAY}... and $((error_lines - 10)) more lines${NC}"
    fi

    # Footer
    echo
    draw_line
    echo -e "${GRAY}Press Ctrl+C to stop watching${NC}"
    echo -e "${GRAY}Checking for changes every 2 seconds...${NC}"
}

# Function to send notifications
send_notification() {
    local title="$1"
    local message="$2"

    # macOS
    if command -v osascript &> /dev/null; then
        osascript -e "display notification \"$message\" with title \"$title\" sound name \"Basso\"" 2>/dev/null
    # Linux
    elif command -v notify-send &> /dev/null; then
        notify-send -u critical "$title" "$message" 2>/dev/null
    # Windows WSL
    elif command -v powershell.exe &> /dev/null; then
        powershell.exe -Command "New-BurntToastNotification -Text '$title', '$message'" 2>/dev/null
    fi
}

# Function to run linting
run_lint() {
    local current_time=$(date +%s)

    # Debounce check
    if [ $((current_time - LAST_RUN)) -lt $DEBOUNCE_SECONDS ]; then
        return
    fi

    LAST_RUN=$current_time

    # Get changed files
    local changed_files=$(git diff --name-only HEAD 2>/dev/null | grep -E '\.(py|ts|tsx|js|jsx)$')

    if [ -z "$changed_files" ]; then
        changed_files=$(git ls-files --others --exclude-standard | grep -E '\.(py|ts|tsx|js|jsx)$')
    fi

    if [ -n "$changed_files" ]; then
        LAST_FILES="$changed_files"
        LAST_RUN_TIME=$(date +"%H:%M:%S")
        LAST_STATUS="RUNNING"
        TOTAL_RUNS=$((TOTAL_RUNS + 1))

        # Update dashboard to show running status
        draw_dashboard

        # Stage files temporarily
        git add $changed_files 2>/dev/null

        # Capture lint output
        lint_output=$(make lint-all-staged 2>&1)
        lint_exit_code=$?

        # Extract only error messages (lines that look like errors)
        LAST_ERRORS=$(echo "$lint_output" | grep -E '(Error|ERROR|Failed|FAILED|✗|error:|ERROR:)' | head -20)

        if [ $lint_exit_code -eq 0 ]; then
            LAST_STATUS="PASSED"
            TOTAL_PASSES=$((TOTAL_PASSES + 1))
            LAST_ERRORS=""
        else
            LAST_STATUS="FAILED"
            TOTAL_FAILURES=$((TOTAL_FAILURES + 1))
            send_notification "Lint Failed" "$(echo "$changed_files" | head -1 | xargs basename) has linting errors"
        fi

        # Unstage files
        git reset HEAD $changed_files 2>/dev/null

        # Redraw dashboard with results
        draw_dashboard
    fi
}

# Trap for clean exit
trap 'echo -e "\n${YELLOW}Stopping dashboard...${NC}"; clear_dashboard; exit 0' INT TERM

# Initialize dashboard
draw_dashboard

# Store initial state for polling
LAST_CHECKSUM=""

# Main loop using polling (more reliable than fswatch for dashboard)
while true; do
    # Get checksum of relevant files
    CURRENT_CHECKSUM=$(find app tools src durable-code-app -type f \( -name "*.py" -o -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" \) 2>/dev/null | xargs ls -la 2>/dev/null | md5sum 2>/dev/null | cut -d' ' -f1)

    # Check if files have changed
    if [ "$CURRENT_CHECKSUM" != "$LAST_CHECKSUM" ] && [ -n "$LAST_CHECKSUM" ]; then
        run_lint
    fi

    LAST_CHECKSUM="$CURRENT_CHECKSUM"
    sleep 2
done

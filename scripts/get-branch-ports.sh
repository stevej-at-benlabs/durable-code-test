#!/bin/bash

# Purpose: Calculate deterministic port assignments based on branch name for multi-branch development
# Scope: Port calculation utility for Docker development environments
# Overview: Generates consistent port numbers for frontend and backend services based on a hash
#     of the branch name. This allows multiple branches to run simultaneously without port conflicts.
#     The script uses a deterministic hash function to ensure the same branch always gets the same
#     ports, making it easy for developers to remember and bookmark their branch-specific URLs.
#     Port ranges are carefully selected to avoid common system ports and stay within valid ranges.
# Dependencies: Standard Unix utilities (cksum, awk, bc)
# Exports: FRONTEND_PORT and BACKEND_PORT environment variables
# Interfaces: Accepts branch name as argument, outputs port assignments
# Implementation: Hash-based port offset calculation with configurable ranges

set -e

# Get branch name from argument or git
BRANCH_NAME="${1:-$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'main')}"

# Normalize branch name (replace special chars with dash, lowercase)
BRANCH_NAME=$(echo "$BRANCH_NAME" | tr '/' '-' | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9-]/-/g')

# Base ports
FRONTEND_BASE=5173
BACKEND_BASE=8000

# Calculate hash-based offset (0-999 range to stay in reasonable port range)
# Use cksum for deterministic hash across systems
if [ "$BRANCH_NAME" = "main" ] || [ "$BRANCH_NAME" = "master" ] || [ "$BRANCH_NAME" = "develop" ]; then
    # Main branches use default ports
    OFFSET=0
else
    # Calculate offset based on branch name hash
    HASH=$(echo -n "$BRANCH_NAME" | cksum | cut -d' ' -f1)
    # Modulo 1000 to get offset in range 0-999
    # Add 1 to avoid offset 0 for feature branches
    OFFSET=$((($HASH % 1000) + 1))
fi

# Calculate final ports
FRONTEND_PORT=$((FRONTEND_BASE + OFFSET))
BACKEND_PORT=$((BACKEND_BASE + OFFSET))

# Ensure ports are in valid range (1024-65535)
# If somehow we exceed, wrap around
if [ $FRONTEND_PORT -gt 65535 ]; then
    FRONTEND_PORT=$((FRONTEND_PORT - 64000))
fi
if [ $BACKEND_PORT -gt 65535 ]; then
    BACKEND_PORT=$((BACKEND_PORT - 64000))
fi

# Output format based on arguments
case "${2:-export}" in
    export)
        # Default: Output as export statements for sourcing
        echo "export FRONTEND_PORT=$FRONTEND_PORT"
        echo "export BACKEND_PORT=$BACKEND_PORT"
        echo "export BRANCH_NAME=\"$BRANCH_NAME\""
        ;;
    json)
        # JSON format for programmatic use
        echo "{\"frontend\": $FRONTEND_PORT, \"backend\": $BACKEND_PORT, \"branch\": \"$BRANCH_NAME\"}"
        ;;
    plain)
        # Plain text format for display
        echo "Branch: $BRANCH_NAME"
        echo "Frontend Port: $FRONTEND_PORT"
        echo "Backend Port: $BACKEND_PORT"
        ;;
    urls)
        # URL format for easy access
        echo "Frontend URL: http://localhost:$FRONTEND_PORT"
        echo "Backend URL: http://localhost:$BACKEND_PORT"
        echo "API Docs: http://localhost:$BACKEND_PORT/docs"
        ;;
    *)
        echo "Usage: $0 [branch-name] [export|json|plain|urls]"
        exit 1
        ;;
esac

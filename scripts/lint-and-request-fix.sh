#!/bin/bash

# Script to lint staged files and request Claude to fix any issues

cd /home/stevejackson/Projects/durable-code-test

# Stage the file that was just written/edited
git add "$1" 2>/dev/null

# Run linting on staged files
if make lint-all-staged 2>&1; then
    echo "✅ Linting passed - no issues found"
    exit 0
else
    echo "❌ Linting failed - issues detected"
    echo ""
    echo "CLAUDE ACTION REQUIRED: Please fix the linting errors above"
    echo "The following files have linting issues that need to be fixed:"
    git diff --cached --name-only --diff-filter=ACM
    echo ""
    echo "Please:"
    echo "1. Review the linting errors shown above"
    echo "2. Fix each issue in the affected files"
    echo "3. Ensure the code follows project standards"
    exit 1
fi

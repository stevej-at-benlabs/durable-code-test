#!/bin/bash

# Fix all hardcoded font-size values with CSS variables

echo "Fixing hardcoded font-size values..."

cd durable-code-app/frontend

# Replace all font-size values with appropriate CSS variables
find src -name "*.css" -type f -exec sed -i \
  -e 's/font-size: 10px/font-size: var(--text-2xs)/g' \
  -e 's/font-size: 11px/font-size: var(--text-xs-plus)/g' \
  -e 's/font-size: 12px/font-size: var(--text-xs)/g' \
  -e 's/font-size: 14px/font-size: var(--text-sm)/g' \
  -e 's/font-size: 16px/font-size: var(--text-base)/g' \
  -e 's/font-size: 18px/font-size: var(--text-lg)/g' \
  -e 's/font-size: 20px/font-size: var(--text-xl)/g' \
  -e 's/font-size: 24px/font-size: var(--text-2xl)/g' \
  -e 's/font-size: 32px/font-size: var(--text-3xl-plus)/g' \
  {} \;

echo "✓ Font-size replacements complete!"

# Check results
echo "Checking for remaining hardcoded font-sizes..."
grep -r "font-size: [0-9]" src/ || echo "✓ No hardcoded font-sizes found!"

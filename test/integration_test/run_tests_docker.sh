#!/bin/bash
# Script to run Playwright tests in Docker using a simpler approach

# Colors for output
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${CYAN}Running Playwright integration tests in Docker...${NC}"

# Run tests using Python container with Playwright
docker run --rm \
  --network durable-code-test_durable-network \
  -v $(pwd)/test/integration_test:/tests \
  -w /tests \
  python:3.11-slim bash -c "
    apt-get update && apt-get install -y wget gnupg
    pip install --no-cache-dir playwright pytest pytest-asyncio pytest-playwright
    playwright install-deps chromium
    playwright install chromium
    pytest -v test_oscilloscope_playwright.py --asyncio-mode=auto
  "

if [ $? -eq 0 ]; then
  echo -e "${GREEN}✓ Playwright tests completed successfully!${NC}"
else
  echo -e "${RED}✗ Playwright tests failed${NC}"
  exit 1
fi

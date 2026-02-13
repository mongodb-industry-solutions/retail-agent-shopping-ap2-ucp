#!/bin/bash
#
# Run All Tests
#

set -euo pipefail

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "================================================"
echo "🧪 Running All API Tests"
echo "================================================"
echo ""

# Track overall results
TOTAL_SUITES=0
PASSED_SUITES=0
FAILED_SUITES=0

# Run each test suite
run_test_suite() {
    local test_file=$1
    local test_name=$(basename "$test_file" .sh)

    ((TOTAL_SUITES++))

    echo "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo "${BLUE}Running: $test_name${NC}"
    echo "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    if bash "$test_file"; then
        echo "${GREEN}✅ $test_name: PASSED${NC}"
        ((PASSED_SUITES++))
    else
        echo "${RED}❌ $test_name: FAILED${NC}"
        ((FAILED_SUITES++))
    fi

    echo ""
}

# Run test suites
run_test_suite "$SCRIPT_DIR/api/test_auth.sh"
run_test_suite "$SCRIPT_DIR/api/test_mandates.sh"

# Print overall summary
echo "================================================"
echo "📊 Overall Test Results"
echo "================================================"
echo "${GREEN}✅ Passed:${NC}  $PASSED_SUITES / $TOTAL_SUITES"
echo "${RED}❌ Failed:${NC}  $FAILED_SUITES / $TOTAL_SUITES"
echo "================================================"

if [ $FAILED_SUITES -gt 0 ]; then
    echo "${RED}Some tests failed!${NC}"
    exit 1
else
    echo "${GREEN}All tests passed!${NC}"
    exit 0
fi



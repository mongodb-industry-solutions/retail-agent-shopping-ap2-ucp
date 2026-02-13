#!/bin/bash
#
# Test Helpers - Shared functions for API tests
#

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test run configuration
export TEST_RUN_ID="test_$(date +%s)_$$"
export TEST_PREFIX="test_$(date +%s)"

# Test counters
export TESTS_PASSED=0
export TESTS_FAILED=0
export TESTS_SKIPPED=0

# Initialize API response variables
export LAST_STATUS=0
export LAST_RESPONSE=""

# Generate unique test entity ID
generate_test_id() {
    local entity_type=${1:-"entity"}
    echo "${TEST_PREFIX}_${entity_type}_$(uuidgen | cut -d'-' -f1 | tr '[:upper:]' '[:lower:]')"
}

# Generate test agent ID
generate_test_agent_id() {
    local agent_name=${1:-"agent"}
    echo "${TEST_PREFIX}_${agent_name}"
}

# Add test metadata to JSON
add_test_metadata() {
    local json=$1
    echo "$json" | jq --arg run_id "$TEST_RUN_ID" \
                      --arg suite "$TEST_SUITE" \
                      '. + {
                          metadata: (.metadata // {}) + {
                              is_test: true,
                              test_run_id: $run_id,
                              test_suite: $suite
                          }
                      }'
}

# Make authenticated API request
api_request() {
    local method=$1
    local endpoint=$2
    local data=${3:-""}

    local url="${BASE_URL}${endpoint}"
    local response_file=$(mktemp)
    local headers_file=$(mktemp)

    if [ -n "$data" ]; then
        curl -s -w "\n%{http_code}" -X "$method" "$url" \
            -H "Authorization: Bearer ${API_KEY}" \
            -H "Content-Type: application/json" \
            -d "$data" \
            -D "$headers_file" \
            > "$response_file"
    else
        curl -s -w "\n%{http_code}" -X "$method" "$url" \
            -H "Authorization: Bearer ${API_KEY}" \
            -D "$headers_file" \
            > "$response_file"
    fi

    # Read the full response
    local full_response=$(cat "$response_file")

    # Extract status code (last 3 digits after newline)
    export LAST_STATUS=$(echo "$full_response" | tail -c 4 | head -c 3)

    # Extract body (everything except last line with status code)
    # Handle both multi-line and single-line responses
    if echo "$full_response" | grep -q $'\n'; then
        # Has newline - status is on separate line
        export LAST_RESPONSE=$(echo "$full_response" | sed '$d')
    else
        # No newline - status is at the end of same line (shouldn't happen with -w "\n%{http_code}")
        export LAST_RESPONSE=$(echo "$full_response" | sed 's/[0-9][0-9][0-9]$//')
    fi

    rm -f "$response_file" "$headers_file"

    echo "$LAST_RESPONSE"
}

# Print test header
print_test_header() {
    local test_name=$1
    echo ""
    echo "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo "${BLUE}▶ ${test_name}${NC}"
    echo "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# Print test result
print_result() {
    local test_name=$1
    local passed=$2
    local message=${3:-""}

    if [ "$passed" = true ]; then
        echo "${GREEN}✅ PASS${NC}: $test_name"
        ((TESTS_PASSED++))
    else
        echo "${RED}❌ FAIL${NC}: $test_name"
        if [ -n "$message" ]; then
            echo "   ${RED}→${NC} $message"
        fi
        ((TESTS_FAILED++))
    fi
}

# Print skip message
print_skip() {
    local test_name=$1
    local reason=${2:-"Skipped"}
    echo "${YELLOW}⊘ SKIP${NC}: $test_name ($reason)"
    ((TESTS_SKIPPED++))
}

# Print test summary
print_summary() {
    local total=$((TESTS_PASSED + TESTS_FAILED + TESTS_SKIPPED))
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📊 Test Summary"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "${GREEN}✅ Passed:${NC}  $TESTS_PASSED"
    echo "${RED}❌ Failed:${NC}  $TESTS_FAILED"
    echo "${YELLOW}⊘ Skipped:${NC} $TESTS_SKIPPED"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Total: $total tests"

    if [ $TESTS_FAILED -gt 0 ]; then
        return 1
    else
        return 0
    fi
}

# Cleanup test data for this run
cleanup_test_run() {
    if [ "${SKIP_CLEANUP:-false}" != "true" ]; then
        echo ""
        echo "${YELLOW}🧹 Cleaning up test data for run: $TEST_RUN_ID${NC}"

        # Find cleanup script (works from tests/ or tests/api/)
        local cleanup_script=""
        if [ -f "cleanup_test_data.py" ]; then
            cleanup_script="cleanup_test_data.py"
        elif [ -f "../cleanup_test_data.py" ]; then
            cleanup_script="../cleanup_test_data.py"
        elif [ -f "tests/cleanup_test_data.py" ]; then
            cleanup_script="tests/cleanup_test_data.py"
        fi

        if [ -n "$cleanup_script" ]; then
            python3 "$cleanup_script" --run-id "$TEST_RUN_ID" 2>/dev/null || {
                echo "${YELLOW}⚠️  Cleanup failed${NC}"
            }
        else
            echo "${YELLOW}⚠️  Cleanup script not found${NC}"
        fi
    else
        echo "${YELLOW}⚠️  Cleanup skipped (SKIP_CLEANUP=true)${NC}"
    fi
}

# Register cleanup on exit
trap cleanup_test_run EXIT

# Export functions
export -f generate_test_id
export -f generate_test_agent_id
export -f add_test_metadata
export -f api_request
export -f print_test_header
export -f print_result
export -f print_skip
export -f print_summary


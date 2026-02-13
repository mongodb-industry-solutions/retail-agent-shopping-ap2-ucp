#!/bin/bash
#
# Auth Endpoint Tests
#

set -eo pipefail  # Removed -u to allow unset variables

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEST_DIR="$(dirname "$SCRIPT_DIR")"

# Source utilities
source "$TEST_DIR/utils/test_helpers.sh"
source "$TEST_DIR/utils/assertions.sh"
source "$TEST_DIR/fixtures/test_config.sh"

export TEST_SUITE="test_auth.sh"

# Print header
echo "================================================"
echo "🔐 Testing Auth Endpoints"
echo "   Test Run ID: $TEST_RUN_ID"
echo "   Base URL: $BASE_URL"
echo "================================================"

# Global test data
TEST_API_KEY_ID=""
TEST_AGENT_ID=$(generate_test_agent_id "test_shopper")

#==========================================
# Test 1: Create API Key (Success)
#==========================================
test_create_api_key() {
    print_test_header "Test 1: Create API Key"

    local request=$(cat <<EOF
{
  "agent_id": "$TEST_AGENT_ID",
  "agent_type": "shopping-agent",
  "scopes": ["mandate:read", "mandate:write"],
  "expires_in_days": 30
}
EOF
)

    api_request POST "/api/v1/auth/api-keys" "$request" > /dev/null
    local response="$LAST_RESPONSE"

    if assert_status 201 && \
       assert_json_exists ".key_id" && \
       assert_json_exists ".api_key" && \
       assert_json_equals ".agent_id" "$TEST_AGENT_ID"; then

        # Save key ID for later tests
        TEST_API_KEY_ID=$(echo "$response" | jq -r '.key_id')
        print_result "Create API Key" true
    else
        print_result "Create API Key" false "Status: $LAST_STATUS"
    fi
}

#==========================================
# Test 2: List API Keys
#==========================================
test_list_api_keys() {
    print_test_header "Test 2: List API Keys"

    api_request GET "/api/v1/auth/api-keys" > /dev/null
    local response="$LAST_RESPONSE"

    if assert_status 200; then
        print_result "List API Keys" true
    else
        print_result "List API Keys" false "Status: $LAST_STATUS"
    fi
}

#==========================================
# Test 3: Get API Key Details
#==========================================
test_get_api_key() {
    print_test_header "Test 3: Get API Key Details"

    if [ -z "$TEST_API_KEY_ID" ]; then
        print_skip "Get API Key Details" "No key ID from previous test"
        return
    fi

    api_request GET "/api/v1/auth/api-keys/$TEST_API_KEY_ID" > /dev/null
    local response="$LAST_RESPONSE"

    if assert_status 200 && \
       assert_json_equals ".key_id" "$TEST_API_KEY_ID"; then
        print_result "Get API Key Details" true
    else
        print_result "Get API Key Details" false "Status: $LAST_STATUS"
    fi
}

#==========================================
# Test 4: Revoke API Key
#==========================================
test_revoke_api_key() {
    print_test_header "Test 4: Revoke API Key"

    if [ -z "$TEST_API_KEY_ID" ]; then
        print_skip "Revoke API Key" "No key ID from previous test"
        return
    fi

    local request=$(cat <<EOF
{
  "reason": "Test cleanup"
}
EOF
)

    api_request DELETE "/api/v1/auth/api-keys/$TEST_API_KEY_ID" "$request" > /dev/null
    local response="$LAST_RESPONSE"

    if assert_status 200; then
        print_result "Revoke API Key" true
    else
        print_result "Revoke API Key" false "Status: $LAST_STATUS"
    fi
}

#==========================================
# Test 5: Create API Key Without Scope (Should Fail)
#==========================================
test_create_api_key_invalid() {
    print_test_header "Test 5: Create API Key (Invalid Request)"

    local request=$(cat <<EOF
{
  "agent_id": "$(generate_test_agent_id "invalid")",
  "agent_type": "shopping-agent"
}
EOF
)

    api_request POST "/api/v1/auth/api-keys" "$request" > /dev/null
    local response="$LAST_RESPONSE"

    # Should fail with 422 (validation error)
    if assert_status 422; then
        print_result "Create API Key (Invalid)" true "Correctly rejected"
    else
        print_result "Create API Key (Invalid)" false "Expected 422, got $LAST_STATUS"
    fi
}

#==========================================
# Test 6: Get Non-existent API Key
#==========================================
test_get_nonexistent_key() {
    print_test_header "Test 6: Get Non-existent API Key"

    local fake_key_id="key_00000000-0000-0000-0000-000000000000"
    api_request GET "/api/v1/auth/api-keys/$fake_key_id" > /dev/null
    local response="$LAST_RESPONSE"

    # Should return 404
    if assert_status 404; then
        print_result "Get Non-existent Key" true "Correctly returned 404"
    else
        print_result "Get Non-existent Key" false "Expected 404, got $LAST_STATUS"
    fi
}

#==========================================
# Run all tests
#==========================================
test_create_api_key
test_list_api_keys
test_get_api_key
test_revoke_api_key
test_create_api_key_invalid
test_get_nonexistent_key

# Print summary
print_summary
exit_code=$?

exit $exit_code


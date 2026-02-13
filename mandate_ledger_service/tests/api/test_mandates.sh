#!/bin/bash
#
# Mandate Endpoint Tests
#

set -eo pipefail  # Removed -u to allow unset variables

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEST_DIR="$(dirname "$SCRIPT_DIR")"

# Source utilities
source "$TEST_DIR/utils/test_helpers.sh"
source "$TEST_DIR/utils/assertions.sh"
source "$TEST_DIR/fixtures/test_config.sh"

export TEST_SUITE="test_mandates.sh"

# Print header
echo "================================================"
echo "📝 Testing Mandate Endpoints"
echo "   Test Run ID: $TEST_RUN_ID"
echo "   Base URL: $BASE_URL"
echo "================================================"

# Global test data
TEST_ENTITY_ID=""

#==========================================
# Test 1: Create Intent Mandate
#==========================================
test_create_intent() {
    print_test_header "Test 1: Create Intent Mandate"

    local entity_id=$(generate_test_id "mandate")
    local fixture=$(cat "$TEST_DIR/fixtures/intent_mandate.json")

    # Add test metadata and entity_id
    local request=$(echo "$fixture" | jq --arg id "$entity_id" \
                                         --arg run_id "$TEST_RUN_ID" \
                                         '.entity_id = $id |
                                          .metadata.is_test = true |
                                          .metadata.test_run_id = $run_id')

    api_request POST "/api/v1/mandates" "$request" > /dev/null
    local response="$LAST_RESPONSE"

    if assert_status 201 && \
       assert_json_exists ".entity_id" && \
       assert_json_equals ".mandate_type" "IntentMandate"; then

        # Save the actual entity_id returned by API
        TEST_ENTITY_ID=$(echo "$response" | jq -r '.entity_id')
        print_result "Create Intent Mandate" true
    else
        print_result "Create Intent Mandate" false "Status: $LAST_STATUS"
    fi
}

#==========================================
# Test 2: Get Mandate
#==========================================
test_get_mandate() {
    print_test_header "Test 2: Get Mandate"

    if [ -z "$TEST_ENTITY_ID" ]; then
        print_skip "Get Mandate" "No entity ID from previous test"
        return
    fi

    api_request GET "/api/v1/mandates/$TEST_ENTITY_ID" > /dev/null
    local response="$LAST_RESPONSE"

    if assert_status 200 && \
       assert_json_equals ".entity_id" "$TEST_ENTITY_ID"; then
        print_result "Get Mandate" true
    else
        print_result "Get Mandate" false "Status: $LAST_STATUS"
    fi
}

#==========================================
# Test 3: Update Mandate to Cart
#==========================================
test_update_to_cart() {
    print_test_header "Test 3: Update Mandate (Intent → Cart)"

    if [ -z "$TEST_ENTITY_ID" ]; then
        print_skip "Update to Cart" "No entity ID from previous test"
        return
    fi

    local fixture=$(cat "$TEST_DIR/fixtures/cart_mandate.json")
    local request=$(echo "$fixture" | jq --arg run_id "$TEST_RUN_ID" \
                                         '.metadata.is_test = true |
                                          .metadata.test_run_id = $run_id')

    api_request PUT "/api/v1/mandates/$TEST_ENTITY_ID" "$request" > /dev/null
    local response="$LAST_RESPONSE"

    if assert_status 200 && \
       assert_json_equals ".mandate_type" "CartMandate"; then
        print_result "Update to Cart" true
    else
        print_result "Update to Cart" false "Status: $LAST_STATUS"
    fi
}

#==========================================
# Test 4: Get Mandate History
#==========================================
test_get_history() {
    print_test_header "Test 4: Get Mandate History"

    if [ -z "$TEST_ENTITY_ID" ]; then
        print_skip "Get History" "No entity ID from previous test"
        return
    fi

    api_request GET "/api/v1/mandates/$TEST_ENTITY_ID/history" > /dev/null
    local response="$LAST_RESPONSE"

    if assert_status 200 && \
       assert_array_length ".versions" 2; then
        print_result "Get Mandate History" true
    else
        print_result "Get Mandate History" false "Expected 2 versions"
    fi
}

#==========================================
# Test 5: Search Mandates
#==========================================
test_search_mandates() {
    print_test_header "Test 5: Search Mandates"

    local request=$(cat <<EOF
{
  "mandate_type": "Cart",
  "limit": 10
}
EOF
)

    api_request POST "/api/v1/mandates/search" "$request" > /dev/null
    local response="$LAST_RESPONSE"

    if assert_status 200; then
        print_result "Search Mandates" true
    else
        print_result "Search Mandates" false "Status: $LAST_STATUS"
    fi
}

#==========================================
# Test 6: Create Cart Mandate (Direct)
#==========================================
test_create_cart() {
    print_test_header "Test 6: Create Cart Mandate (Direct)"

    local entity_id=$(generate_test_id "cart")
    local fixture=$(cat "$TEST_DIR/fixtures/cart_mandate.json")

    local request=$(echo "$fixture" | jq --arg id "$entity_id" \
                                         --arg run_id "$TEST_RUN_ID" \
                                         '.entity_id = $id |
                                          .metadata.is_test = true |
                                          .metadata.test_run_id = $run_id')

    api_request POST "/api/v1/mandates" "$request" > /dev/null
    local response="$LAST_RESPONSE"

    if assert_status 201 && \
       assert_json_equals ".mandate_type" "CartMandate"; then
        print_result "Create Cart Mandate" true
    else
        print_result "Create Cart Mandate" false "Status: $LAST_STATUS"
    fi
}

#==========================================
# Test 7: Create Payment Mandate (Direct)
#==========================================
test_create_payment() {
    print_test_header "Test 7: Create Payment Mandate (Direct)"

    local entity_id=$(generate_test_id "payment")
    local fixture=$(cat "$TEST_DIR/fixtures/payment_mandate.json")

    local request=$(echo "$fixture" | jq --arg id "$entity_id" \
                                         --arg run_id "$TEST_RUN_ID" \
                                         '.entity_id = $id |
                                          .metadata.is_test = true |
                                          .metadata.test_run_id = $run_id')

    api_request POST "/api/v1/mandates" "$request" > /dev/null
    local response="$LAST_RESPONSE"

    if assert_status 201 && \
       assert_json_equals ".mandate_type" "PaymentMandate"; then
        print_result "Create Payment Mandate" true
    else
        print_result "Create Payment Mandate" false "Status: $LAST_STATUS"
    fi
}

#==========================================
# Test 8: Get Non-existent Mandate
#==========================================
test_get_nonexistent() {
    print_test_header "Test 8: Get Non-existent Mandate"

    local fake_id="mandate_00000000-0000-0000-0000-000000000000"
    api_request GET "/api/v1/mandates/$fake_id" > /dev/null
    local response="$LAST_RESPONSE"

    if assert_status 404; then
        print_result "Get Non-existent Mandate" true "Correctly returned 404"
    else
        print_result "Get Non-existent Mandate" false "Expected 404, got $LAST_STATUS"
    fi
}

#==========================================
# Run all tests
#==========================================
test_create_intent
test_get_mandate
test_update_to_cart
test_get_history
test_search_mandates
test_create_cart
test_create_payment
test_get_nonexistent

# Print summary
print_summary
exit_code=$?

exit $exit_code


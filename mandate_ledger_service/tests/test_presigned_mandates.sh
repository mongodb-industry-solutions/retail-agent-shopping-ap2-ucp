#!/bin/bash
set -euo pipefail

# Test script for pre-signed mandate creation (Solution 2)
# This tests creating mandates that are already signed in a single API call

BASE_URL="http://localhost:8001"
API_KEY="mlsk_2805c1e7a703c27bfbb1a9b2017cd6ea"  # Admin key

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Testing Pre-Signed Mandate Creation"
echo "=========================================="
echo ""

# Generate unique IDs
TRANSACTION_ID="txn_presigned_test_$(date +%s)"
echo "Transaction ID: $TRANSACTION_ID"
echo ""

# Helper function to make API requests
api_request() {
    local method=$1
    local endpoint=$2
    local data=$3

    curl -s -X "$method" \
        "$BASE_URL$endpoint" \
        -H "X-API-Key: $API_KEY" \
        -H "Content-Type: application/json" \
        -d "$data"
}

# Helper function to extract JSON field
get_field() {
    echo "$1" | jq -r "$2"
}

# ==================== Test 1: Create Pre-Signed IntentMandate ====================
echo -e "${YELLOW}Test 1: Create Pre-Signed IntentMandate in Single API Call${NC}"

INTENT_RESPONSE=$(api_request POST "/api/v1/mandates" '{
  "mandate_type": "IntentMandate",
  "mandate_data": {
    "user_cart_confirmation_required": true,
    "natural_language_description": "Pre-signed test: Red basketball shoes under $200",
    "merchants": ["nike.com", "adidas.com"],
    "requires_refundability": true,
    "intent_expiry": "2025-12-31T23:59:59Z"
  },
  "transaction_id": "'"$TRANSACTION_ID"'",
  "metadata": {
    "test": "presigned_flow",
    "source": "test_script"
  },
  "initial_signatures": [
    {
      "signature": "0xPRESIGNED_INTENT_abc123def456",
      "signer_id": "shopping-agent-dev",
      "signer_type": "shopping_agent",
      "algorithm": "EdDSA",
      "signed_at": "'"$(date -u +%Y-%m-%dT%H:%M:%SZ)"'",
      "metadata": {
        "signing_method": "presigned_at_creation"
      }
    }
  ],
  "initial_status": "signed"
}')

INTENT_ID=$(get_field "$INTENT_RESPONSE" ".entity_id")
INTENT_STATUS=$(get_field "$INTENT_RESPONSE" ".status")
INTENT_VERSION=$(get_field "$INTENT_RESPONSE" ".version")

echo "Response: $INTENT_RESPONSE"
echo ""

if [ "$INTENT_STATUS" = "signed" ] && [ "$INTENT_VERSION" = "1" ]; then
    echo -e "${GREEN}✅ Test 1 PASSED${NC}"
    echo "   - IntentMandate created with status: $INTENT_STATUS"
    echo "   - Entity ID: $INTENT_ID"
    echo "   - Version: $INTENT_VERSION"
else
    echo -e "${RED}❌ Test 1 FAILED${NC}"
    echo "   Expected status: signed, Got: $INTENT_STATUS"
    echo "   Expected version: 1, Got: $INTENT_VERSION"
    exit 1
fi
echo ""

# ==================== Test 2: Verify Signatures Are Stored ====================
echo -e "${YELLOW}Test 2: Verify Signatures Are Stored Correctly${NC}"

MANDATE_DETAIL=$(api_request GET "/api/v1/mandates/$INTENT_ID" "")
# New API returns array of versions, latest is [0]
SIGNATURE_COUNT=$(echo "$MANDATE_DETAIL" | jq '.[0].signatures | length')
SIGNATURE_VALUE=$(echo "$MANDATE_DETAIL" | jq -r '.[0].signatures[0].signature')
SIGNER_ID=$(echo "$MANDATE_DETAIL" | jq -r '.[0].signatures[0].signer_id')

echo "Stored signatures: $SIGNATURE_COUNT"
echo "First signature: $SIGNATURE_VALUE"
echo "Signer ID: $SIGNER_ID"
echo ""

if [ "$SIGNATURE_COUNT" = "1" ] && [ "$SIGNATURE_VALUE" = "0xPRESIGNED_INTENT_abc123def456" ]; then
    echo -e "${GREEN}✅ Test 2 PASSED${NC}"
    echo "   - Signature stored correctly"
    echo "   - Signer ID: $SIGNER_ID"
else
    echo -e "${RED}❌ Test 2 FAILED${NC}"
    echo "   Expected 1 signature, Got: $SIGNATURE_COUNT"
    echo "   Expected signature: 0xPRESIGNED_INTENT_abc123def456"
    echo "   Got: $SIGNATURE_VALUE"
    exit 1
fi
echo ""

# ==================== Test 3: Create Pre-Signed CartMandate ====================
echo -e "${YELLOW}Test 3: Create Pre-Signed CartMandate${NC}"

CART_RESPONSE=$(api_request POST "/api/v1/mandates" '{
  "mandate_type": "CartMandate",
  "mandate_data": {
    "contents": {
      "id": "cart_presigned_test",
      "user_cart_confirmation_required": true,
      "payment_request": {
        "method_data": [
          {
            "supported_methods": "basic-card",
            "data": {"supportedNetworks": ["visa", "mastercard"]}
          }
        ],
        "details": {
          "id": "payment_details_presigned",
          "total": {"label": "Total", "amount": {"currency": "USD", "value": "199.99"}},
          "display_items": [
            {"label": "Basketball Shoes", "amount": {"currency": "USD", "value": "199.99"}}
          ]
        }
      },
      "cart_expiry": "2025-12-31T23:59:59Z",
      "merchant_name": "Nike Store"
    }
  },
  "transaction_id": "'"$TRANSACTION_ID"'",
  "metadata": {
    "test": "presigned_flow",
    "source": "merchant_agent"
  },
  "initial_signatures": [
    {
      "signature": "0xPRESIGNED_CART_xyz789ghi012",
      "signer_id": "merchant-agent-dev",
      "signer_type": "merchant_agent",
      "algorithm": "EdDSA",
      "signed_at": "'"$(date -u +%Y-%m-%dT%H:%M:%SZ)"'",
      "metadata": {
        "signing_method": "presigned_at_creation"
      }
    }
  ],
  "initial_status": "signed"
}')

CART_ID=$(get_field "$CART_RESPONSE" ".entity_id")
CART_STATUS=$(get_field "$CART_RESPONSE" ".status")

echo "Response: $CART_RESPONSE"
echo ""

if [ "$CART_STATUS" = "signed" ]; then
    echo -e "${GREEN}✅ Test 3 PASSED${NC}"
    echo "   - CartMandate created with status: $CART_STATUS"
    echo "   - Entity ID: $CART_ID"
else
    echo -e "${RED}❌ Test 3 FAILED${NC}"
    echo "   Expected status: signed, Got: $CART_STATUS"
    exit 1
fi
echo ""

# ==================== Test 4: Create Pre-Signed PaymentMandate ====================
echo -e "${YELLOW}Test 4: Create Pre-Signed PaymentMandate${NC}"

PAYMENT_RESPONSE=$(api_request POST "/api/v1/mandates" '{
  "mandate_type": "PaymentMandate",
  "mandate_data": {
    "payment_mandate_contents": {
      "payment_mandate_id": "pm_presigned_test",
      "payment_details_id": "pd_presigned_test",
      "payment_details_total": {"label": "Total", "amount": {"currency": "USD", "value": "199.99"}},
      "payment_response": {
        "request_id": "req_presigned_test",
        "method_name": "basic-card",
        "details": {"cardholderName": "Test User"}
      },
      "merchant_agent": "merchant-agent-dev",
      "timestamp": "'"$(date -u +%Y-%m-%dT%H:%M:%SZ)"'"
    }
  },
  "transaction_id": "'"$TRANSACTION_ID"'",
  "metadata": {
    "test": "presigned_flow",
    "source": "merchant_agent"
  },
  "initial_signatures": [
    {
      "signature": "0xPRESIGNED_PAYMENT_mno345pqr678",
      "signer_id": "merchant-agent-dev",
      "signer_type": "merchant_agent",
      "algorithm": "EdDSA",
      "signed_at": "'"$(date -u +%Y-%m-%dT%H:%M:%SZ)"'",
      "metadata": {
        "signing_method": "presigned_at_creation"
      }
    }
  ],
  "initial_status": "signed"
}')

PAYMENT_ID=$(get_field "$PAYMENT_RESPONSE" ".entity_id")
PAYMENT_STATUS=$(get_field "$PAYMENT_RESPONSE" ".status")

echo "Response: $PAYMENT_RESPONSE"
echo ""

if [ "$PAYMENT_STATUS" = "signed" ]; then
    echo -e "${GREEN}✅ Test 4 PASSED${NC}"
    echo "   - PaymentMandate created with status: $PAYMENT_STATUS"
    echo "   - Entity ID: $PAYMENT_ID"
else
    echo -e "${RED}❌ Test 4 FAILED${NC}"
    echo "   Expected status: signed, Got: $PAYMENT_STATUS"
    exit 1
fi
echo ""

# ==================== Test 5: Verify Audit Logs Show "Pre-Signed" ====================
echo -e "${YELLOW}Test 5: Verify Audit Logs Indicate Pre-Signed Creation${NC}"

AUDIT_LOGS=$(api_request GET "/api/v1/audit/entities/$INTENT_ID/trail?limit=10" "")

AUDIT_ACTION=$(echo "$AUDIT_LOGS" | jq -r '.[0].details.action')

echo "Audit log action: $AUDIT_ACTION"
echo ""

if echo "$AUDIT_ACTION" | grep -q "pre-signed"; then
    echo -e "${GREEN}✅ Test 5 PASSED${NC}"
    echo "   - Audit log correctly indicates pre-signed creation"
else
    echo -e "${RED}❌ Test 5 FAILED${NC}"
    echo "   Expected audit log to contain 'pre-signed'"
    echo "   Got: $AUDIT_ACTION"
    exit 1
fi
echo ""

# ==================== Test 6: Query All Mandates by Transaction ID ====================
echo -e "${YELLOW}Test 6: Query All Mandates by Transaction ID${NC}"

TRANSACTION_MANDATES=$(api_request GET "/api/v1/mandates/transaction/$TRANSACTION_ID" "")

# Should get array of 3 mandates (Intent, Cart, Payment)
MANDATE_COUNT=$(echo "$TRANSACTION_MANDATES" | jq '. | length')
echo "Mandates found for transaction: $MANDATE_COUNT"

if [ "$MANDATE_COUNT" = "3" ]; then
    # Verify they're in chronological order
    FIRST_TYPE=$(echo "$TRANSACTION_MANDATES" | jq -r '.[0].entity_type')
    SECOND_TYPE=$(echo "$TRANSACTION_MANDATES" | jq -r '.[1].entity_type')
    THIRD_TYPE=$(echo "$TRANSACTION_MANDATES" | jq -r '.[2].entity_type')

    echo "Order: $FIRST_TYPE → $SECOND_TYPE → $THIRD_TYPE"
    echo ""

    if [ "$FIRST_TYPE" = "IntentMandate" ] && [ "$SECOND_TYPE" = "CartMandate" ] && [ "$THIRD_TYPE" = "PaymentMandate" ]; then
        echo -e "${GREEN}✅ Test 6 PASSED${NC}"
        echo "   - All 3 mandates found in chronological order"
    else
        echo -e "${RED}❌ Test 6 FAILED${NC}"
        echo "   Expected order: IntentMandate → CartMandate → PaymentMandate"
        exit 1
    fi
else
    echo -e "${RED}❌ Test 6 FAILED${NC}"
    echo "   Expected 3 mandates, Got: $MANDATE_COUNT"
    echo "   Response: $TRANSACTION_MANDATES"
    exit 1
fi
echo ""

# ==================== Summary ====================
echo "=========================================="
echo -e "${GREEN}ALL TESTS PASSED! ✅${NC}"
echo "=========================================="
echo ""
echo "Summary:"
echo "  - IntentMandate (pre-signed): $INTENT_ID"
echo "  - CartMandate (pre-signed): $CART_ID"
echo "  - PaymentMandate (pre-signed): $PAYMENT_ID"
echo "  - Transaction ID: $TRANSACTION_ID"
echo ""
echo "Simplified API Design:"
echo "  ✅ POST /mandates - Create (supports pre-signed)"
echo "  ✅ GET /mandates/{entity_id} - Get all versions (latest at [0])"
echo "  ✅ GET /mandates/transaction/{txn_id} - Get all mandates for transaction"
echo "  ✅ GET /payments/{payment_id} - Get payment record"
echo "  ✅ GET /payments/session/{txn_id} - Get all payments for transaction"
echo ""
echo "Benefits:"
echo "  1. ✅ Single API call to create pre-signed mandates"
echo "  2. ✅ No redundant endpoints (removed sign, search, duplicate get)"
echo "  3. ✅ Transaction-focused queries (real use case)"
echo "  4. ✅ Always get full audit trail with version history"
echo ""


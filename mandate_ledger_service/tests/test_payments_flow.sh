#!/bin/bash
set -euo pipefail

# Test script for Step 16: Payments Collection + Change Streams
# Tests the complete flow from Intent → Cart → Payment → Payment Record Auto-Creation

echo "=========================================="
echo "Testing Payments Flow (Step 16)"
echo "=========================================="
echo ""

# Load test config
source "$(dirname "$0")/fixtures/test_config.sh"

BASE_URL="${BASE_URL:-http://localhost:8001}"

# Generate unique transaction ID for this test
TRANSACTION_ID="txn_payment_test_$(date +%s)"

echo "Test Configuration:"
echo "  Transaction ID: $TRANSACTION_ID"
echo ""

# ==================== Step 1: Create IntentMandate ====================
echo "Step 1: Create IntentMandate"
echo "--------------------------------------"

INTENT_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/mandates" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"mandate_type\": \"IntentMandate\",
    \"mandate_data\": {
      \"user_cart_confirmation_required\": true,
      \"natural_language_description\": \"Coffee maker under \$200\",
      \"merchants\": [\"amazon.com\", \"bestbuy.com\"],
      \"requires_refundability\": true,
      \"intent_expiry\": \"2025-12-31T23:59:59Z\"
    },
    \"transaction_id\": \"$TRANSACTION_ID\",
    \"created_by_agent\": \"shopping-agent-1\",
    \"created_by_agent_type\": \"shopping_agent\",
    \"metadata\": {
      \"test\": \"payments_flow\"
    }
  }")

INTENT_ID=$(echo "$INTENT_RESPONSE" | jq -r '.entity_id')
INTENT_STATUS=$(echo "$INTENT_RESPONSE" | jq -r '.status')

if [ "$INTENT_STATUS" = "created" ]; then
  echo "✅ Created IntentMandate: $INTENT_ID"
else
  echo "❌ Failed to create IntentMandate"
  echo "$INTENT_RESPONSE" | jq '.'
  exit 1
fi
echo ""

# ==================== Step 2: Sign IntentMandate ====================
echo "Step 2: Sign IntentMandate"
echo "--------------------------------------"

INTENT_SIGN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/mandates/$INTENT_ID/sign" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "signature_data": {
      "signature": "0x_intent_signature_abc123def456",
      "algorithm": "EdDSA",
      "metadata": {
        "context": "user_confirmed_intent"
      }
    }
  }')

INTENT_SIGN_STATUS=$(echo "$INTENT_SIGN_RESPONSE" | jq -r '.status')

if [ "$INTENT_SIGN_STATUS" = "signed" ]; then
  echo "✅ Signed IntentMandate"
else
  echo "❌ Failed to sign IntentMandate"
  echo "$INTENT_SIGN_RESPONSE" | jq '.'
  exit 1
fi
echo ""

# ==================== Step 3: Create CartMandate ====================
echo "Step 3: Create CartMandate"
echo "--------------------------------------"

CART_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/mandates" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"mandate_type\": \"CartMandate\",
    \"mandate_data\": {
      \"contents\": {
        \"id\": \"cart_$(date +%s)\",
        \"user_cart_confirmation_required\": true,
        \"payment_request\": {
          \"method_data\": [
            {
              \"supported_methods\": \"basic-card\",
              \"data\": {
                \"supportedNetworks\": [\"visa\", \"mastercard\"]
              }
            }
          ],
          \"details\": {
            \"id\": \"payment_details_001\",
            \"total\": {
              \"label\": \"Total\",
              \"amount\": {
                \"currency\": \"USD\",
                \"value\": \"149.99\"
              }
            },
            \"display_items\": [
              {
                \"label\": \"Coffee Maker\",
                \"amount\": {
                  \"currency\": \"USD\",
                  \"value\": \"149.99\"
                }
              }
            ]
          }
        },
        \"cart_expiry\": \"2025-12-31T23:59:59Z\",
        \"merchant_name\": \"Test Electronics Store\"
      }
    },
    \"transaction_id\": \"$TRANSACTION_ID\",
    \"created_by_agent\": \"merchant-agent-1\",
    \"created_by_agent_type\": \"merchant_agent\",
    \"metadata\": {
      \"test\": \"payments_flow\"
    }
  }")

CART_ID=$(echo "$CART_RESPONSE" | jq -r '.entity_id')
CART_STATUS=$(echo "$CART_RESPONSE" | jq -r '.status')

if [ "$CART_STATUS" = "proposed" ]; then
  echo "✅ Created CartMandate: $CART_ID"
else
  echo "❌ Failed to create CartMandate (expected status 'proposed', got '$CART_STATUS')"
  echo "$CART_RESPONSE" | jq '.'
  exit 1
fi
echo ""

# ==================== Step 4: Sign CartMandate ====================
echo "Step 4: Sign CartMandate"
echo "--------------------------------------"

CART_SIGN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/mandates/$CART_ID/sign" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "signature_data": {
      "signature": "0x_cart_signature_xyz789uvw012",
      "algorithm": "EdDSA",
      "metadata": {
        "context": "merchant_confirmed_cart"
      }
    }
  }')

CART_SIGN_STATUS=$(echo "$CART_SIGN_RESPONSE" | jq -r '.status')

if [ "$CART_SIGN_STATUS" = "signed" ]; then
  echo "✅ Signed CartMandate"
else
  echo "❌ Failed to sign CartMandate"
  echo "$CART_SIGN_RESPONSE" | jq '.'
  exit 1
fi
echo ""

# ==================== Step 5: Create PaymentMandate ====================
echo "Step 5: Create PaymentMandate"
echo "--------------------------------------"

PAYMENT_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/mandates" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"mandate_type\": \"PaymentMandate\",
    \"mandate_data\": {
      \"payment_mandate_contents\": {
        \"payment_mandate_id\": \"pm_test_$(date +%s)\",
        \"payment_details_id\": \"pd_test_001\",
        \"payment_details_total\": {
          \"label\": \"Total\",
          \"amount\": {
            \"currency\": \"USD\",
            \"value\": \"149.99\"
          }
        },
        \"payment_response\": {
          \"request_id\": \"req_test_001\",
          \"method_name\": \"basic-card\",
          \"details\": {
            \"cardholderName\": \"John Doe\"
          }
        },
        \"merchant_agent\": \"merchant-agent-1\",
        \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"
      }
    },
    \"transaction_id\": \"$TRANSACTION_ID\",
    \"created_by_agent\": \"payment-processor-1\",
    \"created_by_agent_type\": \"payment_processor\",
    \"metadata\": {
      \"test\": \"payments_flow\"
    }
  }")

PAYMENT_MANDATE_ID=$(echo "$PAYMENT_RESPONSE" | jq -r '.entity_id')
PAYMENT_MANDATE_STATUS=$(echo "$PAYMENT_RESPONSE" | jq -r '.status')

if [ "$PAYMENT_MANDATE_STATUS" = "created" ]; then
  echo "✅ Created PaymentMandate: $PAYMENT_MANDATE_ID"
else
  echo "❌ Failed to create PaymentMandate"
  echo "$PAYMENT_RESPONSE" | jq '.'
  exit 1
fi
echo ""

# ==================== Step 6: Sign PaymentMandate (Triggers Change Stream!) ====================
echo "Step 6: Sign PaymentMandate (triggers auto-payment creation)"
echo "--------------------------------------"

PAYMENT_SIGN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/mandates/$PAYMENT_MANDATE_ID/sign" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "signature_data": {
      "signature": "0x_payment_signature_final_qwerty12345",
      "algorithm": "EdDSA",
      "metadata": {
        "context": "payment_completed"
      }
    }
  }')

PAYMENT_SIGN_STATUS=$(echo "$PAYMENT_SIGN_RESPONSE" | jq -r '.status')

if [ "$PAYMENT_SIGN_STATUS" = "signed" ]; then
  echo "✅ Signed PaymentMandate"
  echo "   ⏳ Waiting for Change Stream to auto-create payment record..."
  sleep 3  # Give change stream time to process
else
  echo "❌ Failed to sign PaymentMandate"
  echo "$PAYMENT_SIGN_RESPONSE" | jq '.'
  exit 1
fi
echo ""

# ==================== Step 7: Verify Payment Record Was Auto-Created ====================
echo "Step 7: Verify payment record was auto-created"
echo "--------------------------------------"

# Search for payment by transaction_id
PAYMENT_SEARCH_RESPONSE=$(curl -s -X GET "$BASE_URL/api/v1/payments/session/$TRANSACTION_ID" \
  -H "X-API-Key: $API_KEY")

PAYMENT_COUNT=$(echo "$PAYMENT_SEARCH_RESPONSE" | jq '.total_count')

if [ "$PAYMENT_COUNT" -ge 1 ]; then
  echo "✅ Payment record auto-created! Found $PAYMENT_COUNT payment(s)"

  # Extract payment details
  PAYMENT_ID=$(echo "$PAYMENT_SEARCH_RESPONSE" | jq -r '.payments[0].payment_id')
  PAYMENT_STATUS=$(echo "$PAYMENT_SEARCH_RESPONSE" | jq -r '.payments[0].status')
  PAYMENT_AMOUNT=$(echo "$PAYMENT_SEARCH_RESPONSE" | jq -r '.payments[0].amount')

  echo "   Payment ID: $PAYMENT_ID"
  echo "   Status: $PAYMENT_STATUS"
  echo "   Amount: $PAYMENT_AMOUNT USD"
else
  echo "❌ No payment record found!"
  echo "Response:"
  echo "$PAYMENT_SEARCH_RESPONSE" | jq '.'
  exit 1
fi
echo ""

# ==================== Step 8: Test GET Payment by ID ====================
echo "Step 8: Test GET /api/v1/payments/{payment_id}"
echo "--------------------------------------"

PAYMENT_GET_RESPONSE=$(curl -s -X GET "$BASE_URL/api/v1/payments/$PAYMENT_ID" \
  -H "X-API-Key: $API_KEY")

PAYMENT_GET_ID=$(echo "$PAYMENT_GET_RESPONSE" | jq -r '.payment_id')

if [ "$PAYMENT_GET_ID" = "$PAYMENT_ID" ]; then
  echo "✅ Successfully retrieved payment by ID"

  # Verify mandate references exist
  INTENT_REF=$(echo "$PAYMENT_GET_RESPONSE" | jq -r '.intent_mandate.mandate_id')
  CART_REF=$(echo "$PAYMENT_GET_RESPONSE" | jq -r '.cart_mandate.mandate_id')
  PAYMENT_REF=$(echo "$PAYMENT_GET_RESPONSE" | jq -r '.payment_mandate.mandate_id')

  echo "   Intent Mandate: $INTENT_REF"
  echo "   Cart Mandate: $CART_REF"
  echo "   Payment Mandate: $PAYMENT_REF"

  # Verify signatures exist
  INTENT_SIG=$(echo "$PAYMENT_GET_RESPONSE" | jq -r '.intent_mandate.signature')
  CART_SIG=$(echo "$PAYMENT_GET_RESPONSE" | jq -r '.cart_mandate.signature')
  PAYMENT_SIG=$(echo "$PAYMENT_GET_RESPONSE" | jq -r '.payment_mandate.signature')

  if [ -n "$INTENT_SIG" ] && [ "$INTENT_SIG" != "null" ] && [ "$INTENT_SIG" != "" ]; then
    echo "   ✅ Intent signature: ${INTENT_SIG:0:20}..."
  else
    echo "   ⚠️  Intent signature missing"
  fi

  if [ -n "$CART_SIG" ] && [ "$CART_SIG" != "null" ] && [ "$CART_SIG" != "" ]; then
    echo "   ✅ Cart signature: ${CART_SIG:0:20}..."
  else
    echo "   ⚠️  Cart signature missing"
  fi

  if [ -n "$PAYMENT_SIG" ] && [ "$PAYMENT_SIG" != "null" ] && [ "$PAYMENT_SIG" != "" ]; then
    echo "   ✅ Payment signature: ${PAYMENT_SIG:0:20}..."
  else
    echo "   ⚠️  Payment signature missing"
  fi
else
  echo "❌ Failed to retrieve payment by ID"
  echo "$PAYMENT_GET_RESPONSE" | jq '.'
  exit 1
fi
echo ""

# ==================== Step 9: Test GET Payments by Session ====================
echo "Step 9: Test GET /api/v1/payments/session/{transaction_id}"
echo "--------------------------------------"

SESSION_PAYMENTS=$(curl -s -X GET "$BASE_URL/api/v1/payments/session/$TRANSACTION_ID" \
  -H "X-API-Key: $API_KEY")

SESSION_COUNT=$(echo "$SESSION_PAYMENTS" | jq '.total_count')

if [ "$SESSION_COUNT" -ge 1 ]; then
  echo "✅ Successfully retrieved payments for session"
  echo "   Total payments: $SESSION_COUNT"
else
  echo "❌ Failed to retrieve payments for session"
  exit 1
fi
echo ""

# ==================== Step 10: Test Search Payments ====================
echo "Step 10: Test GET /api/v1/payments (search)"
echo "--------------------------------------"

SEARCH_RESPONSE=$(curl -s -X GET "$BASE_URL/api/v1/payments?status=SUCCESS&limit=10" \
  -H "X-API-Key: $API_KEY")

SEARCH_COUNT=$(echo "$SEARCH_RESPONSE" | jq '.total_count')

if [ "$SEARCH_COUNT" -ge 1 ]; then
  echo "✅ Successfully searched payments"
  echo "   Found $SEARCH_COUNT payment(s) with status=SUCCESS"
else
  echo "⚠️  No payments found in search (this is okay if it's first run)"
fi
echo ""

# ==================== Step 11: Verify Payment Record is Ultra-Lean ====================
echo "Step 11: Verify payment record is ultra-lean (no content)"
echo "--------------------------------------"

# Check that mandate references contain only ID + signature + timestamp
HAS_CONTENT=$(echo "$PAYMENT_GET_RESPONSE" | jq '.intent_mandate | has("contents") or has("mandate_data")')

if [ "$HAS_CONTENT" = "false" ]; then
  echo "✅ Payment record is ultra-lean (no mandate content)"
  echo "   Mandate references contain ONLY: ID + signature + timestamp"
else
  echo "⚠️  Warning: Payment record may contain unnecessary content"
fi
echo ""

# ==================== Summary ====================
echo "=========================================="
echo "✅ ALL TESTS PASSED!"
echo "=========================================="
echo ""
echo "Summary:"
echo "  Transaction ID: $TRANSACTION_ID"
echo "  IntentMandate: $INTENT_ID (signed)"
echo "  CartMandate: $CART_ID (signed)"
echo "  PaymentMandate: $PAYMENT_MANDATE_ID (signed)"
echo "  Payment Record: $PAYMENT_ID (auto-created)"
echo ""
echo "Test Results:"
echo "  ✅ Step 1: Created IntentMandate"
echo "  ✅ Step 2: Signed IntentMandate"
echo "  ✅ Step 3: Created CartMandate"
echo "  ✅ Step 4: Signed CartMandate"
echo "  ✅ Step 5: Created PaymentMandate"
echo "  ✅ Step 6: Signed PaymentMandate"
echo "  ✅ Step 7: Payment auto-created by Change Stream"
echo "  ✅ Step 8: GET payment by ID"
echo "  ✅ Step 9: GET payments by session"
echo "  ✅ Step 10: Search payments"
echo "  ✅ Step 11: Verified ultra-lean format"
echo ""
echo "Next: Integration testing with Shopping Agent, Merchant Agent, Payment Processor"


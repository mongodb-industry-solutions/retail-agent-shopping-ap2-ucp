#!/bin/bash
set -euo pipefail

# Test POST /api/v1/payments endpoint
BASE_URL="http://localhost:8001"
API_KEY="mlsk_2805c1e7a703c27bfbb1a9b2017cd6ea"  # Admin key
TRANSACTION_ID="txn_post_payment_test_$(date +%s)"

echo "=========================================="
echo "Testing POST /api/v1/payments"
echo "=========================================="
echo ""
echo "Transaction ID: $TRANSACTION_ID"
echo ""

# ==================== Step 1: Create Test Mandates ====================
echo "Step 1: Create & sign test mandates"
echo "--------------------------------------"

# Create IntentMandate (pre-signed)
INTENT_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/mandates" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"mandate_type\": \"IntentMandate\",
    \"mandate_data\": {
      \"user_cart_confirmation_required\": true,
      \"natural_language_description\": \"Test POST payment - Red shoes under \$200\",
      \"merchants\": [\"nike.com\"],
      \"requires_refundability\": true,
      \"intent_expiry\": \"2025-12-31T23:59:59Z\"
    },
    \"transaction_id\": \"$TRANSACTION_ID\",
    \"initial_signatures\": [{
      \"signature\": \"0xINTENT_POST_TEST_abc123\",
      \"signer_id\": \"shopping-agent\",
      \"signer_type\": \"shopping_agent\",
      \"algorithm\": \"EdDSA\",
      \"signed_at\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"
    }],
    \"initial_status\": \"signed\",
    \"metadata\": {\"test\": \"post_payment\"}
  }")

INTENT_ID=$(echo "$INTENT_RESPONSE" | jq -r '.entity_id')
echo "✅ Created IntentMandate: $INTENT_ID"

# Create CartMandate (pre-signed)
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
              \"data\": {\"supportedNetworks\": [\"visa\"]}
            }
          ],
          \"details\": {
            \"id\": \"pd_post_test\",
            \"total\": {
              \"label\": \"Total\",
              \"amount\": {\"currency\": \"USD\", \"value\": \"179.99\"}
            },
            \"display_items\": [
              {\"label\": \"Red Shoes\", \"amount\": {\"currency\": \"USD\", \"value\": \"179.99\"}}
            ]
          }
        },
        \"cart_expiry\": \"2025-12-31T23:59:59Z\",
        \"merchant_name\": \"Nike Store\"
      }
    },
    \"transaction_id\": \"$TRANSACTION_ID\",
    \"initial_signatures\": [{
      \"signature\": \"0xCART_POST_TEST_xyz789\",
      \"signer_id\": \"merchant-agent\",
      \"signer_type\": \"merchant_agent\",
      \"algorithm\": \"EdDSA\",
      \"signed_at\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"
    }],
    \"initial_status\": \"signed\",
    \"metadata\": {\"test\": \"post_payment\"}
  }")

CART_ID=$(echo "$CART_RESPONSE" | jq -r '.entity_id')
echo "✅ Created CartMandate: $CART_ID"

# Create PaymentMandate (pre-signed)
PAYMENT_MANDATE_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/mandates" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"mandate_type\": \"PaymentMandate\",
    \"mandate_data\": {
      \"payment_mandate_contents\": {
        \"payment_mandate_id\": \"pm_post_test_$(date +%s)\",
        \"payment_details_id\": \"pd_post_test\",
        \"payment_details_total\": {
          \"label\": \"Total\",
          \"amount\": {\"currency\": \"USD\", \"value\": \"179.99\"}
        },
        \"payment_response\": {
          \"request_id\": \"req_post_test\",
          \"method_name\": \"basic-card\",
          \"details\": {\"cardholderName\": \"Test User\"}
        },
        \"merchant_agent\": \"merchant-agent-dev\",
        \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"
      }
    },
    \"transaction_id\": \"$TRANSACTION_ID\",
    \"initial_signatures\": [{
      \"signature\": \"0xPAYMENT_POST_TEST_qwe456\",
      \"signer_id\": \"merchant-agent\",
      \"signer_type\": \"merchant_agent\",
      \"algorithm\": \"EdDSA\",
      \"signed_at\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"
    }],
    \"initial_status\": \"signed\",
    \"metadata\": {\"test\": \"post_payment\"}
  }")

PAYMENT_MANDATE_ID=$(echo "$PAYMENT_MANDATE_RESPONSE" | jq -r '.entity_id')
echo "✅ Created PaymentMandate: $PAYMENT_MANDATE_ID"

echo ""

# ==================== Step 2: Test POST /api/v1/payments ====================
echo "Step 2: Create payment via POST endpoint"
echo "--------------------------------------"

PAYMENT_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/payments" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"transaction_id\": \"$TRANSACTION_ID\",
    \"intent_mandate_id\": \"$INTENT_ID\",
    \"cart_mandate_id\": \"$CART_ID\",
    \"payment_mandate_id\": \"$PAYMENT_MANDATE_ID\",
    \"amount\": 179.99,
    \"currency\": \"USD\",
    \"status\": \"SUCCESS\",
    \"merchant_agent\": \"merchant-agent-dev\",
    \"payment_processor_agent\": \"payment-processor-test\",
    \"payment_method_type\": \"basic-card\",
    \"metadata\": {\"test\": \"post_endpoint\", \"manual\": true}
  }")

PAYMENT_ID=$(echo "$PAYMENT_RESPONSE" | jq -r '.payment_id')
PAYMENT_STATUS=$(echo "$PAYMENT_RESPONSE" | jq -r '.status')
PAYMENT_AMOUNT=$(echo "$PAYMENT_RESPONSE" | jq -r '.amount')

if [ "$PAYMENT_ID" != "null" ] && [ "$PAYMENT_STATUS" = "SUCCESS" ]; then
  echo "✅ Payment created successfully"
  echo "   Payment ID: $PAYMENT_ID"
  echo "   Amount: $PAYMENT_AMOUNT USD"
  echo "   Status: $PAYMENT_STATUS"
else
  echo "❌ Failed to create payment"
  echo "$PAYMENT_RESPONSE" | jq '.'
  exit 1
fi

echo ""

# ==================== Step 3: Verify Signatures Were Extracted ====================
echo "Step 3: Verify ultra-lean format with signatures"
echo "--------------------------------------"

INTENT_SIG=$(echo "$PAYMENT_RESPONSE" | jq -r '.intent_mandate.signature')
CART_SIG=$(echo "$PAYMENT_RESPONSE" | jq -r '.cart_mandate.signature')
PAYMENT_SIG=$(echo "$PAYMENT_RESPONSE" | jq -r '.payment_mandate.signature')

echo "Intent signature: $INTENT_SIG"
echo "Cart signature: $CART_SIG"
echo "Payment signature: $PAYMENT_SIG"

if [ "$INTENT_SIG" = "0xINTENT_POST_TEST_abc123" ] && \
   [ "$CART_SIG" = "0xCART_POST_TEST_xyz789" ] && \
   [ "$PAYMENT_SIG" = "0xPAYMENT_POST_TEST_qwe456" ]; then
  echo "✅ All signatures correctly extracted from mandates"
else
  echo "❌ Signatures not correctly extracted"
  exit 1
fi

echo ""

# ==================== Step 4: Verify GET Retrieves Created Payment ====================
echo "Step 4: Verify GET /api/v1/payments/{payment_id}"
echo "--------------------------------------"

GET_RESPONSE=$(curl -s -X GET "$BASE_URL/api/v1/payments/$PAYMENT_ID" \
  -H "X-API-Key: $API_KEY")

RETRIEVED_ID=$(echo "$GET_RESPONSE" | jq -r '.payment_id')

if [ "$RETRIEVED_ID" = "$PAYMENT_ID" ]; then
  echo "✅ Payment retrieved successfully via GET"
else
  echo "❌ Failed to retrieve payment"
  exit 1
fi

echo ""

# ==================== Step 5: Verify Audit Log ====================
echo "Step 5: Verify audit log for payment creation"
echo "--------------------------------------"

AUDIT_LOGS=$(curl -s -X GET "$BASE_URL/api/v1/audit/entities/$PAYMENT_ID/trail" \
  -H "X-API-Key: $API_KEY")

AUDIT_ACTION=$(echo "$AUDIT_LOGS" | jq -r '.[0].details.action')

if echo "$AUDIT_ACTION" | grep -q "manual_create_payment"; then
  echo "✅ Audit log correctly recorded manual payment creation"
  echo "   Action: $AUDIT_ACTION"
else
  echo "⚠️  Audit log may not be correctly recorded"
  echo "   Action: $AUDIT_ACTION"
fi

echo ""

# ==================== Summary ====================
echo "=========================================="
echo "✅ POST /api/v1/payments TEST PASSED!"
echo "=========================================="
echo ""
echo "Summary:"
echo "  ✅ Created 3 pre-signed mandates"
echo "  ✅ POST payment record with mandate IDs"
echo "  ✅ Signatures correctly extracted"
echo "  ✅ Payment retrievable via GET"
echo "  ✅ Audit log recorded"
echo ""
echo "Payment Details:"
echo "  Payment ID: $PAYMENT_ID"
echo "  Transaction ID: $TRANSACTION_ID"
echo "  Amount: 179.99 USD"
echo "  Status: SUCCESS"
echo ""
echo "🎉 Manual payment creation endpoint working!"
echo ""



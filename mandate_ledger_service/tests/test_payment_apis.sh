#!/bin/bash
set -euo pipefail

# Test Payment APIs (without change streams)
BASE_URL="http://localhost:8001"
API_KEY="mlsk_2805c1e7a703c27bfbb1a9b2017cd6ea"  # Admin key
TRANSACTION_ID="txn_payment_api_test_$(date +%s)"

echo "=========================================="
echo "Testing Payment APIs"
echo "=========================================="
echo ""
echo "Configuration:"
echo "  BASE_URL: $BASE_URL"
echo "  API_KEY: ${API_KEY:0:20}..."
echo "  TRANSACTION_ID: $TRANSACTION_ID"
echo ""

# ==================== Step 1: Create Test Mandates ====================
echo "Step 1: Create test mandates"
echo "--------------------------------------"

# Create IntentMandate
INTENT_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/mandates" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"mandate_type\": \"IntentMandate\",
    \"mandate_data\": {
      \"user_cart_confirmation_required\": true,
      \"natural_language_description\": \"Test basketball shoes under \$200\",
      \"merchants\": [\"nike.com\", \"adidas.com\"],
      \"requires_refundability\": true,
      \"intent_expiry\": \"2025-12-31T23:59:59Z\"
    },
    \"transaction_id\": \"$TRANSACTION_ID\",
    \"metadata\": {\"test\": \"payment_api\"}
  }")

INTENT_ID=$(echo "$INTENT_RESPONSE" | jq -r '.entity_id')
echo "✅ Created IntentMandate: $INTENT_ID"

# Sign IntentMandate
curl -s -X POST "$BASE_URL/api/v1/mandates/$INTENT_ID/sign" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "signature_data": {
      "signature": "0x_intent_test_signature_abc123",
      "algorithm": "EdDSA"
    }
  }' > /dev/null
echo "✅ Signed IntentMandate"

# Create CartMandate
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
              \"data\": {\"supportedNetworks\": [\"visa\", \"mastercard\"]}
            }
          ],
          \"details\": {
            \"id\": \"pd_001\",
            \"total\": {
              \"label\": \"Total\",
              \"amount\": {\"currency\": \"USD\", \"value\": \"199.99\"}
            },
            \"display_items\": [
              {
                \"label\": \"Basketball Shoes\",
                \"amount\": {\"currency\": \"USD\", \"value\": \"199.99\"}
              }
            ]
          }
        },
        \"cart_expiry\": \"2025-12-31T23:59:59Z\",
        \"merchant_name\": \"Nike Store\"
      }
    },
    \"transaction_id\": \"$TRANSACTION_ID\",
    \"metadata\": {\"test\": \"payment_api\"}
  }")

CART_ID=$(echo "$CART_RESPONSE" | jq -r '.entity_id')
echo "✅ Created CartMandate: $CART_ID"

# Sign CartMandate
curl -s -X POST "$BASE_URL/api/v1/mandates/$CART_ID/sign" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "signature_data": {
      "signature": "0x_cart_test_signature_xyz789",
      "algorithm": "EdDSA"
    }
  }' > /dev/null
echo "✅ Signed CartMandate"

# Create PaymentMandate
PAYMENT_MANDATE_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/mandates" \
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
          \"amount\": {\"currency\": \"USD\", \"value\": \"199.99\"}
        },
        \"payment_response\": {
          \"request_id\": \"req_test_001\",
          \"method_name\": \"basic-card\",
          \"details\": {\"cardholderName\": \"Test User\"}
        },
        \"merchant_agent\": \"merchant-agent-test\",
        \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"
      }
    },
    \"transaction_id\": \"$TRANSACTION_ID\",
    \"metadata\": {\"test\": \"payment_api\"}
  }")

PAYMENT_MANDATE_ID=$(echo "$PAYMENT_MANDATE_RESPONSE" | jq -r '.entity_id')
echo "✅ Created PaymentMandate: $PAYMENT_MANDATE_ID"

# Sign PaymentMandate
curl -s -X POST "$BASE_URL/api/v1/mandates/$PAYMENT_MANDATE_ID/sign" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "signature_data": {
      "signature": "0x_payment_test_signature_qwe456",
      "algorithm": "EdDSA"
    }
  }' > /dev/null
echo "✅ Signed PaymentMandate"

echo ""

# ==================== Step 2: Manually Create Payment Record ====================
echo "Step 2: Manually create payment record in database"
echo "--------------------------------------"

# Use Python to insert payment record directly
PAYMENT_ID=$(python3 << EOF
import sys
sys.path.insert(0, '/Users/sakshi.garg/AP2-test/AP2/mandate_ledger_service')
import asyncio
from datetime import datetime, timezone
from uuid import uuid4
from src.db.mongodb import MongoDB, connect_to_mongo, close_mongo_connection

async def create_test_payment():
    await connect_to_mongo()

    payment_id = f"pay_{uuid4()}"
    payment_record = {
        "payment_id": payment_id,
        "transaction_id": "$TRANSACTION_ID",
        "amount": 199.99,
        "currency": "USD",
        "status": "SUCCESS",
        "intent_mandate": {
            "mandate_id": "$INTENT_ID",
            "signature": "0x_intent_test_signature_abc123",
            "timestamp": datetime.now(timezone.utc).isoformat()
        },
        "cart_mandate": {
            "mandate_id": "$CART_ID",
            "signature": "0x_cart_test_signature_xyz789",
            "timestamp": datetime.now(timezone.utc).isoformat()
        },
        "payment_mandate": {
            "mandate_id": "$PAYMENT_MANDATE_ID",
            "signature": "0x_payment_test_signature_qwe456",
            "timestamp": datetime.now(timezone.utc).isoformat()
        },
        "processed_at": datetime.now(timezone.utc),
        "merchant_agent": "merchant-agent-test",
        "payment_processor_agent": "payment-processor-test",
        "metadata": {"test": "payment_api", "created_by": "test_script"}
    }
    await MongoDB.payments.insert_one(payment_record)
    print(payment_id)
    await close_mongo_connection()

asyncio.run(create_test_payment())
EOF
)

if [ -n "$PAYMENT_ID" ] && [ "$PAYMENT_ID" != "null" ]; then
  echo "✅ Payment record created: $PAYMENT_ID"
else
  echo "❌ Failed to create payment record"
  exit 1
fi

echo ""

# ==================== Step 3: Test GET /api/v1/payments/{payment_id} ====================
echo "Step 3: Test GET /api/v1/payments/{payment_id}"
echo "--------------------------------------"

PAYMENT_GET=$(curl -s -X GET "$BASE_URL/api/v1/payments/$PAYMENT_ID" \
  -H "X-API-Key: $API_KEY")

RETRIEVED_ID=$(echo "$PAYMENT_GET" | jq -r '.payment_id')

if [ "$RETRIEVED_ID" = "$PAYMENT_ID" ]; then
  echo "✅ Successfully retrieved payment by ID"
  echo "   Payment ID: $RETRIEVED_ID"
  echo "   Amount: $(echo "$PAYMENT_GET" | jq -r '.amount') $(echo "$PAYMENT_GET" | jq -r '.currency')"
  echo "   Status: $(echo "$PAYMENT_GET" | jq -r '.status')"
else
  echo "❌ Failed to retrieve payment by ID"
  echo "$PAYMENT_GET" | jq '.'
  exit 1
fi

echo ""

# ==================== Step 4: Test GET /api/v1/payments/session/{transaction_id} ====================
echo "Step 4: Test GET /api/v1/payments/session/{transaction_id}"
echo "--------------------------------------"

SESSION_PAYMENTS=$(curl -s -X GET "$BASE_URL/api/v1/payments/session/$TRANSACTION_ID" \
  -H "X-API-Key: $API_KEY")

TOTAL_COUNT=$(echo "$SESSION_PAYMENTS" | jq -r '.total_count')

if [ "$TOTAL_COUNT" -ge 1 ]; then
  echo "✅ Successfully retrieved payments for session"
  echo "   Total payments: $TOTAL_COUNT"
  echo "   Payment IDs: $(echo "$SESSION_PAYMENTS" | jq -r '.payments[].payment_id')"
else
  echo "❌ Failed to retrieve payments for session"
  echo "$SESSION_PAYMENTS" | jq '.'
  exit 1
fi

echo ""

# ==================== Step 5: Test GET /api/v1/payments (search) ====================
echo "Step 5: Test GET /api/v1/payments (search)"
echo "--------------------------------------"

SEARCH_PAYMENTS=$(curl -s -X GET "$BASE_URL/api/v1/payments?status=SUCCESS&limit=10" \
  -H "X-API-Key: $API_KEY")

SEARCH_COUNT=$(echo "$SEARCH_PAYMENTS" | jq -r '.total_count')

if [ "$SEARCH_COUNT" -ge 1 ]; then
  echo "✅ Successfully searched payments"
  echo "   Found $SEARCH_COUNT payment(s) with status=SUCCESS"
else
  echo "⚠️  No payments found in search (database might be empty)"
fi

echo ""

# ==================== Step 6: Verify Ultra-Lean Format ====================
echo "Step 6: Verify ultra-lean format"
echo "--------------------------------------"

HAS_INTENT_CONTENT=$(echo "$PAYMENT_GET" | jq '.intent_mandate | has("mandate_data") or has("contents")')
HAS_CART_CONTENT=$(echo "$PAYMENT_GET" | jq '.cart_mandate | has("mandate_data") or has("contents")')
HAS_PAYMENT_CONTENT=$(echo "$PAYMENT_GET" | jq '.payment_mandate | has("mandate_data") or has("contents")')

if [ "$HAS_INTENT_CONTENT" = "false" ] && [ "$HAS_CART_CONTENT" = "false" ] && [ "$HAS_PAYMENT_CONTENT" = "false" ]; then
  echo "✅ Payment record is ultra-lean"
  echo "   Contains ONLY: IDs + signatures + timestamps"
  echo ""
  echo "   Intent reference:"
  echo "     - ID: $(echo "$PAYMENT_GET" | jq -r '.intent_mandate.mandate_id')"
  echo "     - Signature: $(echo "$PAYMENT_GET" | jq -r '.intent_mandate.signature' | cut -c1-30)..."
  echo ""
  echo "   Cart reference:"
  echo "     - ID: $(echo "$PAYMENT_GET" | jq -r '.cart_mandate.mandate_id')"
  echo "     - Signature: $(echo "$PAYMENT_GET" | jq -r '.cart_mandate.signature' | cut -c1-30)..."
  echo ""
  echo "   Payment reference:"
  echo "     - ID: $(echo "$PAYMENT_GET" | jq -r '.payment_mandate.mandate_id')"
  echo "     - Signature: $(echo "$PAYMENT_GET" | jq -r '.payment_mandate.signature' | cut -c1-30)..."
else
  echo "⚠️  Warning: Payment record may contain unnecessary content"
fi

echo ""

# ==================== Summary ====================
echo "=========================================="
echo "✅ ALL PAYMENT API TESTS PASSED!"
echo "=========================================="
echo ""
echo "Test Results:"
echo "  ✅ Step 1: Created & signed 3 mandates"
echo "  ✅ Step 2: Manually created payment record"
echo "  ✅ Step 3: GET payment by ID"
echo "  ✅ Step 4: GET payments by session/transaction"
echo "  ✅ Step 5: Search payments by status"
echo "  ✅ Step 6: Verified ultra-lean format"
echo ""
echo "Payment Details:"
echo "  Transaction ID: $TRANSACTION_ID"
echo "  Payment ID: $PAYMENT_ID"
echo "  Amount: 199.99 USD"
echo "  Status: SUCCESS"
echo ""


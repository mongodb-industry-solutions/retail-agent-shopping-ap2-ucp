#!/bin/bash
# Setup script for Mandate Ledger Service integration
# This script loads environment variables from .env file

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/.env"

echo "Setting up Mandate Ledger Service environment variables..."

# Load from .env file if it exists
if [ -f "$ENV_FILE" ]; then
  set -a
  source "$ENV_FILE"
  set +a
else
  echo "⚠️  No .env file found at: $ENV_FILE"
  echo "   Create one from .env.example with your API key"
  exit 1
fi

# Set defaults if not already set
export MANDATE_LEDGER_SERVICE_URL="${MANDATE_LEDGER_SERVICE_URL:-http://localhost:5000}"

# Validate required variables
if [ -z "$MANDATE_LEDGER_API_KEY" ]; then
  echo "❌ Error: MANDATE_LEDGER_API_KEY not set in .env"
  echo "   Get your key from: mandate_ledger_service/api_keys_*.json"
  exit 1
fi

# Show masked key for confirmation
KEY_PREFIX="${MANDATE_LEDGER_API_KEY:0:12}"
echo "✅ Environment variables set:"
echo "   MANDATE_LEDGER_SERVICE_URL value is $MANDATE_LEDGER_SERVICE_URL"
echo "   MANDATE_LEDGER_API_KEY prefix is ${KEY_PREFIX}*** (merchant_agent_dev)"



#!/bin/bash
#
# Test Configuration
#
# Load environment variables and set up test configuration
#

# Base URL for API
export BASE_URL="${BASE_URL:-http://localhost:8001}"

# MongoDB connection (for cleanup script)
export MONGODB_URI="${MONGODB_URI:-mongodb://localhost:27017}"
export MONGODB_DATABASE="${MONGODB_DATABASE:-mandate_ledger}"

# Test configuration
export SKIP_CLEANUP="${SKIP_CLEANUP:-false}"  # Set to 'true' to keep test data
export VERBOSE="${VERBOSE:-false}"             # Set to 'true' for detailed output

# Load API key from environment or files
if [ -z "${API_KEY:-}" ]; then
    # Try to find api_keys_*.json file (from setup script)
    API_KEYS_FILE=$(ls -t ../api_keys_*.json 2>/dev/null | head -1)
    if [ -n "$API_KEYS_FILE" ] && [ -f "$API_KEYS_FILE" ] && command -v jq &> /dev/null; then
        # Use admin-user key which has admin:write permission
        export API_KEY=$(cat "$API_KEYS_FILE" | jq -r '.keys[] | select(.agent_id == "admin-user") | .api_key' 2>/dev/null)
        if [ -z "${API_KEY:-}" ] || [ "$API_KEY" == "null" ]; then
            # Fallback to first key
            export API_KEY=$(cat "$API_KEYS_FILE" | jq -r '.keys[0].api_key' 2>/dev/null)
        fi
        if [ -n "${API_KEY:-}" ] && [ "$API_KEY" != "null" ]; then
            echo "✅ Loaded API key from: $(basename "$API_KEYS_FILE")"
        fi
    fi

    # Fallback to .env file
    if [ -z "${API_KEY:-}" ] && [ -f "../.env" ]; then
        export API_KEY=$(grep BOOTSTRAP_ADMIN_KEY ../.env | cut -d= -f2)
    fi

    # Last resort: current directory .env
    if [ -z "${API_KEY:-}" ] && [ -f ".env" ]; then
        export API_KEY=$(grep BOOTSTRAP_ADMIN_KEY .env | cut -d= -f2)
    fi
fi

# Verify required variables
if [ -z "${API_KEY:-}" ]; then
    echo "ERROR: API_KEY not set!"
    echo ""
    echo "Options:"
    echo "  1. Export API_KEY environment variable"
    echo "  2. Run setup script: python scripts/setup_agent_keys.py"
    echo "  3. Set BOOTSTRAP_ADMIN_KEY in .env"
    exit 1
fi

echo "Test Configuration:"
echo "  BASE_URL: $BASE_URL"
echo "  API_KEY: ${API_KEY:0:12}..."
echo "  SKIP_CLEANUP: $SKIP_CLEANUP"
echo ""


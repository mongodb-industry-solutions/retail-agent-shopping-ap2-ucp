#!/bin/bash

# UCP + AP2 Flow Demo Runner
# This script starts both the UCP Merchant Server and the Shopper Agent

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   UCP + AP2 Integration Demo${NC}"
echo -e "${BLUE}========================================${NC}"

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
AGENTS_DIR="$SCRIPT_DIR/shopper_agent"
LOG_DIR="$REPO_ROOT/.logs"

# Check we're in the right place
if [ ! -d "$SCRIPT_DIR/merchant_server" ]; then
    echo -e "${RED}Error: merchant_server directory not found.${NC}"
    echo "Please run this script from the repository root:"
    echo "  bash example/ucp_flow/run.sh"
    exit 1
fi

# Load environment variables
if [ -f "$REPO_ROOT/.env" ]; then
    echo -e "${GREEN}Loading .env from repository root...${NC}"
    set -a
    source "$REPO_ROOT/.env"
    set +a
fi

if [ -f "$SCRIPT_DIR/.env" ]; then
    echo -e "${GREEN}Loading .env from ucp_flow directory...${NC}"
    set -a
    source "$SCRIPT_DIR/.env"
    set +a
fi

# Check required environment variables
USE_VERTEXAI=$(printf "%s" "${GOOGLE_GENAI_USE_VERTEXAI}" | tr '[:upper:]' '[:lower:]')
if [ -z "${GOOGLE_API_KEY}" ] && [ "${USE_VERTEXAI}" != "true" ]; then
    echo -e "${RED}Error: GOOGLE_API_KEY not set.${NC}"
    echo "Set it in .env file or as environment variable."
    exit 1
fi

echo -e "${GREEN}✓ Google API Key configured${NC}"

# Check ledger configuration
if [ -z "${MANDATE_LEDGER_API_KEY}" ]; then
    echo -e "${YELLOW}Warning: MANDATE_LEDGER_API_KEY not set.${NC}"
    echo "The merchant server needs this to write to the AP2 Ledger."
    echo "Set it in .env file or run the setup script first."
fi

LEDGER_URL="${MANDATE_LEDGER_SERVICE_URL:-http://localhost:5000}"
echo -e "${GREEN}✓ Ledger URL: $LEDGER_URL${NC}"

# Setup Python environment
echo ""
echo -e "${BLUE}Setting up Python environment...${NC}"

cd "$REPO_ROOT"

if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    uv venv --python 3.12
fi

# Activate venv
case "$OSTYPE" in
    msys* | cygwin*)
        source .venv/Scripts/activate
        ;;
    *)
        source .venv/bin/activate
        ;;
esac

echo "Installing dependencies..."
uv pip install -e . --quiet
uv pip install fastapi uvicorn --quiet

# Sync packages
echo "Syncing packages..."
uv sync --package ap2-samples --quiet 2>/dev/null || true

# Create log directory
mkdir -p "$LOG_DIR"
rm -f "$LOG_DIR"/ucp_*.log

# Cleanup function
pids=()
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down...${NC}"
    if [ ${#pids[@]} -ne 0 ]; then
        kill "${pids[@]}" 2>/dev/null
        wait "${pids[@]}" 2>/dev/null
    fi
    echo -e "${GREEN}Cleanup complete.${NC}"
}
trap cleanup EXIT

# Export UCP merchant URL for shopper agent
export UCP_MERCHANT_URL="http://localhost:8004"

echo ""
echo -e "${BLUE}Starting services...${NC}"

# Start Merchant Server
echo -e "  ${GREEN}→${NC} Starting UCP Merchant Server (port 8004)..."
cd "$SCRIPT_DIR"
PYTHONPATH="$REPO_ROOT/example/src:$SCRIPT_DIR" \
    uvicorn merchant_server.server:app \
    --host 0.0.0.0 \
    --port 8004 \
    --reload \
    > "$LOG_DIR/ucp_merchant.log" 2>&1 &
pids+=($!)

# Wait for merchant to start
sleep 2

# Check if merchant is running
if curl -s "http://localhost:8004/health" > /dev/null 2>&1; then
    echo -e "  ${GREEN}✓${NC} Merchant Server running at http://localhost:8004"
else
    echo -e "  ${YELLOW}⚠${NC} Merchant Server may still be starting..."
fi

cd "$REPO_ROOT"

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}  UCP + AP2 Demo Ready!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "  Merchant Server:  http://localhost:8004"
echo "  Discovery:        http://localhost:8004/.well-known/ucp.json"
echo ""
echo "  Logs: $LOG_DIR/ucp_merchant.log"
echo ""
echo -e "${BLUE}Starting Shopper Agent (port 8000)...${NC}"
echo "  Open: http://localhost:8000/dev-ui"
echo "  Select: ucp_shopper_agent"
echo ""
echo -e "${YELLOW}Try saying: \"I want to buy a coffee maker\"${NC}"
echo ""
echo "Press Ctrl+C to stop all services."
echo ""

# Start the ADK web interface (foreground)
PYTHONPATH="$REPO_ROOT/example/src:$SCRIPT_DIR" \
    uv run --no-sync --package ap2-samples \
    adk web --host 0.0.0.0 "$SCRIPT_DIR"


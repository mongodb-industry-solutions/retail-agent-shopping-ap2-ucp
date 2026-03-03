#!/bin/bash

# Backend Startup Script with A2A Agents
# This script sets up and starts the backend service with integrated A2A agents

set -e

# Configuration
BACKEND_PORT=8000
LOG_DIR=".logs"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting Backend Service with A2A Agents${NC}"

# Check if we're in the backend directory
if [ ! -f "main.py" ]; then
  echo -e "${RED}Error: Please run this script from the backend directory${NC}"
  echo "Expected to find main.py in current directory"
  exit 1
fi

# Source environment variables if .env exists
if [ -f ../.env ]; then
  echo -e "${YELLOW}Loading environment variables from ../.env${NC}"
  set -a
  source ../.env
  set +a
fi

# Source Mandate Ledger Service environment variables
if [ -f "../example/card_flow/setup_ledger_env.sh" ]; then
  echo -e "${YELLOW}Loading Mandate Ledger Service configuration...${NC}"
  source "../example/card_flow/setup_ledger_env.sh"
fi

# Check required environment variables
USE_VERTEXAI=$(printf "%s" "${GOOGLE_GENAI_USE_VERTEXAI}" | tr '[:upper:]' '[:lower:]')
if [ -z "${GOOGLE_API_KEY}" ] && [ "${USE_VERTEXAI}" != "true" ]; then
  echo -e "${RED}⚠️  Warning: GOOGLE_API_KEY not set and GOOGLE_GENAI_USE_VERTEXAI is not true${NC}"
  echo "Some agent functionality may not work properly."
  echo "Set GOOGLE_API_KEY or GOOGLE_GENAI_USE_VERTEXAI=true to use Vertex AI with ADC."
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
  echo -e "${RED}Error: Virtual environment not found${NC}"
  echo "Please run 'make uv_init' and 'make uv_sync' first"
  exit 1
fi

# Activate virtual environment
echo -e "${YELLOW}Activating Python virtual environment...${NC}"
source .venv/bin/activate

# Ensure dependencies are synced
echo -e "${YELLOW}Syncing dependencies...${NC}"
uv sync

# Create log directory
mkdir -p "$LOG_DIR"

echo -e "${GREEN}📡 Starting Backend Service on port ${BACKEND_PORT}${NC}"
echo -e "${YELLOW}The following services will be started automatically:${NC}"
echo "  - Unified Backend + Shopping Agent API (port 8000)"
echo "  - Merchant Agent (port 8001)"
echo "  - Credentials Provider Agent (port 8002)" 
echo "  - Merchant Payment Processor Agent (port 8003)"
echo "  - Auditor Agent (port 8004)"
echo ""
echo -e "${YELLOW}API endpoints will be available at:${NC}"
echo "  - Backend API: http://localhost:${BACKEND_PORT}"
echo "  - Shopping Agent Chat: http://localhost:${BACKEND_PORT}/api/v1/shopping/chat"
echo "  - Product Search: http://localhost:${BACKEND_PORT}/api/v1/shopping/search"
echo "  - Cart Update: http://localhost:${BACKEND_PORT}/api/v1/shopping/cart/update"
echo "  - Payment: http://localhost:${BACKEND_PORT}/api/v1/shopping/payment/initiate"
echo "  - Health Check: http://localhost:${BACKEND_PORT}/health"
echo "  - API Documentation: http://localhost:${BACKEND_PORT}/docs"
echo ""
echo -e "${YELLOW}Agent logs will be stored in: ${LOG_DIR}${NC}"
echo ""
echo -e "${GREEN}Press Ctrl+C to stop all services${NC}"
echo ""

# Start the backend service with uvicorn
# The agents will be started automatically via the FastAPI lifespan manager
uv run uvicorn main:app --host 0.0.0.0 --port "${BACKEND_PORT}" --reload
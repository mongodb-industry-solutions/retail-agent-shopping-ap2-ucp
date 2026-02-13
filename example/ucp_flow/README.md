# UCP + AP2 Integration Demo

This example demonstrates how the **Universal Commerce Protocol (UCP)** and **Agent Payment Protocol (AP2)** work together.

## Overview

| Protocol | Role |
|----------|------|
| **UCP** | Commerce layer - REST APIs for product discovery, checkout, orders |
| **AP2** | Trust layer - mandate signing, immutable ledger, audit trail |

## Architecture

```
┌─────────────────────┐                    ┌─────────────────────┐
│   Shopper Agent     │      UCP REST      │   Merchant Server   │
│   (ADK)             │◄──────────────────►│   (FastAPI)         │
│                     │                    │                     │
│   - AI reasoning    │   /.well-known/    │   - Product catalog │
│   - User interaction│   /checkout        │   - Checkout logic  │
│   - NO MongoDB      │   /complete        │   - AP2 Ledger ✓    │
└─────────────────────┘                    └──────────┬──────────┘
                                                      │
                                                      ▼
                                           ┌─────────────────────┐
                                           │  AP2 Mandate Ledger │
                                           │  Service            │
                                           └─────────────────────┘
```

## Key Differences from Card Flow

| Aspect | Card Flow | UCP Flow |
|--------|-----------|----------|
| Shopper ↔ Merchant | A2A protocol | **REST/HTTP (UCP)** |
| Merchant implementation | ADK agent | **FastAPI server** |
| Discovery | agent.json | **/.well-known/ucp.json** |
| AP2 Ledger integration | Same | Same |

## Components

### 1. Merchant Server (FastAPI)
- `/.well-known/ucp.json` - UCP capability discovery
- `POST /api/checkout` - Create checkout with AP2 merchant signature
- `POST /api/checkout/{id}/complete` - Complete checkout, write mandates to ledger

### 2. Shopper Agent (ADK)
- AI-powered shopping assistant
- Uses UCP REST endpoints (not A2A)
- Signs mandates locally, merchant writes to ledger

### 3. Auditor Agent (ADK)
- Verifies transactions in the AP2 Mandate Ledger
- Demonstrates immutability and audit trail
- Can lookup by `payment_id`, `transaction_id`, or `order_id` (same as transaction_id)

## Setup

### Prerequisites
- Python 3.12+
- AP2 Mandate Ledger Service running on port 5000
- Google API Key (for ADK agent)

### Environment Variables

Create `.env` in `example/ucp_flow/`:
MANDATE_LEDGER_API_KEY is your mlsk_merchant_key_from_setup

```bash
GOOGLE_API_KEY=
MANDATE_LEDGER_SERVICE_URL=http://localhost:5000
MANDATE_LEDGER_API_KEY=
```

## Running

From repository root:

```bash
bash example/ucp_flow/run.sh
```

Or run each component separately:

1. **Start Merchant Server** (port 8004):
   ```bash
   cd example/ucp_flow
   uvicorn merchant_server.server:app --port 8004 --reload
   ```

2. **Start Shopper Agent** (port 8000):
   ```bash
   uv run --package ap2-samples adk web example/ucp_flow/shopper_agent
   ```

## Usage

### Shopping Flow

1. Open http://localhost:8000/dev-ui
2. Select `shopper_agent`
3. Say: "I want to buy a coffee maker"
4. Follow the checkout flow
5. Note the `order_id` (same as `transaction_id`) from the receipt

### Auditing Flow

1. After completing a purchase, select `auditor_agent`
2. Say: "Audit transaction txn_ucp_checkout_xxx" (use the order_id from receipt)
3. Or: "Verify payment pay_xxx"
4. Try: "Delete this payment" to see immutability in action

## UCP Capability Discovery

The merchant advertises AP2 support via `/.well-known/ucp.json`:

```json
{
  "name": "Demo UCP Merchant",
  "ucp_version": "2026-01-11",
  "capabilities": [
    {"name": "dev.ucp.shopping.checkout", "version": "2026-01-11"},
    {"name": "dev.ucp.shopping.ap2_mandate", "version": "2026-01-11"}
  ]
}
```

When the shopper agent discovers `ap2_mandate` capability, it knows the merchant supports:
- Signed merchant authorization on checkout
- Mandate-based payment authorization
- Immutable audit trail via AP2 Ledger

## Documentation

- [UCP + AP2 Integration Guide](../../docs/UCP_AP2_INTEGRATION.md)
- [AP2 Mandate Ledger API](../../mandate_ledger_service/docs/API_REFERENCE.md)


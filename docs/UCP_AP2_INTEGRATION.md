# Understanding UCP + AP2 Integration

This document explains how the **Universal Commerce Protocol (UCP)** and **Agent Payment Protocol (AP2)** work together, and how the AP2 Mandate Ledger Service integrates with UCP-based commerce flows.

---

## Table of Contents

1. [Overview: UCP vs AP2](#overview-ucp-vs-ap2)
2. [What is `/.well-known/ucp.json`?](#what-is-well-knownucpjson)
3. [What is `dev.ucp.shopping.ap2_mandate`?](#what-is-devucpshoppingap2_mandate)
4. [How Capability Negotiation Works](#how-capability-negotiation-works)
5. [Step-by-Step Flow](#step-by-step-flow)
6. [Mapping to Card Flow](#mapping-to-card-flow)
7. [Implementation Example](#implementation-example)

---

## Overview: UCP vs AP2

| Aspect | UCP (Universal Commerce Protocol) | AP2 (Agent Payment Protocol) |
|--------|-----------------------------------|------------------------------|
| **Focus** | Commerce flow (discovery, checkout, orders) | Payment authorization & audit trail |
| **Communication** | REST APIs / OpenAPI | A2A protocol or REST with extensions |
| **Key Concepts** | Checkout sessions, order lifecycle, capability discovery | Mandates (Intent, Cart, Payment), signatures, immutable ledger |
| **Value Prop** | Standardized commerce interactions between agents | Immutable ledger, legal attestation, non-repudiation |

**They're complementary**: 
- **UCP** defines *how* agents discover and transact (the commerce protocol)
- **AP2** provides *proof* of authorization and an immutable audit trail (the trust layer)

---

## What is `/.well-known/ucp.json`?

### The Concept

Think of it like a **business card for your merchant server** that any shopping agent can automatically discover.

When an AI shopping agent wants to buy something from "Amazon" or "Ulta", it needs to know:
- What can this merchant do? (product search, checkout, payments?)
- What payment methods do they accept?
- Do they support AP2 mandates for secure transactions?

Instead of hardcoding this, UCP uses a **standard discovery URL**.

### How It Works

```
Shopper Agent thinks: "I want to shop at amazon.example.com"
                           ↓
             Fetches: https://amazon.example.com/.well-known/ucp.json
                           ↓
             Gets back: Merchant's capabilities, endpoints, keys
```

### Example File

```json
{
  "name": "Amazon Demo Store",
  "ucp_version": "2026-01-11",
  
  "services": {
    "shopping": {
      "transport": "rest",
      "endpoint": "https://amazon.example.com/api/ucp"
    }
  },
  
  "capabilities": [
    {
      "name": "dev.ucp.shopping.checkout",
      "version": "2026-01-11"
    },
    {
      "name": "dev.ucp.shopping.ap2_mandate",
      "version": "2026-01-11",
      "extends": "dev.ucp.shopping.checkout"
    }
  ],
  
  "payment_handlers": ["CARD", "GOOGLE_PAY"],
  
  "signing_keys": [
    {
      "kid": "amazon-key-2026",
      "kty": "EC",
      "crv": "P-256",
      "x": "abc123...",
      "y": "def456..."
    }
  ]
}
```

### Why This Matters

| Benefit | Description |
|---------|-------------|
| **Automatic Discovery** | Shopping agents don't need to know each merchant's API in advance |
| **Capability Negotiation** | Agent can check "does this merchant support AP2 mandates?" before shopping |
| **Signature Verification** | Public keys for verifying the merchant's signatures |

---

## What is `dev.ucp.shopping.ap2_mandate`?

### The Concept

This is the **name of a capability** (like a feature flag) that says: *"This merchant supports AP2 mandates for secure, auditable transactions."*

The naming convention `dev.ucp.shopping.ap2_mandate` means:
- `dev.ucp` → UCP specification namespace
- `shopping` → The shopping service
- `ap2_mandate` → The AP2 mandate extension feature

### Why It Exists

**Without this capability (basic UCP):**
```
Shopper: "I want to buy this"
Merchant: "OK, pay me $50"
Shopper: "Here's my card"
Merchant: "Done!"
                    ↓
         No cryptographic proof of what was agreed
```

**With `ap2_mandate` capability (UCP + AP2):**
```
Shopper: "I want to buy this"
Merchant: "OK, here's the offer. I SIGN it: 🔐"
Shopper: "I agree. I SIGN it too: 🔐"  
Merchant: "Here's payment authorization. I SIGN: 🔐"
Shopper: "I authorize payment. I SIGN: 🔐"
                    ↓
         All signatures stored in AP2 Ledger = PROOF
```

### When to Use It

- **Autonomous agent scenarios**: When AI agents are making purchases on behalf of users
- **Non-repudiable proof**: Legal evidence that the user agreed to specific terms
- **Fraud reduction**: Tokens/payment authorizations are only valid for one checkout hash, preventing replay or tampering

---

## How Capability Negotiation Works

### Step 1: Discovery

```
Shopper Agent                         Merchant Server
     │                                      │
     │── GET /.well-known/ucp.json ────────►│
     │                                      │
     │◄─── JSON with capabilities ──────────│
     │     including "ap2_mandate"          │
```

### Step 2: Capability Matching

```
Shopper Agent checks:

  My capabilities:          Merchant capabilities:
  ✓ checkout                ✓ checkout
  ✓ ap2_mandate             ✓ ap2_mandate    ← MATCH!
  ✓ order                   ✓ order

  Result: AP2 mandate flow is ACTIVATED
```

### Step 3: Checkout with AP2 Signatures

```
Shopper Agent                         Merchant Server
     │                                      │
     │── POST /checkout ───────────────────►│
     │   {items: [...]}                     │
     │                                      │
     │◄─── checkout response ───────────────│
     │     {                                │
     │       cart: {...},                   │
     │       ap2: {                         │
     │         merchant_authorization: "eyJ..." ← SIGNED!
     │       }                              │
     │     }                                │
```

### Step 4: User Consent & Mandate Creation

```
Shopper Agent (locally, no network):

  1. Shows cart to user
  2. User says "Yes, buy this"
  3. Agent creates checkout_mandate (SIGNS it)
  4. Agent creates payment_mandate (SIGNS it)

  These mandates contain:
  - The merchant's signature (from step 3)
  - The shopper's signature (just created)
  - The exact terms both agreed to
```

### Step 5: Complete Checkout (Merchant writes to AP2 Ledger)

```
Shopper Agent                         Merchant Server
     │                                      │
     │── POST /complete_checkout ──────────►│
     │   {                                  │
     │     ap2: {                           │
     │       checkout_mandate: "eyJ...",    │
     │     },                               │
     │     payment_data: {                  │
     │       token: "eyJ..." (payment_mandate)
     │     }                                │
     │   }                                  │
     │                                      │
     │                          ┌───────────┴───────────┐
     │                          │ Merchant:             │
     │                          │ 1. Verify signatures  │
     │                          │ 2. Write mandates to  │
     │                          │    AP2 Ledger ────────┼──► 📚
     │                          │ 3. Process payment    │
     │                          │ 4. Create payment rec │
     │                          └───────────┬───────────┘
     │                                      │
     │◄─── {order_id, receipt} ─────────────│
```

---

## Step-by-Step Flow

### Complete Flow Diagram

```
┌─────────────────────┐                    ┌─────────────────────┐
│   Consumer Agent    │      UCP REST      │   Merchant Agent    │
│   (Shopper)         │◄──────────────────►│   (Amazon/Ulta)     │
│                     │   /checkout        │                     │
│   NO MongoDB        │   /complete        │   HAS AP2 Ledger    │
│   NO AP2 Client     │                    │   Integration       │
└─────────────────────┘                    └──────────┬──────────┘
                                                      │
                                                      │ AP2 API
                                                      ▼
                                           ┌─────────────────────┐
                                           │  AP2 Mandate Ledger │
                                           │  Service (MongoDB)  │
                                           │                     │
                                           │  Hosted by Merchant │
                                           │  or as SaaS         │
                                           └─────────────────────┘
```

### Key Insight: Merchant-Centric Architecture

- **Consumer/Shopper** only speaks **UCP** (REST/HTTP) - no database, no ledger client
- **Merchant** handles all AP2 Ledger writes - they have the infrastructure
- The merchant writes mandates on behalf of the transaction, signed by both parties

### Detailed Flow

| Step | Actor | Action | AP2 Ledger |
|------|-------|--------|------------|
| 1 | Shopper | Discovers merchant via `/.well-known/ucp.json` | - |
| 2 | Shopper | Sends checkout request with items | - |
| 3 | Merchant | Returns cart + `merchant_authorization` signature | - |
| 4 | Shopper | User consents, creates `checkout_mandate` (signed) | - |
| 5 | Shopper | Creates `payment_mandate` with payment method (signed) | - |
| 6 | Shopper | Sends `complete_checkout` with both mandates | - |
| 7 | Merchant | Verifies all signatures | - |
| 8 | Merchant | Writes CartMandate to ledger | ✅ Created |
| 9 | Merchant | Writes PaymentMandate to ledger | ✅ Created |
| 10 | Merchant | Processes payment | - |
| 11 | Merchant | Creates payment record in ledger | ✅ Created |
| 12 | Merchant | Returns order confirmation | - |

---

## Mapping to Card Flow

The beautiful part - **the card_flow example already implements AP2!**

| UCP + AP2 Mandate Concept | Card Flow Equivalent |
|---------------------------|----------------------|
| `/.well-known/ucp.json` | `agent.json` files (A2A agent cards) |
| `merchant_authorization` signature | `cart_mandate.merchant_authorization` |
| `checkout_mandate` (shopper signs cart) | `cart_signature` from Shopping Agent |
| `payment_mandate` | `PaymentMandate` signed by Shopping Agent |
| Merchant writes to ledger | `MandateLedgerClient.create_mandate()` |

**The AP2 pattern is already implemented - just wrapped in A2A protocol instead of UCP REST.**

---

## Implementation Example

### Merchant Server (FastAPI with UCP + AP2)

```python
from fastapi import FastAPI
from common.mandate_ledger_client import MandateLedgerClient
import os

app = FastAPI()

# Initialize AP2 Ledger Client
ledger = MandateLedgerClient(
    base_url=os.getenv("MANDATE_LEDGER_SERVICE_URL"),
    api_key=os.getenv("MANDATE_LEDGER_API_KEY"),
    agent_id="amazon_merchant",
    agent_type="merchant-agent"
)

# ============ STEP 1: Discovery ============
@app.get("/.well-known/ucp.json")
async def ucp_profile():
    """
    Any shopping agent can fetch this to discover our capabilities.
    """
    return {
        "name": "Amazon Demo Merchant",
        "ucp_version": "2026-01-11",
        "capabilities": [
            {"name": "dev.ucp.shopping.checkout", "version": "2026-01-11"},
            {"name": "dev.ucp.shopping.ap2_mandate", "version": "2026-01-11"}
        ],
        "services": {
            "shopping": {
                "transport": "rest",
                "endpoint": "/api/ucp"
            }
        },
        "signing_keys": [get_merchant_public_key()]
    }


# ============ STEP 3: Checkout with Merchant Signature ============
@app.post("/api/ucp/checkout")
async def create_checkout(request: CheckoutRequest):
    """
    Create checkout session with AP2 merchant authorization.
    """
    cart = build_cart(request.items)
    
    # Sign the cart (same as card_flow merchant_authorization!)
    merchant_signature = sign_with_merchant_key(cart)
    
    return {
        "checkout_id": generate_id(),
        "cart": cart,
        "ap2": {
            "merchant_authorization": merchant_signature
        }
    }


# ============ STEP 5: Complete Checkout ============
@app.post("/api/ucp/checkout/{checkout_id}/complete")
async def complete_checkout(checkout_id: str, request: CompleteRequest):
    """
    Receive signed mandates from shopper and write to AP2 Ledger.
    """
    checkout_mandate = request.ap2.checkout_mandate
    payment_mandate = request.payment_data.token
    
    # Verify signatures...
    
    # Write to AP2 Ledger - EXACTLY like card_flow!
    await ledger.create_mandate(
        mandate_type="CartMandate",
        mandate_data=checkout_mandate,
        initial_signatures=[shopper_sig, merchant_sig],
        initial_status="signed"
    )
    
    await ledger.create_mandate(
        mandate_type="PaymentMandate",
        mandate_data=payment_mandate,
        initial_signatures=[shopper_payment_sig],
        initial_status="authorized"
    )
    
    # Process payment & create payment record
    await ledger.create_payment(
        transaction_id=checkout_id,
        intent_mandate_id=intent_id,
        cart_mandate_id=cart_id,
        payment_mandate_id=payment_id,
        amount=amount,
        currency="USD",
        status="SUCCESS",
        merchant_agent="amazon_merchant",
        payment_processor_agent="amazon_payments"
    )
    
    return {"order_id": order_id, "receipt": receipt}
```

### Shopper Agent (Pure UCP, No AP2 Ledger)

```python
import httpx
import jwt

MERCHANT_URL = "http://localhost:8004"

async def discover_merchant():
    """Fetch merchant capabilities via UCP discovery."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{MERCHANT_URL}/.well-known/ucp.json")
        profile = resp.json()
        
        # Check if merchant supports AP2 mandates
        supports_ap2 = any(
            cap["name"] == "dev.ucp.shopping.ap2_mandate" 
            for cap in profile["capabilities"]
        )
        return profile, supports_ap2


async def checkout(items: list, private_key: str):
    """Create checkout - merchant will return signed cart."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{MERCHANT_URL}/api/ucp/checkout",
            json={"items": items}
        )
        return resp.json()  # Contains cart + ap2.merchant_authorization


def create_checkout_mandate(checkout_response: dict, private_key: str) -> str:
    """
    User consents - create signed checkout mandate.
    This combines merchant's signature with shopper's consent.
    """
    return jwt.encode({
        "cart": checkout_response["cart"],
        "merchant_authorization": checkout_response["ap2"]["merchant_authorization"],
        "action": "consent_to_checkout"
    }, private_key, algorithm="RS256")


def create_payment_mandate(checkout_mandate: str, payment_method: dict, private_key: str) -> str:
    """Create signed payment authorization."""
    return jwt.encode({
        "checkout_mandate_ref": hash(checkout_mandate),
        "payment_method": payment_method,
        "action": "authorize_payment"
    }, private_key, algorithm="RS256")


async def complete_checkout(checkout_id: str, checkout_mandate: str, payment_mandate: str):
    """Send signed mandates to merchant - they write to AP2 Ledger."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{MERCHANT_URL}/api/ucp/checkout/{checkout_id}/complete",
            json={
                "ap2": {"checkout_mandate": checkout_mandate},
                "payment_data": {"token": payment_mandate}
            }
        )
        return resp.json()  # Order confirmation
```

---

## Summary

| Concept | What It Is | Analogy |
|---------|-----------|---------|
| `/.well-known/ucp.json` | Discovery endpoint | "Business card" for your merchant |
| `dev.ucp.shopping.ap2_mandate` | Capability name | "Feature flag" saying you support AP2 |
| Capability Negotiation | Both parties check compatibility | "We both speak AP2? Great, let's use it!" |
| `merchant_authorization` | Merchant's signature on cart | Same as card_flow |
| `checkout_mandate` / `payment_mandate` | Shopper's signed agreements | Same as card_flow |
| Merchant writes to AP2 Ledger | Immutable audit trail | **Already implemented!** |

---

## References

- [UCP Samples Repository](https://github.com/Universal-Commerce-Protocol/samples)
- [UCP Python SDK](https://github.com/Universal-Commerce-Protocol/python-sdk)


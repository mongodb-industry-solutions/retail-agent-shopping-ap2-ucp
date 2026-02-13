# Bootstrap Authentication Setup Guide

## Overview

Bootstrap authentication solves the **chicken-and-egg problem**: you need an API key to create API keys!

This guide explains how to use the bootstrap mechanism to create your first API keys.

---

## The Problem

```
┌─────────────────────────────────────────────────┐
│  To Create an API Key...                        │
│  You need to call: POST /api/v1/auth/api-keys  │
│                                                 │
│  But this endpoint requires authentication!     │
│  You must provide an existing API key.          │
│                                                 │
│  But you don't have any API keys yet...        │
│  because this is the first time running!       │
└─────────────────────────────────────────────────┘
```

## The Solution: Bootstrap Admin Key

A **bootstrap admin key** is a special pre-configured password that:
1. ✅ Bypasses database authentication checks
2. ✅ Grants temporary admin privileges
3. ✅ Allows creating the first "real" API keys
4. ✅ Should be disabled after initial setup

---

## Setup Steps

### Step 1: Configure Bootstrap Key

Your `.env` file should have these settings:
BOOTSTRAP_ADMIN_KEY value is your secret bootstrap key
```bash
# Bootstrap Authentication (Development Only)
BOOTSTRAP_ADMIN_KEY=
ENABLE_BOOTSTRAP_AUTH=true
```

**Security Note:** Use a strong, random key. Generate one with:
```bash
openssl rand -hex 32
```

### Step 2: Start the Service

```bash
cd mandate_ledger_service
source .venv/bin/activate
uvicorn src.main:app --reload --host 0.0.0.0 --port 5000
```

Verify it's running:
```bash
curl http://localhost:5000/api/v1/health
```

### Step 3: Run the Setup Script

The setup script will create API keys for agents that interact with the ledger:

```bash
cd mandate_ledger_service
PYTHONPATH=. python3 scripts/setup_agent_keys.py
```

This creates keys for:
- ✅ **merchant_agent_dev** - Read/Write mandates and payments
- ✅ **auditor_agent_dev** - Read-only for compliance verification
- ✅ **admin-user** - Full access for management

**Note:** Shopping Agent, Credentials Provider, and Payment Processor do NOT
need API keys. They communicate via A2A protocol and don't access the ledger directly.
Only the Merchant Agent writes to the ledger on behalf of the entire transaction flow.

**AUTOMATIC BACKUP:** The script automatically saves all API keys to a timestamped JSON file:
```
api_keys_20251118_143052.json
```

**File Features:**
- ✅ All keys in one secure file
- ✅ Timestamped for easy tracking
- ✅ Permissions set to 600 (owner read/write only)
- ✅ Protected by `.gitignore` (won't be committed)
- ✅ Includes key metadata (agent_id, scopes, expiration)

**Security:** The JSON file permissions are set to 600 (owner read/write only).
Keep this file secure and do not commit it to git (it's in `.gitignore`).

### Step 4: Configure the Merchant Agent

Create `.env` file for the card flow example:

**example/card_flow/.env:**
```bash
# Mandate Ledger Service
MANDATE_LEDGER_SERVICE_URL=http://localhost:5000
MANDATE_LEDGER_API_KEY value is mlsk_<merchant_agent_key_from_setup>

# Google AI (for ADK agents)
GOOGLE_API_KEY=
GOOGLE_GENAI_USE_VERTEXAI=true
```

**Note:** Only the Merchant Agent needs a ledger API key. Other agents
communicate via A2A and don't access the ledger directly.

### Step 5: Disable Bootstrap (Production)

**After creating all keys**, disable bootstrap for security:

Edit `mandate_ledger_service/.env`:
```bash
ENABLE_BOOTSTRAP_AUTH=false
```

Restart the service:
```bash
# Press Ctrl+C to stop
uvicorn src.main:app --reload --host 0.0.0.0 --port 5000
```

Now only real API keys from the database will work!

---

## Manual API Key Creation

If you prefer to create keys manually (without the script):

```bash
# Create merchant agent key
curl -X POST http://localhost:5000/api/v1/auth/api-keys \
  -H "Authorization: Bearer YOUR_BOOTSTRAP_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "merchant_agent_dev",
    "agent_type": "merchant-agent",
    "scopes": ["mandate:read", "mandate:write", "payment:read", "payment:write", "audit:read"],
    "expires_in_days": 365,
    "metadata": {
      "description": "Merchant agent - writes mandates and payments to ledger"
    }
  }'

# Save the returned api_key!
```

---

## Testing Your Setup

### Test 1: Verify Bootstrap Works

```bash
# Should return 200 OK with agent keys
curl -X GET http://localhost:5000/api/v1/auth/api-keys \
  -H "Authorization: Bearer YOUR_BOOTSTRAP_KEY"
```

### Test 2: Verify Merchant Agent Key Works

```bash
# Should return 200 OK (may be empty if no mandates yet)
curl -X GET "http://localhost:5000/api/v1/mandates/transaction/test" \
  -H "X-API-Key: mlsk_<your_merchant_agent_key>"
```

### Test 3: Verify Bootstrap is Disabled (After Step 5)

```bash
# Should return 401 Unauthorized after disabling
curl -X GET http://localhost:5000/api/v1/auth/api-keys \
  -H "Authorization: Bearer YOUR_BOOTSTRAP_KEY"
```

---

## Security Best Practices

### Development
- ✅ Use bootstrap key for initial setup
- ✅ Create all needed API keys immediately
- ✅ Save API keys securely (password manager, secrets vault)
- ✅ Disable bootstrap after setup

### Production
- ❌ **NEVER leave bootstrap enabled in production**
- ✅ Use strong, random bootstrap key (if needed for deployment)
- ✅ Disable immediately after deployment
- ✅ Rotate API keys regularly
- ✅ Monitor for unauthorized access attempts
- ✅ Set expiration dates on non-admin keys

---

## Troubleshooting

### Problem: "Authentication required"

**Cause:** Bootstrap key not matching or bootstrap disabled.

**Solution:**
1. Check `.env` has `ENABLE_BOOTSTRAP_AUTH` set to `true`
2. Verify `BOOTSTRAP_ADMIN_KEY` matches what you're sending
3. Restart the service after changing `.env`

### Problem: "Invalid API key" after creating keys

**Cause:** Using bootstrap key instead of real key.

**Solution:** Use the `api_key` from the creation response, not the bootstrap key.

### Problem: Can't disable bootstrap, need to create more keys

**Solution:** Re-enable bootstrap temporarily:
```bash
# Edit .env
ENABLE_BOOTSTRAP_AUTH=true

# Restart service
# Create new keys
# Disable bootstrap again
ENABLE_BOOTSTRAP_AUTH=false
```

### Problem: Lost an API key

**Solution:**
1. Use admin key (or bootstrap if still enabled) to list keys
2. Revoke the lost key
3. Create a new key for that agent

```bash
# Revoke old key
curl -X DELETE http://localhost:5000/api/v1/auth/api-keys/{key_id} \
  -H "Authorization: Bearer <admin_key>"

# Create new key
# (follow manual creation steps above)
```

---

## How It Works Internally

When you make a request with the bootstrap key:

```python
# In src/api/dependencies.py

async def get_authenticated_agent(...):
    # 1. Extract API key from header
    api_key = get_key_from_header()

    # 2. Check if it's the bootstrap key (if enabled)
    if settings.ENABLE_BOOTSTRAP_AUTH and api_key == settings.BOOTSTRAP_ADMIN_KEY:
        # 3. Grant admin access WITHOUT database lookup
        return AuthenticatedAgent(
            agent_id="bootstrap-admin",
            agent_type="admin",
            scopes=["admin", "mandate:read", "mandate:write", ...]
        )

    # 4. Normal flow: lookup key in database
    return await auth_service.authenticate(api_key)
```

This **bypasses the database check** for the bootstrap key only, solving the circular dependency.

---

## Next Steps

After completing bootstrap setup:

1. ✅ All agents have API keys
2. ✅ Bootstrap is disabled
3. ✅ Service is secure

Now you can proceed with:
- **Integrating agents** with the mandate ledger
- **Testing the full flow** (intent → cart → payment)
- **Monitoring** via audit logs and metrics

See the main README for integration instructions!

---

## Quick Reference

| Action | Command |
|--------|---------|
| Start service | `uvicorn src.main:app --reload --host 0.0.0.0 --port 5000` |
| Run setup script | `PYTHONPATH=. python3 scripts/setup_agent_keys.py` |
| Test health | `curl http://localhost:5000/api/v1/health` |
| List keys (bootstrap) | `curl -H "Authorization: Bearer <bootstrap>" http://localhost:5000/api/v1/auth/api-keys` |
| Create key (bootstrap) | `curl -X POST -H "Authorization: Bearer <bootstrap>" http://localhost:5000/api/v1/auth/api-keys -d '{...}'` |
| Disable bootstrap | Edit `.env`: `ENABLE_BOOTSTRAP_AUTH=false` |

---

**Last Updated:** November 2025
**Version:** 1.0


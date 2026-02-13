# Mandate Ledger Service - API Reference

**Base URL:** `http://localhost:5000/api/v1`

**Authentication:** All endpoints require `X-API-Key` header (except `/health`)

---

## Authentication

All requests (except health check) must include:

```http
X-API-Key: mlsk_your_api_key_here
```

---

## Mandates API

### Create Mandate (with Pre-signed Support)

Create a new mandate in the ledger, optionally with initial signatures.

**Endpoint:** `POST /api/v1/mandates`

**Request Body:**
```json
{
  "mandate_type": "IntentMandate",
  "mandate_data": { /* AP2 mandate object */ },
  "transaction_id": "txn_abc123",
  "initial_signatures": [
    {
      "signature": "0x_shopping_agent_sig_2024-11-26T10:30:00Z",
      "signer_id": "trusted_shopping_agent",
      "signer_type": "shopping-agent",
      "algorithm": "EdDSA",
      "signed_at": "2024-11-26T10:30:00Z"
    }
  ],
  "initial_status": "signed",
  "metadata": {}
}
```

**Response (201 Created):**
```json
{
  "entity_id": "IntentMandate_abc-123",
  "version": 1,
  "mandate_type": "IntentMandate",
  "status": "signed",
  "transaction_id": "txn_abc123",
  "created_at": "2024-11-26T10:30:00Z",
  "created_by_agent": "shopping_agent_123"
}
```

---

### Get Mandate History

Retrieve all versions of a mandate.

**Endpoint:** `GET /api/v1/mandates/{entity_id}`

**Response (200 OK):**
```json
{
  "entity_id": "IntentMandate_abc-123",
  "mandate_type": "IntentMandate",
  "transaction_id": "txn_abc123",
  "versions": [
    {
      "version": 1,
      "status": "created",
      "mandate_data": { /* ... */ },
      "signatures": [],
      "created_at": "2024-11-26T10:30:00Z"
    },
    {
      "version": 2,
      "status": "signed",
      "mandate_data": { /* ... */ },
      "signatures": [
        {
          "signature": "0x_...",
          "signer_id": "shopping_agent",
          "signer_type": "shopping-agent",
          "algorithm": "EdDSA",
          "signed_at": "2024-11-26T10:31:00Z"
        }
      ],
      "created_at": "2024-11-26T10:31:00Z"
    }
  ],
  "current_version": 2,
  "current_status": "signed"
}
```

---

### Get Transaction Mandates

Retrieve all mandates associated with a transaction ID.

**Endpoint:** `GET /api/v1/mandates/transaction/{transaction_id}`

**Response (200 OK):**
```json
{
  "transaction_id": "txn_abc123",
  "mandates": [
    {
      "entity_id": "IntentMandate_abc-123",
      "mandate_type": "IntentMandate",
      "current_version": 1,
      "current_status": "signed",
      "created_at": "2024-11-26T10:30:00Z",
      "updated_at": "2024-11-26T10:30:00Z"
    },
    {
      "entity_id": "CartMandate_def-456",
      "mandate_type": "CartMandate",
      "current_version": 2,
      "current_status": "signed",
      "created_at": "2024-11-26T10:31:00Z",
      "updated_at": "2024-11-26T10:32:00Z"
    },
    {
      "entity_id": "PaymentMandate_ghi-789",
      "mandate_type": "PaymentMandate",
      "current_version": 1,
      "current_status": "created",
      "created_at": "2024-11-26T10:33:00Z",
      "updated_at": "2024-11-26T10:33:00Z"
    }
  ],
  "total": 3
}
```

---

## Payments API

### Create Payment Record

Create an ultra-lean payment record referencing mandates.

**Endpoint:** `POST /api/v1/payments`

**Request Body:**
```json
{
  "transaction_id": "txn_abc123",
  "intent_mandate_id": "IntentMandate_abc-123",
  "cart_mandate_id": "CartMandate_def-456",
  "payment_mandate_id": "PaymentMandate_ghi-789",
  "amount": 29.99,
  "currency": "USD",
  "status": "SUCCESS",
  "merchant_agent": "merchant_agent_dev",
  "payment_processor_agent": "payment_processor",
  "payment_method_type": "CARD",
  "metadata": {}
}
```

**Response (201 Created):**
```json
{
  "payment_id": "pay_xyz789",
  "transaction_id": "txn_abc123",
  "intent_mandate": {
    "mandate_id": "IntentMandate_abc-123",
    "signature": "0x_...",
    "timestamp": "2024-11-26T10:30:00Z"
  },
  "cart_mandate": {
    "mandate_id": "CartMandate_def-456",
    "signature": "0x_...",
    "timestamp": "2024-11-26T10:32:00Z"
  },
  "payment_mandate": {
    "mandate_id": "PaymentMandate_ghi-789",
    "signature": "0x_...",
    "timestamp": "2024-11-26T10:33:00Z"
  },
  "amount": 29.99,
  "currency": "USD",
  "status": "SUCCESS",
  "created_at": "2024-11-26T10:35:00Z"
}
```

---

### Get Payment Record

**Endpoint:** `GET /api/v1/payments/{payment_id}`

**Response:** Same as create response

---

### Get Payments by Transaction

**Endpoint:** `GET /api/v1/payments/session/{transaction_id}`

**Response (200 OK):**
```json
{
  "transaction_id": "txn_abc123",
  "payments": [
    {
      "payment_id": "pay_xyz789",
      "amount": 29.99,
      "currency": "USD",
      "status": "SUCCESS",
      "created_at": "2024-11-26T10:35:00Z"
    }
  ],
  "total": 1
}
```

---

### Search Payments

**Endpoint:** `GET /api/v1/payments`

**Query Parameters:**
- `status` (optional) - Filter by payment status (e.g., `SUCCESS`, `FAILED`)
- `merchant_agent` (optional) - Filter by merchant agent ID
- `skip` (optional, default: 0) - Number of records to skip
- `limit` (optional, default: 100, max: 1000) - Maximum records to return

**Example:**
```bash
GET /api/v1/payments?status=SUCCESS&merchant_agent=merchant_123&limit=50
```

**Response (200 OK):**
```json
{
  "payments": [...],
  "total": 25,
  "skip": 0,
  "limit": 50
}
```

---

## Audit API

### Get Audit Logs

**Endpoint:** `GET /api/v1/audit/logs`

**Query Parameters:**
- `entity_id` (optional) - Filter by entity
- `agent_id` (optional) - Filter by agent
- `action` (optional) - Filter by action type
- `limit` (optional, default: 100)
- `offset` (optional, default: 0)

**Response (200 OK):**
```json
{
  "logs": [
    {
      "log_id": "log_123",
      "entity_id": "IntentMandate_abc-123",
      "entity_type": "mandate",
      "action": "create",
      "agent_id": "shopping_agent_123",
      "timestamp": "2024-11-26T10:30:00Z",
      "changes": {
        "status": {"old": null, "new": "created"}
      }
    }
  ],
  "total": 1,
  "limit": 100,
  "offset": 0
}
```

---

### Get Mandate Audit Trail

**Endpoint:** `GET /api/v1/audit/mandates/{entity_id}`

**Response:** Same format as Get Audit Logs, filtered by entity_id

---

## Health & Admin API

### Health Check

**Endpoint:** `GET /api/v1/health`

**Authentication:** Not required

**Response (200 OK):**
```json
{
  "status": "healthy",
  "timestamp": "2024-11-26T10:30:00Z",
  "database": "connected",
  "version": "1.0.0"
}
```

---

### Storage Statistics

**Endpoint:** `GET /api/v1/admin/storage-stats`

**Response (200 OK):**
```json
{
  "database": "mandate_ledger",
  "collections": {
    "mandate_ledger": {
      "documents": 150,
      "size_bytes": 1048576,
      "indexes": 5
    },
    "payments": {
      "documents": 25,
      "size_bytes": 102400,
      "indexes": 3
    }
  },
  "total_size_mb": 1.5
}
```

---

## Idempotency

All mutation operations (POST) support idempotency using the `X-Idempotency-Key` header:

```http
POST /api/v1/mandates
X-API-Key: mlsk_...
X-Idempotency-Key: unique-operation-id-12345
Content-Type: application/json

{ /* request body */ }
```

If you retry with the same idempotency key within 24 hours, you'll receive the original response (cached).

---

## Error Responses

All errors follow this format:

```json
{
  "error": {
    "code": "MANDATE_NOT_FOUND",
    "message": "Mandate with entity_id 'IntentMandate_abc' does not exist",
    "details": {},
    "timestamp": "2024-11-26T10:30:00Z"
  }
}
```

**Common Error Codes:**
- `MANDATE_NOT_FOUND` (404)
- `INVALID_MANDATE_TYPE` (400)
- `UNAUTHORIZED` (401)
- `FORBIDDEN` (403)
- `VALIDATION_ERROR` (422)
- `INTERNAL_SERVER_ERROR` (500)

---

**Interactive API Documentation:** http://localhost:5000/docs


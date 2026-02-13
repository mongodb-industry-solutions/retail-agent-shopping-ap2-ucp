# Mandate Ledger Service

**An immutable, append-only ledger for Agent Payments Protocol (AP2) mandates.**

Built with MongoDB Atlas, FastAPI, and Python 3.12+.

---

## 🎯 Overview

This service provides a secure ledger for tracking AP2 payment mandates with:

- ✅ **Immutability** – No UPDATE/DELETE operations, append-only
- ✅ **Authentication** – API key validation per agent
- ✅ **RBAC** – Role-based access control by agent type
- ✅ **Idempotency** – Safe retries via `X-Idempotency-Key` header
- ✅ **Audit Trail** – Complete history of all operations

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- MongoDB Atlas M30+ or local MongoDB 7.0+

### Installation

```bash
cd mandate_ledger_service

python3.12 -m venv .venv
source .venv/bin/activate
pip install -e .

cp .env.example .env
# Edit .env with your MongoDB URI

uvicorn src.main:app --reload --port 5000
```

**Access:**
- API: http://localhost:5000
- Docs: http://localhost:5000/docs
- Health: http://localhost:5000/health

---

## 🔐 Bootstrap Authentication

Create API keys for your agents:

1. Set in `.env`:
   ```bash
   BOOTSTRAP_ADMIN_KEY=your_key_here  # Generate: openssl rand -hex 32
   ENABLE_BOOTSTRAP_AUTH=true
   ```

2. Run setup script:
   ```bash
   PYTHONPATH=. python3 scripts/setup_agent_keys.py
   ```

3. **Save the API keys** – they won't be shown again!

4. Disable bootstrap:
   ```bash
   # Edit .env
   ENABLE_BOOTSTRAP_AUTH=false
   ```

**Full guide:** [docs/BOOTSTRAP_AUTH_SETUP.md](docs/BOOTSTRAP_AUTH_SETUP.md)

---

## 📚 API Endpoints

### Mandates (Immutable)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/mandates` | Create mandate (supports pre-signed) |
| `GET` | `/api/v1/mandates/{entity_id}` | Get all versions |
| `GET` | `/api/v1/mandates/transaction/{txn_id}` | Get transaction mandates |

### Payments
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/payments` | Create payment record |
| `GET` | `/api/v1/payments/{payment_id}` | Get payment record |
| `GET` | `/api/v1/payments/session/{txn_id}` | Get session payments |
| `GET` | `/api/v1/payments?status=X` | Search payments (query params) |

### Audit & Admin
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/audit/logs` | Query audit logs |
| `GET` | `/api/v1/audit/mandates/{entity_id}` | Mandate audit trail |
| `GET` | `/api/v1/health` | Health check |
| `GET` | `/api/v1/admin/storage-stats` | Storage statistics |

**Full API documentation:** [docs/API_REFERENCE.md](docs/API_REFERENCE.md)

---

## 🔧 Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGODB_URI` | MongoDB connection string | Required |
| `MONGODB_DATABASE` | Database name | `mandate_ledger` |
| `ENABLE_BOOTSTRAP_AUTH` | Enable bootstrap key | `false` |
| `BOOTSTRAP_ADMIN_KEY` | Bootstrap admin key | - |
| `DEFAULT_RATE_LIMIT_PER_MINUTE` | Rate limit per agent | `60` |
| `ALLOWED_CORS_ORIGINS` | CORS origins | `*` |

See `.env.example` for all options.

---

## 🗄️ MongoDB Collections

| Collection | Purpose |
|------------|---------|
| `mandate_ledger` | Immutable mandate versions |
| `payments` | Payment records |
| `api_keys` | Agent API keys |
| `audit_log` | Operation audit trail |
| `idempotency_records` | Request deduplication |

---

## 📁 Project Structure

```
src/
├── api/routes/          # FastAPI endpoints
├── core/                # State machine, hashing, errors
├── db/                  # MongoDB connection
├── models/              # Pydantic models
├── repositories/        # Data access layer
├── services/            # Business logic
└── types/               # AP2 mandate types
```

---

## 📄 License

Apache License 2.0

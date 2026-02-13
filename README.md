# retail-agent-shopping-ap2-ucp

[![Apache License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Powered by MongoDB](https://img.shields.io/badge/Powered%20by-MongoDB-green.svg)](https://www.mongodb.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-blue.svg)](https://fastapi.tiangolo.com/)

## 🎯 Overview

This Proof of Concept (PoC) demonstrates an enterprise-grade agentic commerce system built around the **Agent Payment Protocol (AP2)**. At its core, **MongoDB Atlas** serves as the immutable **Mandate Ledger** – a highly secure, scalable, and auditable document database establishing the canonical System of Record for all AP2 transactions throughout the agentic commerce lifecycle.

---

## 🏗️ Architecture

The system consists of multiple agents communicating via **Agent-to-Agent (A2A)** or **Universal Commerce Protocol (UCP)** to execute transactions. MongoDB Atlas serves as the central, immutable ledger.

> **NEW:** See the [UCP + AP2 Integration Guide](docs/UCP_AP2_INTEGRATION.md) to understand how AP2 works with the Universal Commerce Protocol.

### Service Layer Protection

The **Mandate Ledger Service** acts as a protective middleware between agents and the database, **preventing direct database modifications**:

| Layer | Responsibility |
|-------|----------------|
| **Authentication Layer** | API key validation, role-based access control (RBAC) |
| **Business Logic Layer** | Validation, concurrency control, idempotency, immutability |
| **Data Access Layer** | MongoDB client with optimized indexing |

All operations flow through this service layer ensuring audit trails, state machine validation, and secure access.

![Architecture Overview](assets/architecture_diagram.png)

### Transaction Flow

The complete payment lifecycle flows through three mandate types:

1. **IntentMandate** – User's shopping intent (signed by Shopping Agent)
2. **CartMandate** – Merchant's product offer (signed by both parties)
3. **PaymentMandate** – User's payment authorization (signed → completed)
4. **Payment Record** – Ultra-lean completion record referencing all mandates

![Transaction Flow](assets/transaction_flow.png)

---

## 📋 Prerequisites

- Python 3.12+
- MongoDB Atlas M30+ or local MongoDB 7.0+
- Google API Key ([Get one](https://aistudio.google.com/apikey)) or Vertex AI access
- [`uv`](https://docs.astral.sh/uv/) (optional)

---

## 🚀 Setup & Run

### Step 1: Install Ledger Service

```bash
git clone https://github.com/mongodb-ps/aifac-mandate-ledger-service-AP2.git
cd aifac-mandate-ledger-service-AP2/mandate_ledger_service

python3.12 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Create `.env` file in `mandate_ledger_service/`:

```bash
MONGODB_URI=**** # Your connection string
MONGODB_DATABASE=mandate_ledger
SERVICE_NAME=mandate-ledger-service
ENVIRONMENT=development

# Bootstrap Auth (dev only - set to false after Step 2)
BOOTSTRAP_ADMIN_KEY=****  # Generate: openssl rand -hex 32
ENABLE_BOOTSTRAP_AUTH=true

ALLOWED_CORS_ORIGINS=*
DEFAULT_RATE_LIMIT_PER_MINUTE=60
```

Start the service:
```bash
uvicorn src.main:app --reload --port 5000
```

### Step 2: Generate Agent API Keys

Open a new terminal and run:
```bash
cd mandate_ledger_service
source .venv/bin/activate
PYTHONPATH=. python3 scripts/setup_agent_keys.py
```

Copy the **Merchant Agent API Key** from output. Then edit `.env` and set `ENABLE_BOOTSTRAP_AUTH=false`, restart service.

> **Production:** Use a secrets manager (Google Secret Manager, AWS Secrets Manager) and implement key rotation.

### Step 3: Configure Card Flow

> The card flow example is adapted from the official [AP2 Samples](https://github.com/google-agentic-commerce/AP2/tree/main/samples).

Create `.env` file in `example/card_flow/`:
MANDATE_LEDGER_API_KEY is your mlsk_merchant_key_from_step2

```bash
GOOGLE_API_KEY=
MANDATE_LEDGER_SERVICE_URL=http://localhost:5000
MANDATE_LEDGER_API_KEY=
```

For Vertex AI, replace first line with:
```bash
GOOGLE_GENAI_USE_VERTEXAI=true
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
```

### Step 4: Run Demo

From repository root:
```bash
bash example/card_flow/run.sh
```

Open http://localhost:8000/dev-ui and say: *"I want to buy a coffee maker"*

Follow prompts → Enter OTP `123` when asked → Payment complete! 🎉

---

## 🔑 Key Features

### Mandate Ledger Service

| Feature | Description |
|---------|-------------|
| **Immutability** | No UPDATE/DELETE operations – append-only ledger |
| **Authentication** | API key validation per agent |
| **RBAC** | Role-based access control by agent type |
| **Idempotency** | Safe retries via `X-Idempotency-Key` header |
| **Audit Trail** | Complete history of all operations |

### Example Flows

This demo includes two example flows demonstrating AP2 with different protocols:

| Example | Protocol | Description |
|---------|----------|-------------|
| **[Card Flow](example/card_flow/)** | A2A | Multi-agent flow using Agent-to-Agent protocol |
| **[UCP Flow](example/ucp_flow/)** | UCP | REST-based flow using Universal Commerce Protocol |

#### Card Flow Agents (A2A)

| Agent | Role |
|-------|------|
| **Shopping Agent** | User-facing orchestrator |
| **Merchant Agent** | Product catalog, cart management |
| **Credentials Provider** | Payment methods wallet |
| **Payment Processor** | Transaction processing |

#### UCP Flow Components

| Component | Role |
|-----------|------|
| **Shopper Agent** (ADK) | AI shopping assistant using UCP REST |
| **Merchant Server** (FastAPI) | UCP-compliant REST server with AP2 integration |

> **Note:** The AP2 Mandate Ledger Service works with any commerce protocol – A2A, UCP, or custom implementations.

---

## 📁 Repository Structure

```
├── mandate_ledger_service/        # 🔐 Core Immutable Ledger
│   ├── src/
│   │   ├── api/                   # FastAPI endpoints
│   │   ├── core/                  # Business logic, state machine
│   │   ├── db/                    # MongoDB connection
│   │   ├── models/                # Pydantic models
│   │   ├── repositories/          # Data access layer
│   │   └── services/              # Service layer
│   ├── scripts/                   # Setup utilities
│   └── docs/                      # API documentation
│
├── example/                       # 🛍️ Commerce Examples
│   ├── src/
│   │   ├── ap2/types/             # AP2 protocol types
│   │   ├── common/                # Shared utilities
│   │   └── roles/                 # Agent implementations (A2A)
│   ├── card_flow/                 # A2A-based demo
│   └── ucp_flow/                  # UCP-based demo (NEW)
│       ├── merchant_server/       # FastAPI UCP server
│       └── shopper_agent/         # ADK agent with UCP client
│
├── docs/                          # 📖 Documentation
│   └── UCP_AP2_INTEGRATION.md     # UCP + AP2 integration guide
│
└── assets/                        # 📊 Architecture diagrams
```

---

## 🚨 Troubleshooting

```bash
# Kill stuck processes
lsof -ti:5000 | xargs kill -9  # Ledger service
lsof -ti:8000 | xargs kill -9  # Shopping agent

# Check service health
curl http://localhost:5000/health
```

**Common issues:**
- `.env` file must be in `example/card_flow/` directory
- Must use Merchant Agent API key (not Shopping Agent)
- Run `run.sh` from repository root

---

## 📚 Documentation

- [API Reference](mandate_ledger_service/docs/API_REFERENCE.md) – Complete endpoint docs
- [Bootstrap Auth](mandate_ledger_service/docs/BOOTSTRAP_AUTH_SETUP.md) – API key setup
- [Card Flow Details](example/card_flow/README.md) – A2A demo walkthrough
- [UCP Flow Details](example/ucp_flow/README.md) – UCP demo walkthrough
- [UCP + AP2 Integration](docs/UCP_AP2_INTEGRATION.md) – How UCP and AP2 work together

---

## 📄 License

Apache License 2.0 - See [LICENSE](LICENSE)

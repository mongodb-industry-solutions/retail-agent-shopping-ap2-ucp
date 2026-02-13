# Example: Card Payment Flow with Mandate Ledger

This directory contains a working example demonstrating the Mandate Ledger Service integration with a multi-agent card payment flow.

## Structure

```
example/
├── src/
│   ├── common/                    # Shared utilities
│   │   └── mandate_ledger_client.py  # Client library for Ledger
│   └── roles/                     # Agent implementations
│       ├── shopping_agent/        # User-facing agent
│       ├── merchant_agent/        # Product catalog + ledger writes
│       ├── credentials_provider_agent/
│       └── merchant_payment_processor_agent/
│
└── card_flow/                     # Card payment demo
    ├── run.sh                     # Launch script
    ├── setup_ledger_env.sh        # Environment setup
    └── README.md                  # Detailed instructions
```

## Quick Start

See the [card_flow/README.md](card_flow/README.md) for detailed instructions.

```bash
# From repository root
bash example/card_flow/run.sh
```

## Prerequisites

- Python 3.10+
- `uv` package manager
- Running Mandate Ledger Service (see main README)
- Google API Key or Vertex AI access

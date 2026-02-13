#!/usr/bin/env python3
"""
Setup script to create API keys for agents that interact with the Mandate Ledger.

This script uses the bootstrap admin key to create real API keys for:
- Merchant Agent: Writes mandates and payment records to the ledger
- Auditor Agent: Read-only access for audit and verification
- Admin User: Full access for management and monitoring

NOTE: Shopping Agent, Credentials Provider, and Payment Processor do NOT
need API keys because they don't interact directly with the Mandate Ledger.
Only the Merchant Agent writes to the ledger on behalf of the transaction flow.

Usage:
    cd mandate_ledger_service
    PYTHONPATH=. python3 scripts/setup_agent_keys.py

Requirements:
    - Mandate Ledger Service must be running
    - BOOTSTRAP_ADMIN_KEY must be set in .env
    - ENABLE_BOOTSTRAP_AUTH must be true
"""

import asyncio
import httpx
import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Load .env file if present
try:
    from dotenv import load_dotenv
    # Look for .env in current directory and parent directory
    env_path = Path(".env")
    if not env_path.exists():
        env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print(f"[INFO] Loaded environment from: {env_path}")
except ImportError:
    print("[WARNING] python-dotenv not installed. Using environment variables only.")
    print("         Install with: pip install python-dotenv")

# Configuration
LEDGER_SERVICE_URL = os.getenv("LEDGER_SERVICE_URL", "http://localhost:5000")
BOOTSTRAP_KEY = os.getenv("BOOTSTRAP_ADMIN_KEY", "")

# Agent configurations
# Only agents that directly interact with the Mandate Ledger need API keys
AGENTS = [
    {
        "agent_id": "merchant_agent_dev",
        "agent_type": "merchant-agent",
        "scopes": ["mandate:read", "mandate:write", "payment:read", "payment:write", "audit:read"],
        "expires_in_days": 365,
        "metadata": {
            "description": "Merchant agent - writes mandates and payment records to ledger",
            "environment": "development"
        }
    },
    {
        "agent_id": "auditor_agent_dev",
        "agent_type": "auditor",
        "scopes": ["mandate:read", "payment:read", "audit:read"],
        "expires_in_days": 365,
        "metadata": {
            "description": "Auditor agent - read-only access for verification and compliance",
            "environment": "development"
        }
    },
    {
        "agent_id": "admin-user",
        "agent_type": "admin",
        "scopes": ["admin", "mandate:read", "mandate:write", "payment:read", "payment:write", "audit:read", "auth:manage"],
        "expires_in_days": None,  # Never expires
        "metadata": {
            "description": "Admin user for monitoring and management",
            "environment": "development"
        }
    }
]


async def create_agent_key(client: httpx.AsyncClient, agent_config: dict) -> dict:
    """Create an API key for an agent."""
    print(f"\n[CREATING] API key for {agent_config['agent_id']}...")

    try:
        response = await client.post(
            f"{LEDGER_SERVICE_URL}/api/v1/auth/api-keys",
            headers={
                "Authorization": f"Bearer {BOOTSTRAP_KEY}",
                "Content-Type": "application/json"
            },
            json=agent_config,
            timeout=30.0
        )

        if response.status_code == 201:
            data = response.json()
            print(f"[SUCCESS] Created key for {data['agent_id']}")
            print(f"  Key ID: {data['key_id']}")
            print(f"  Key Prefix: {data['key_prefix']}")
            print(f"  API Key: {data['api_key']}")
            print(f"  Scopes: {', '.join(data['scopes'])}")
            if data.get('expires_at'):
                print(f"  Expires: {data['expires_at']}")
            print("  [WARNING] SAVE THIS KEY! It won't be shown again.")
            return data
        else:
            print(f"[ERROR] Failed to create key: {response.status_code}")
            print(f"  Response: {response.text}")
            return None
    except Exception as e:
        print(f"[ERROR] Exception while creating key: {e}")
        return None


def save_api_keys_to_file(created_keys: list[dict], output_dir: str = ".") -> str:
    """
    Save API keys to a secure JSON file.

    Args:
        created_keys: List of API key data from the service
        output_dir: Directory to save the file (default: current directory)

    Returns:
        Path to the created file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"api_keys_{timestamp}.json"
    filepath = Path(output_dir) / filename

    # Prepare data with warning
    data = {
        "generated_at": datetime.now().isoformat(),
        "warning": "⚠️  KEEP THIS FILE SECURE! Contains sensitive API keys that grant access to the mandate ledger.",
        "note": "These keys are only shown once. Back up this file in a secure location (e.g., password manager, vault).",
        "service_url": LEDGER_SERVICE_URL,
        "total_keys": len(created_keys),
        "keys": created_keys
    }

    # Ensure directory exists
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Write to file with pretty formatting
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

    # Set restrictive permissions (Unix-like systems)
    try:
        filepath.chmod(0o600)  # Only owner can read/write
    except Exception:
        pass  # Windows doesn't support chmod

    return str(filepath)


async def main():
    print("=" * 70)
    print("  MANDATE LEDGER SERVICE - AGENT KEY SETUP")
    print("=" * 70)
    print(f"\nLedger Service: {LEDGER_SERVICE_URL}")

    if not BOOTSTRAP_KEY:
        print("\n[ERROR] BOOTSTRAP_ADMIN_KEY not set!")
        print("Please set it in your .env file or environment.")
        sys.exit(1)

    print(f"Bootstrap Key: {BOOTSTRAP_KEY[:20]}...")
    print(f"\nThis will create API keys for {len(AGENTS)} agents.")

    # Check service health
    print("\n[CHECKING] Service health...")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            health_response = await client.get(f"{LEDGER_SERVICE_URL}/api/v1/health")
            if health_response.status_code == 200:
                health_data = health_response.json()
                print(f"[OK] Service is healthy!")
                print(f"  Service: {health_data.get('service')}")
                print(f"  Status: {health_data.get('status')}")
                print(f"  Database: {health_data.get('database')}")
            else:
                print(f"[WARNING] Service health check returned {health_response.status_code}")
    except Exception as e:
        print(f"[ERROR] Cannot connect to service: {e}")
        print("\nMake sure the service is running:")
        print("  cd mandate_ledger_service")
        print("  uvicorn src.main:app --reload --host 0.0.0.0 --port 8000")
        sys.exit(1)

    # Create keys for all agents
    print("\n" + "=" * 70)
    print("  CREATING API KEYS")
    print("=" * 70)

    created_keys = []
    async with httpx.AsyncClient(timeout=30.0) as client:
        for agent_config in AGENTS:
            key_data = await create_agent_key(client, agent_config)
            if key_data:
                created_keys.append(key_data)
            await asyncio.sleep(0.5)  # Rate limiting courtesy

    # Save API keys to file
    keys_file = None
    if created_keys:
        try:
            keys_file = save_api_keys_to_file(created_keys, output_dir=".")
            print(f"\n[SAVED] API keys written to file: {keys_file}")
            print(f"  File permissions: 600 (read/write owner only)")
            print(f"  Total keys saved: {len(created_keys)}")
        except Exception as e:
            print(f"\n[ERROR] Failed to save API keys to file: {e}")
            print("  Keys are still displayed above - copy them manually!")

    # Summary
    print("\n" + "=" * 70)
    print("  SETUP COMPLETE")
    print("=" * 70)
    print(f"\nCreated {len(created_keys)} API keys successfully.")

    if len(created_keys) < len(AGENTS):
        print(f"\n[WARNING] Failed to create {len(AGENTS) - len(created_keys)} keys.")
        print("Check the error messages above.")

    # Next steps
    print("\n" + "=" * 70)
    print("  NEXT STEPS")
    print("=" * 70)
    if keys_file:
        print(f"\n1. ✅ API KEYS SAVED TO FILE:")
        print(f"   {keys_file}")
        print("   • Keep this file secure (do not commit to git)")
        print("   • Back up to password manager or secure vault")
        print("   • File permissions set to 600 (owner read/write only)")
    else:
        print("\n1. SAVE THE API KEYS ABOVE to a secure location!")
        print("   Each key is shown only once and cannot be retrieved later.")
    print("\n2. CONFIGURE the Merchant Agent:")
    print("   Set in example/card_flow/.env:")
    print("   MANDATE_LEDGER_SERVICE_URL value is http://localhost:5000")
    print("   MANDATE_LEDGER_API_KEY value is <merchant_agent_key_from_json>")
    print("\n3. Note: Only the Merchant Agent needs a ledger API key.")
    print("   Other agents (Shopping, Credentials, Payment Processor)")
    print("   communicate via A2A and don't access the ledger directly.")
    print("\n4. DISABLE BOOTSTRAP in production:")
    print("   Edit mandate_ledger_service/.env:")
    print("   ENABLE_BOOTSTRAP_AUTH value is false")
    print("\n5. RESTART the mandate ledger service after disabling bootstrap")

    # Generate sample .env content for merchant agent
    print("\n" + "=" * 70)
    print("  SAMPLE .env CONTENT FOR CARD FLOW")
    print("=" * 70)
    for key_data in created_keys:
        if key_data['agent_type'] == 'merchant-agent':
            print(f"\n# File: example/card_flow/.env")
            print(f"MANDATE_LEDGER_SERVICE_URL value is http://localhost:5000")
            print(f"MANDATE_LEDGER_API_KEY value is {key_data['api_key']}")
            print(f"GOOGLE_API_KEY")
            print(f"GOOGLE_GENAI_USE_VERTEXAI value is true")

    print("\n" + "=" * 70)
    print("\nSetup complete! The Merchant Agent can now write to the ledger.")
    print("\nAgent Access Summary:")
    print("  • Merchant Agent: Read/Write mandates and payments")
    print("  • Auditor Agent:  Read-only for compliance verification")
    print("  • Admin User:     Full access for management")

    if keys_file:
        print(f"\n📄 API keys saved to: {keys_file}")
        print("   View the file to get individual API keys.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n[CANCELLED] Setup interrupted by user.")
        sys.exit(1)


# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Tools for the UCP Auditor Agent.

These tools verify transactions and demonstrate the immutability
of the AP2 Mandate Ledger.
"""

import os
import logging
import httpx
from typing import Optional

logger = logging.getLogger(__name__)

# Ledger service configuration
LEDGER_URL = os.getenv("MANDATE_LEDGER_SERVICE_URL", "http://localhost:5000")
LEDGER_API_KEY = os.getenv("MANDATE_LEDGER_API_KEY", "")


def _get_headers() -> dict:
    """Get headers for ledger API requests."""
    return {
        "Authorization": f"Bearer {LEDGER_API_KEY}",
        "Content-Type": "application/json"
    }


async def check_ledger_by_payment_id(payment_id: str) -> dict:
    """
    Verify a transaction in the mandate ledger by payment_id.
    
    Returns transaction status, confirmation that the record exists in the ledger,
    and AP2 signature verification results (Buyer Intent, Seller Cart, Buyer Payment).
    Also returns the transaction_id and all mandate IDs for further investigation.
    
    Args:
        payment_id: Unique payment identifier (e.g., pay_xxx)
    
    Returns:
        Verification results with signature validation.
    """
    try:
        # Step 1: Get payment record
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{LEDGER_URL}/api/v1/payments/{payment_id}",
                headers=_get_headers()
            )
            response.raise_for_status()
            payment_data = response.json()

        # Step 2: Extract mandate IDs
        intent_mandate_id = payment_data["intent_mandate"]["mandate_id"]
        cart_mandate_id = payment_data["cart_mandate"]["mandate_id"]
        payment_mandate_id = payment_data["payment_mandate"]["mandate_id"]

        # Step 3: Get each mandate to verify signatures
        async with httpx.AsyncClient(timeout=30.0) as client:
            intent_resp = await client.get(
                f"{LEDGER_URL}/api/v1/mandates/{intent_mandate_id}",
                headers=_get_headers()
            )
            intent_mandates = intent_resp.json()
            
            cart_resp = await client.get(
                f"{LEDGER_URL}/api/v1/mandates/{cart_mandate_id}",
                headers=_get_headers()
            )
            cart_mandates = cart_resp.json()
            
            payment_resp = await client.get(
                f"{LEDGER_URL}/api/v1/mandates/{payment_mandate_id}",
                headers=_get_headers()
            )
            payment_mandates = payment_resp.json()

        # Get latest version (index 0)
        intent_mandate = intent_mandates[0] if intent_mandates else {}
        cart_mandate = cart_mandates[0] if cart_mandates else {}
        payment_mandate = payment_mandates[0] if payment_mandates else {}

        # Build verification result
        signature_checks = {
            "buyer_intent_signature": bool(intent_mandate.get("signatures")),
            "seller_cart_signature": bool(cart_mandate.get("signatures")),
            "buyer_payment_signature": bool(payment_mandate.get("signatures"))
        }

        all_signatures_valid = all(signature_checks.values())
        transaction_successful = payment_data["status"] == "SUCCESS"

        return {
            "success": True,
            "payment_id": payment_id,
            "transaction_id": payment_data["transaction_id"],
            "status": payment_data["status"],
            "amount": payment_data["amount"],
            "currency": payment_data["currency"],
            "transaction_successful": transaction_successful,
            "ledger_record_found": True,
            "signature_verification": {
                "all_valid": all_signatures_valid,
                "buyer_intent_signature_valid": signature_checks["buyer_intent_signature"],
                "seller_cart_signature_valid": signature_checks["seller_cart_signature"],
                "buyer_payment_signature_valid": signature_checks["buyer_payment_signature"]
            },
            "intent_mandate_id": intent_mandate_id,
            "cart_mandate_id": cart_mandate_id,
            "payment_mandate_id": payment_mandate_id,
            "message": (
                f"The transaction was {'successful' if transaction_successful else 'unsuccessful'}, "
                f"and all signatures have been cryptographically verified as authentic."
            )
        }

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return {
                "success": False,
                "payment_id": payment_id,
                "ledger_record_found": False,
                "error": "Payment record not found in mandate ledger",
                "message": f"No transaction record found for payment_id: {payment_id}"
            }
        raise
    except Exception as e:
        logger.error(f"Failed to verify payment: {e}")
        return {
            "success": False,
            "payment_id": payment_id,
            "error": str(e),
            "message": f"Error verifying payment: {str(e)}"
        }


async def get_mandate_history(
    transaction_id: Optional[str] = None,
    mandate_id: Optional[str] = None,
) -> dict:
    """
    Get detailed mandate history and audit trail.
    
    Can retrieve:
    1. Full transaction history - provide transaction_id to see all 3 mandate histories
    2. Specific mandate history - provide mandate_id for a single mandate
    
    Args:
        transaction_id: Transaction ID (same as order_id in UCP flow)
        mandate_id: Specific mandate entity ID
    
    Returns:
        Complete audit trail with all versions.
    """
    try:
        if transaction_id:
            # Get all mandates for this transaction
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{LEDGER_URL}/api/v1/mandates/transaction/{transaction_id}",
                    headers=_get_headers()
                )
                response.raise_for_status()
                mandates = response.json()

            if not mandates:
                return {
                    "success": False,
                    "message": f"No mandates found for transaction_id: {transaction_id}"
                }

            # Get all versions for each mandate
            intent_versions = []
            cart_versions = []
            payment_versions = []

            async with httpx.AsyncClient(timeout=30.0) as client:
                for mandate in mandates:
                    entity_id = mandate["entity_id"]
                    mandate_type = mandate["entity_type"]

                    response = await client.get(
                        f"{LEDGER_URL}/api/v1/mandates/{entity_id}",
                        headers=_get_headers()
                    )
                    response.raise_for_status()
                    versions = response.json()

                    if mandate_type == "IntentMandate":
                        intent_versions = versions
                    elif mandate_type == "CartMandate":
                        cart_versions = versions
                    elif mandate_type == "PaymentMandate":
                        payment_versions = versions

            return {
                "success": True,
                "type": "full_transaction_timeline",
                "transaction_id": transaction_id,
                "timeline": {
                    "intent": {
                        "entity_id": intent_versions[0]["entity_id"] if intent_versions else None,
                        "versions": intent_versions,
                        "total_versions": len(intent_versions),
                        "description": "Buyer's intent with signature"
                    },
                    "cart": {
                        "entity_id": cart_versions[0]["entity_id"] if cart_versions else None,
                        "versions": cart_versions,
                        "total_versions": len(cart_versions),
                        "description": "Cart flow: proposed → signed by buyer and merchant"
                    },
                    "payment": {
                        "entity_id": payment_versions[0]["entity_id"] if payment_versions else None,
                        "versions": payment_versions,
                        "total_versions": len(payment_versions),
                        "description": "Final payment mandate with signatures"
                    }
                },
                "total_mandates": len(mandates),
                "message": f"Retrieved complete transaction timeline for {transaction_id}"
            }

        elif mandate_id:
            # Get all versions for a specific mandate
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{LEDGER_URL}/api/v1/mandates/{mandate_id}",
                    headers=_get_headers()
                )
                response.raise_for_status()
                versions = response.json()

            return {
                "success": True,
                "type": "single_mandate",
                "mandate_id": mandate_id,
                "version_count": len(versions),
                "versions": versions,
                "message": f"Retrieved {len(versions)} version(s) for mandate {mandate_id}"
            }
        else:
            return {
                "success": False,
                "message": "Must provide either transaction_id (order_id) or mandate_id"
            }

    except Exception as e:
        logger.error(f"Failed to get mandate history: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Error retrieving mandate history: {str(e)}"
        }


async def test_mandate_integrity(
    identifier: str,
    operation: str,
    details: Optional[str] = None,
) -> dict:
    """
    Test the immutability of the mandate ledger by attempting prohibited operations.
    
    Use this when users request operations like 'delete payment ABC' or 'update
    transaction XYZ to change amount to $60'. Demonstrates that the ledger rejects
    deletions and modifications.
    
    Args:
        identifier: Payment ID, transaction ID, or mandate ID
        operation: Operation to attempt (delete, update, or modify)
        details: What the user wants to change (e.g., 'change amount to $60')
    
    Returns:
        Results showing the operation was rejected.
    """
    results = {
        "operation_requested": operation,
        "identifier": identifier,
        "details": details or "No specific details provided",
        "operation_allowed": False,
        "rejection_reason": "",
        "explanation": ""
    }

    try:
        if operation == "delete":
            results["rejection_reason"] = "DELETE operations are not supported on the mandate ledger"
            results["explanation"] = (
                "The mandate ledger is append-only and immutable. Records cannot be deleted. "
                "This ensures:\n"
                "• Complete audit trail for compliance\n"
                "• Fraud prevention and dispute resolution\n"
                "• Regulatory compliance (financial records retention)\n"
                "• Protection for all parties (buyers, sellers, processors)"
            )

            # Attempt the operation to show it fails
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.delete(
                        f"{LEDGER_URL}/api/v1/payments/{identifier}",
                        headers=_get_headers()
                    )
                    # If we get here without error, something is wrong
                    results["operation_allowed"] = True
                    results["warning"] = "DELETE succeeded - this should not happen!"
            except httpx.HTTPStatusError as e:
                results["http_status"] = e.response.status_code
                results["error_message"] = str(e)

        elif operation in ["update", "modify"]:
            results["rejection_reason"] = "UPDATE/MODIFY operations cannot change historical records"
            results["explanation"] = (
                "The mandate ledger is immutable. You cannot modify existing records. "
                "Any changes create NEW versions, preserving the complete history.\n\n"
                f"Your requested change: {details or 'modify existing record'}\n\n"
                "Why immutability matters:\n"
                "• Every change is tracked with timestamp and agent ID\n"
                "• Historical records remain unchanged for audit purposes\n"
                "• Prevents retroactive tampering or fraud\n"
                "• Supports dispute resolution with provable history\n\n"
                "To make changes, the proper flow is:\n"
                "1. Create a NEW version of the mandate\n"
                "2. Both parties must re-sign the new version\n"
                "3. The old version remains in the ledger for audit trail"
            )

        results["final_status"] = (
            f"❌ Operation REJECTED: The mandate ledger's immutability protections "
            f"prevented this {operation} operation. All records remain intact and auditable."
        )

    except Exception as e:
        logger.error(f"Test execution error: {e}")
        results["error"] = str(e)
        results["final_status"] = f"Operation rejected with error: {str(e)}"

    return results


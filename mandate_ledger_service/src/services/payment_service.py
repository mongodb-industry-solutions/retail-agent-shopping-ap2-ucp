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
Payment Service
Business logic for payment record management
"""

from typing import Dict, Any
from datetime import datetime, timezone
from uuid import uuid4
import logging

from src.repositories.payment_repository import PaymentRepository
from src.repositories.mandate_repository import MandateRepository
from src.repositories.audit_repository import AuditRepository
from src.models.enums import EventType
from src.models.payment import PaymentRecord, MandateReference

logger = logging.getLogger(__name__)


class PaymentService:
    """Service for managing payment records"""

    def __init__(self):
        self.payment_repo = PaymentRepository()
        self.mandate_repo = MandateRepository()
        self.audit_repo = AuditRepository()

    async def auto_create_payment_from_mandates(
        self,
        transaction_id: str,
        intent_mandate: Dict[str, Any],
        cart_mandate: Dict[str, Any],
        payment_mandate: Dict[str, Any]
    ) -> PaymentRecord:
        """
        Auto-create ULTRA-LEAN payment record from mandate snapshots.

        Triggered by Change Stream when PaymentMandate is signed.

        Args:
            transaction_id: Transaction ID
            intent_mandate: Intent mandate document from DB
            cart_mandate: Cart mandate document from DB
            payment_mandate: Payment mandate document from DB

        Returns:
            Created payment record
        """

        payment_id = f"pay_{uuid4()}"

        logger.info(f"Auto-creating payment {payment_id} for transaction {transaction_id}")

        # Extract payment amount from cart mandate
        cart_data = cart_mandate.get("mandate_data", {})
        contents = cart_data.get("contents", {})
        payment_request = contents.get("payment_request", {})
        details = payment_request.get("details", {})
        total = details.get("total", {})
        amount_data = total.get("amount", {})

        amount = float(amount_data.get("value", 0))
        currency = amount_data.get("currency", "USD")

        # Extract agent info
        payment_data = payment_mandate.get("mandate_data", {})
        payment_contents = payment_data.get("payment_mandate_contents", {})
        merchant_agent = payment_contents.get("merchant_agent", "unknown")
        payment_processor = payment_mandate.get("created_by_agent", "unknown")

        # Extract payment method
        payment_response = payment_contents.get("payment_response", {})
        method_name = payment_response.get("method_name")

        # Extract user_id and session_id from mandate-level fields or metadata
        user_id = payment_mandate.get("user_id") or payment_mandate.get("metadata", {}).get("user_id")
        session_id = payment_mandate.get("session_id") or payment_mandate.get("metadata", {}).get("session_id")

        # Build ultra-lean mandate references (ID + signature + timestamp ONLY)
        intent_ref = self._build_mandate_reference(intent_mandate)
        cart_ref = self._build_mandate_reference(cart_mandate)
        payment_ref = self._build_mandate_reference(payment_mandate)

        # Create ULTRA-LEAN payment record
        payment_record = {
            "payment_id": payment_id,
            "transaction_id": transaction_id,
            "user_id": user_id,
            "session_id": session_id,

            # Mandate references (ID + signature + timestamp ONLY, NO content)
            "intent_mandate": intent_ref,
            "cart_mandate": cart_ref,
            "payment_mandate": payment_ref,

            # Payment summary (NOT in mandates)
            "amount": amount,
            "currency": currency,
            "status": "SUCCESS",
            "payment_method_type": method_name,

            # Metadata
            "merchant_agent": merchant_agent,
            "payment_processor_agent": payment_processor,
            "processed_at": datetime.now(timezone.utc),
            "metadata": {
                "auto_created": True,
                "source": "change_stream_listener"
            }
        }

        # Insert into payments collection
        created_payment = await self.payment_repo.create_payment(payment_record)

        # Create audit log
        await self.audit_repo.create_audit_log(
            event_type=EventType.PAYMENT_CREATED,
            entity_id=payment_id,
            entity_type="payment",
            entity_version=1,  # Payment records don't have versions, always 1
            actor_id="change_stream_auto",
            actor_type="system",
            action="auto_create_payment",
            changes={
                "transaction_id": transaction_id,
                "amount": amount,
                "currency": currency
            },
            metadata={
                "trigger": "payment_mandate_signed",
                "payment_mandate_id": payment_mandate["entity_id"]
            }
        )

        logger.info(f"✅ Payment record created: {payment_id}")

        return created_payment

    def _build_mandate_reference(self, mandate: Dict[str, Any]) -> dict:
        """
        Build ultra-lean mandate reference - ID + signature + timestamp ONLY.

        Args:
            mandate: Mandate document from DB

        Returns:
            Mandate reference dict
        """
        signatures = mandate.get("signatures", [])

        # Get latest signature
        if signatures:
            latest_sig = signatures[-1]
            signature = latest_sig.get("signature", "")
            timestamp = latest_sig.get("signed_at", "")

            # Convert datetime to ISO string if needed
            if isinstance(timestamp, datetime):
                timestamp = timestamp.isoformat()
        else:
            signature = ""
            timestamp = ""

        return {
            "mandate_id": mandate["entity_id"],
            "signature": signature,
            "timestamp": timestamp
            # NO CONTENT - query mandates collection if needed
        }

    async def create_payment_record(
        self,
        transaction_id: str,
        intent_mandate_id: str,
        cart_mandate_id: str,
        payment_mandate_id: str,
        amount: float,
        currency: str,
        status: str,
        merchant_agent: str,
        payment_processor_agent: str,
        payment_method_type: str = None,
        metadata: dict = None,
        user_id: str = None,
        session_id: str = None
    ) -> PaymentRecord:
        """
        Manually create a payment record.

        Temporary method until Change Streams are enabled.
        Validates that all 3 mandates exist and extracts signatures.

        Args:
            transaction_id: Transaction ID
            intent_mandate_id: Intent mandate entity ID
            cart_mandate_id: Cart mandate entity ID
            payment_mandate_id: Payment mandate entity ID
            amount: Payment amount
            currency: Currency code
            status: Payment status
            merchant_agent: Merchant agent ID
            payment_processor_agent: Payment processor agent ID
            payment_method_type: Optional payment method
            metadata: Optional metadata

        Returns:
            Created payment record

        Raises:
            ValueError: If any mandate is not found
        """

        logger.info(f"Manually creating payment for transaction {transaction_id}")

        # Fetch all 3 mandates to get their signatures
        intent_history = await self.mandate_repo.get_ledger_history(intent_mandate_id, limit=1)
        cart_history = await self.mandate_repo.get_ledger_history(cart_mandate_id, limit=1)
        payment_history = await self.mandate_repo.get_ledger_history(payment_mandate_id, limit=1)

        if not intent_history:
            raise ValueError(f"Intent mandate {intent_mandate_id} not found")
        if not cart_history:
            raise ValueError(f"Cart mandate {cart_mandate_id} not found")
        if not payment_history:
            raise ValueError(f"Payment mandate {payment_mandate_id} not found")

        # Get latest version (index 0)
        intent_mandate = intent_history[0].model_dump()
        cart_mandate = cart_history[0].model_dump()
        payment_mandate = payment_history[0].model_dump()

        # Build ultra-lean mandate references
        intent_ref = self._build_mandate_reference(intent_mandate)
        cart_ref = self._build_mandate_reference(cart_mandate)
        payment_ref = self._build_mandate_reference(payment_mandate)

        # Generate payment ID
        payment_id = f"pay_{uuid4()}"

        # Create ultra-lean payment record
        payment_record = {
            "payment_id": payment_id,
            "transaction_id": transaction_id,
            "user_id": user_id,
            "session_id": session_id,

            # Mandate references (ID + signature + timestamp ONLY)
            "intent_mandate": intent_ref,
            "cart_mandate": cart_ref,
            "payment_mandate": payment_ref,

            # Payment summary
            "amount": amount,
            "currency": currency,
            "status": status,
            "payment_method_type": payment_method_type,

            # Metadata
            "merchant_agent": merchant_agent,
            "payment_processor_agent": payment_processor_agent,
            "processed_at": datetime.now(timezone.utc),
            "metadata": metadata or {"source": "manual_creation"}
        }

        # Insert into payments collection
        created_payment = await self.payment_repo.create_payment(payment_record)

        # Create audit log
        await self.audit_repo.create_audit_log(
            event_type=EventType.PAYMENT_CREATED,
            entity_id=payment_id,
            entity_type="payment",
            entity_version=1,  # Payment records don't have versions, always 1
            actor_id=merchant_agent,
            actor_type="merchant_agent",
            action="manual_create_payment",
            changes={
                "transaction_id": transaction_id,
                "amount": amount,
                "currency": currency,
                "status": status
            },
            metadata={
                "intent_mandate_id": intent_mandate_id,
                "cart_mandate_id": cart_mandate_id,
                "payment_mandate_id": payment_mandate_id
            }
        )

        logger.info(f"✅ Payment record created: {payment_id}")

        return PaymentRecord(**payment_record)


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
Payment Record Auto-Creation Listener

Watches for signed PaymentMandates and creates payment records automatically.

Trigger: PaymentMandate with status='signed'
Action: Create corresponding payment record in payments collection
"""

import logging
from src.db.mongodb import MongoDB
from src.core.change_streams import change_stream_manager
from src.services.payment_service import PaymentService

logger = logging.getLogger(__name__)


async def handle_signed_payment_mandate(change: dict):
    """
    Auto-create payment record when PaymentMandate is signed.

    This handler is triggered by a MongoDB Change Stream when a new
    PaymentMandate document is inserted with status='signed'.

    Args:
        change: Change event from MongoDB
    """

    operation = change.get("operationType")
    if operation != "insert":
        return

    mandate = change.get("fullDocument")
    if not mandate:
        return

    # Verify it's a signed PaymentMandate
    mandate_type = mandate.get("entity_type")
    status = mandate.get("status")
    signatures = mandate.get("signatures", [])

    if mandate_type != "PaymentMandate" or status != "signed" or not signatures:
        logger.debug(f"Skipping mandate {mandate.get('entity_id')}: not a signed PaymentMandate")
        return

    entity_id = mandate.get("entity_id")
    logger.info(f"🔔 Detected signed PaymentMandate: {entity_id}")

    try:
        # Extract transaction context
        transaction_id = mandate.get("transaction_id")
        if not transaction_id:
            logger.error(f"❌ No transaction_id in PaymentMandate {entity_id}")
            return

        # Check if payment record already exists (idempotency)
        existing_payment = await MongoDB.payments.find_one({
            "payment_mandate.mandate_id": entity_id
        })

        if existing_payment:
            logger.info(f"⏭️  Payment record already exists for {entity_id}, skipping")
            return

        # Fetch related mandates (latest versions for this transaction)
        # MongoDB collection's find_one() supports sort parameter
        intent_mandate = await MongoDB.mandate_ledger.find_one(
            {
                "transaction_id": transaction_id,
                "entity_type": "IntentMandate"
            },
            sort=[("version", -1)]
        )

        cart_mandate = await MongoDB.mandate_ledger.find_one(
            {
                "transaction_id": transaction_id,
                "entity_type": "CartMandate"
            },
            sort=[("version", -1)]
        )

        if not intent_mandate:
            logger.error(f"❌ IntentMandate not found for transaction {transaction_id}")
            return

        if not cart_mandate:
            logger.error(f"❌ CartMandate not found for transaction {transaction_id}")
            return

        # Create payment record via service
        payment_service = PaymentService()
        payment_record = await payment_service.auto_create_payment_from_mandates(
            transaction_id=transaction_id,
            intent_mandate=intent_mandate,
            cart_mandate=cart_mandate,
            payment_mandate=mandate
        )

        logger.info(
            f"✅ Auto-created payment record: {payment_record.payment_id} "
            f"for transaction {transaction_id}"
        )

    except Exception as e:
        logger.error(
            f"❌ Failed to auto-create payment for mandate {entity_id}: {e}",
            exc_info=True
        )


def register_payment_listeners():
    """Register all payment-related change stream listeners"""

    logger.info("Registering payment change stream listeners...")

    # Listener: Auto-create payment records when PaymentMandate is signed
    change_stream_manager.register_listener(
        collection=MongoDB.mandate_ledger,
        pipeline=[
            {
                "$match": {
                    "operationType": "insert",
                    "fullDocument.entity_type": "PaymentMandate",
                    "fullDocument.status": "signed"
                }
            }
        ],
        handler=handle_signed_payment_mandate,
        name="PaymentRecordAutoCreator"
    )

    logger.info("✅ Payment listeners registered")


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

"""Tools used by the merchant agent.

Each agent uses individual tools to handle distinct tasks throughout the
shopping and purchasing process.
"""

import base64
import json
import logging

from pydantic import ValidationError
from typing import Any

from a2a.server.tasks.task_updater import TaskUpdater
from a2a.types import DataPart
from a2a.types import Part
from a2a.types import Task
from a2a.types import TextPart

from . import storage
from ap2.types.contact_picker import ContactAddress
from ap2.types.mandate import CART_MANDATE_DATA_KEY
from ap2.types.mandate import PAYMENT_MANDATE_DATA_KEY
from ap2.types.mandate import PaymentMandate
from ap2.types.payment_request import PaymentCurrencyAmount
from ap2.types.payment_request import PaymentItem
from common import message_utils
from common.a2a_extension_utils import EXTENSION_URI
from common.a2a_message_builder import A2aMessageBuilder
from common.payment_remote_a2a_client import PaymentRemoteA2aClient

# A map of payment method types to their corresponding processor agent URLs.
# This is the set of linked Merchant Payment Processor Agents this Merchant
# is integrated with.
_PAYMENT_PROCESSORS_BY_PAYMENT_METHOD_TYPE = {
    "CARD": "http://localhost:8003/a2a/merchant_payment_processor_agent",
}

# A placeholder for a JSON Web Token (JWT) used for merchant authorization.
_FAKE_JWT = "eyJhbGciOiJSUzI1NiIsImtpZIwMjQwOTA..."


async def update_cart(
    data_parts: list[dict[str, Any]],
    updater: TaskUpdater,
    current_task: Task | None,
    debug_mode: bool = False,
) -> None:
  """Updates an existing cart after a shipping address is provided.

  Args:
    data_parts: A list of data part contents from the request.
    updater: The TaskUpdater instance to add artifacts and complete the task.
    current_task: The current task -- not used in this function.
    debug_mode: Whether the agent is in debug mode.
  """
  cart_id = message_utils.find_data_part("cart_id", data_parts)
  if not cart_id:
    await _fail_task(updater, "Missing cart_id.")
    return

  # Extract shopping agent's signature
  cart_signature = message_utils.find_data_part("cart_signature", data_parts)
  if not cart_signature:
    await _fail_task(updater, "Missing cart_signature from Shopping Agent.")
    return

  shipping_address = message_utils.find_data_part(
      "shipping_address", data_parts
  )
  if not shipping_address:
    await _fail_task(updater, "Missing shipping_address.")
    return

  cart_mandate = storage.get_cart_mandate(cart_id)
  if not cart_mandate:
    await _fail_task(updater, f"CartMandate not found for cart_id: {cart_id}")
    return

  risk_data = storage.get_risk_data(updater.context_id)
  if not risk_data:
    await _fail_task(
        updater, f"Missing risk_data for context_id: {updater.context_id}"
    )
    return

  # Update the CartMandate with new shipping and tax cost.
  try:
    # Add the shipping address to the CartMandate:
    cart_mandate.contents.payment_request.shipping_address = (
        ContactAddress.model_validate(shipping_address)
    )

    # Add new shipping and tax costs to the PaymentRequest:
    tax_and_shipping_costs = [
        PaymentItem(
            label="Shipping",
            amount=PaymentCurrencyAmount(currency="USD", value=2.00),
        ),
        PaymentItem(
            label="Tax",
            amount=PaymentCurrencyAmount(currency="USD", value=1.50),
        ),
    ]

    payment_request = cart_mandate.contents.payment_request

    if payment_request.details.display_items is None:
      payment_request.details.display_items = tax_and_shipping_costs
    else:
      payment_request.details.display_items.extend(tax_and_shipping_costs)

    # Recompute the total amount of the PaymentRequest:
    payment_request.details.total.amount.value = sum(
        item.amount.value for item in payment_request.details.display_items
    )

    # A base64url-encoded JSON Web Token (JWT) that digitally signs the cart
    # contents by the merchant's private key.
    cart_mandate.merchant_authorization = _FAKE_JWT

    # Write updated CartMandate to Mandate Ledger Service with both signatures
    from common.mandate_ledger_client import MandateLedgerClient
    from datetime import datetime, timezone
    import os

    ledger_client = MandateLedgerClient(
        base_url=os.getenv("MANDATE_LEDGER_SERVICE_URL", "http://localhost:5000"),
        api_key=os.getenv("MANDATE_LEDGER_API_KEY"),
        agent_id="merchant_agent_dev",
        agent_type="merchant-agent"
    )

    try:
      # Get transaction_id and entity_id from storage
      transaction_id = storage.get_transaction_id(updater.context_id)
      entity_id = storage.get_cart_mandate_entity_id(updater.context_id, cart_id)

      if not entity_id:
        # If entity_id not found, this cart wasn't written to ledger initially
        # Write it now with both signatures
        if not transaction_id:
          transaction_id = f"txn_{updater.context_id}"
          storage.set_transaction_id(updater.context_id, transaction_id)

        # Create merchant signature
        merchant_signature = {
            "signature": cart_mandate.merchant_authorization,
            "signer_id": "merchant_agent_dev",
            "signer_type": "merchant-agent",
            "algorithm": "JWT",
            "signed_at": datetime.now(timezone.utc).isoformat()
        }

        ledger_entry = await ledger_client.create_mandate(
            mandate_type="CartMandate",
            mandate_data=cart_mandate.model_dump(),
            transaction_id=transaction_id,
            initial_signatures=[cart_signature, merchant_signature],
            initial_status="signed",
            idempotency_key=f"cart_signed_{cart_id}",
            metadata={
                "source": "merchant_agent",
                "context_id": updater.context_id,
                "cart_id": cart_id,
                "updated_with_shipping": True
            }
        )

        storage.set_cart_mandate_entity_id(updater.context_id, cart_id, ledger_entry["entity_id"])

        # Cache cart signature for fast payment record creation
        storage.set_cart_signature(updater.context_id, cart_id, cart_signature)

        # Store chosen cart_id for this shopping session
        storage.set_chosen_cart_id(updater.context_id, cart_id)
      else:
        # Update existing CartMandate in ledger (create new version)
        # This would require a PUT endpoint, for now we'll create a new entry
        # with the updated data and both signatures
        if not transaction_id:
          transaction_id = f"txn_{updater.context_id}"

        merchant_signature = {
            "signature": cart_mandate.merchant_authorization,
            "signer_id": "merchant_agent_dev",
            "signer_type": "merchant-agent",
            "algorithm": "JWT",
            "signed_at": datetime.now(timezone.utc).isoformat()
        }

        # For now, create a new entry (ideally should be PUT to update)
        ledger_entry = await ledger_client.create_mandate(
            mandate_type="CartMandate",
            mandate_data=cart_mandate.model_dump(),
            transaction_id=transaction_id,
            initial_signatures=[cart_signature, merchant_signature],
            initial_status="signed",
            idempotency_key=f"cart_signed_updated_{cart_id}",
            metadata={
                "source": "merchant_agent",
                "context_id": updater.context_id,
                "cart_id": cart_id,
                "updated_with_shipping": True,
                "replaces_entity_id": entity_id
            }
        )

        # Update stored entity_id
        storage.set_cart_mandate_entity_id(updater.context_id, cart_id, ledger_entry["entity_id"])

        # Cache cart signature for fast payment record creation
        storage.set_cart_signature(updater.context_id, cart_id, cart_signature)

        # Store chosen cart_id for this shopping session
        storage.set_chosen_cart_id(updater.context_id, cart_id)

    except Exception as e:
      # CRITICAL: If ledger write fails, we must fail the task to maintain data integrity
      import logging
      logging.error(f"Failed to write updated CartMandate to ledger: {e}")
      await _fail_task(updater, f"Failed to create/update CartMandate in ledger: {str(e)}")
      return

    await updater.add_artifact([
        Part(
            root=DataPart(
                data={CART_MANDATE_DATA_KEY: cart_mandate.model_dump()}
            )
        ),
        Part(root=DataPart(data={"risk_data": risk_data})),
    ])
    await updater.complete()

  except ValidationError as e:
    await _fail_task(updater, f"Invalid CartMandate after update: {e}")


async def _create_payment_record(
    updater: TaskUpdater,
    payment_mandate: PaymentMandate,
    transaction_id: str
) -> dict:
  """Create payment record in payments collection using cached signatures.

  This function is called after successful payment processing to create
  an ultra-lean payment record with references to all three mandates and
  their signatures (retrieved from cache for performance).

  Args:
    updater: The TaskUpdater instance.
    payment_mandate: The PaymentMandate that was processed.
    transaction_id: The transaction ID linking all mandates.
  """
  from common.mandate_ledger_client import MandateLedgerClient
  import os

  ledger_client = MandateLedgerClient(
      base_url=os.getenv("MANDATE_LEDGER_SERVICE_URL", "http://localhost:5000"),
      api_key=os.getenv("MANDATE_LEDGER_API_KEY"),
      agent_id="merchant_agent_dev",
      agent_type="merchant-agent"
  )

  # Get cached signatures (fast! ~1ms per lookup)
  intent_sig = storage.get_intent_signature(updater.context_id)
  cart_id = storage.get_chosen_cart_id(updater.context_id)
  cart_sig = storage.get_cart_signature(updater.context_id, cart_id) if cart_id else None
  payment_mandate_id = payment_mandate.payment_mandate_contents.payment_mandate_id
  payment_sig = storage.get_payment_signature(payment_mandate_id)

  # Get entity IDs
  intent_entity_id = storage.get_intent_mandate_entity_id(updater.context_id)
  cart_entity_id = storage.get_cart_mandate_entity_id(updater.context_id, cart_id) if cart_id else None
  payment_entity_id = storage.get_payment_mandate_entity_id(payment_mandate_id)

  if not all([intent_sig, cart_sig, payment_sig, intent_entity_id, cart_entity_id, payment_entity_id]):
    import logging
    logging.warning(f"Missing cached data for payment record creation: "
                   f"intent_sig={bool(intent_sig)}, cart_sig={bool(cart_sig)}, "
                   f"payment_sig={bool(payment_sig)}, intent_id={bool(intent_entity_id)}, "
                   f"cart_id={bool(cart_entity_id)}, payment_id={bool(payment_entity_id)}")
    return

  # Create payment record with cached signatures
  result = await ledger_client.create_payment(
      transaction_id=transaction_id,
      intent_mandate_id=intent_entity_id,
      cart_mandate_id=cart_entity_id,
      payment_mandate_id=payment_entity_id,
      amount=payment_mandate.payment_mandate_contents.payment_details_total.amount.value,
      currency=payment_mandate.payment_mandate_contents.payment_details_total.amount.currency,
      status="SUCCESS",
      merchant_agent="merchant_agent_dev",
      payment_processor_agent="payment_processor",
      payment_method_type="CARD",
      metadata={
          "context_id": updater.context_id,
          "payment_mandate_id": payment_mandate_id
      }
  )
  return result


async def initiate_payment(
    data_parts: list[dict[str, Any]],
    updater: TaskUpdater,
    current_task: Task | None,
    debug_mode: bool = False,
) -> None:
  """Initiates a payment for a given payment mandate. Use to make a payment.

  Args:
    data_parts: The data parts from the request, expected to contain a
      PaymentMandate and optionally a challenge response.
    updater: The TaskUpdater instance for updating the task state.
    current_task: The current task, used to find the processor's task ID.
    debug_mode: Whether the agent is in debug mode.
  """
  payment_mandate = message_utils.parse_canonical_object(
      PAYMENT_MANDATE_DATA_KEY, data_parts, PaymentMandate
  )
  if not payment_mandate:
    await _fail_task(updater, "Missing payment_mandate.")
    return

  # Extract shopping agent's payment signature
  payment_signature = message_utils.find_data_part("payment_signature", data_parts)
  if not payment_signature:
    await _fail_task(updater, "Missing payment_signature from Shopping Agent.")
    return

  risk_data = message_utils.find_data_part("risk_data", data_parts)
  if not risk_data:
    await _fail_task(updater, "Missing risk_data.")
    return

  # Write PaymentMandate to Mandate Ledger Service
  from common.mandate_ledger_client import MandateLedgerClient
  import os

  ledger_client = MandateLedgerClient(
      base_url=os.getenv("MANDATE_LEDGER_SERVICE_URL", "http://localhost:5000"),
      api_key=os.getenv("MANDATE_LEDGER_API_KEY"),
      agent_id="merchant_agent_dev",
      agent_type="merchant-agent"
  )

  try:
    # Get transaction_id from storage
    transaction_id = storage.get_transaction_id(updater.context_id)
    if not transaction_id:
      transaction_id = f"txn_{updater.context_id}"
      storage.set_transaction_id(updater.context_id, transaction_id)

    # Write PaymentMandate to ledger (status: "created")
    payment_mandate_id = payment_mandate.payment_mandate_contents.payment_mandate_id
    ledger_entry = await ledger_client.create_mandate(
        mandate_type="PaymentMandate",
        mandate_data=payment_mandate.model_dump(),
        transaction_id=transaction_id,
        initial_signatures=[payment_signature],
        initial_status="created",
        idempotency_key=f"payment_{payment_mandate_id}",
        metadata={
            "source": "shopping_agent",
            "context_id": updater.context_id,
            "payment_mandate_id": payment_mandate_id
        }
    )

    # Store entity_id and cache signature for payment record creation
    storage.set_payment_mandate_entity_id(payment_mandate_id, ledger_entry["entity_id"])
    storage.set_payment_signature(payment_mandate_id, payment_signature)

  except Exception as e:
    # Don't fail the task if ledger write fails, just log it
    import logging
    logging.error(f"Failed to write PaymentMandate to ledger: {e}")

  payment_method_type = (
      payment_mandate.payment_mandate_contents.payment_response.method_name
  )
  processor_url = _PAYMENT_PROCESSORS_BY_PAYMENT_METHOD_TYPE.get(
      payment_method_type
  )

  if not processor_url:
    await _fail_task(
        updater, f"No payment processor found for method: {payment_method_type}"
    )
    return

  payment_processor_agent = PaymentRemoteA2aClient(
      name="payment_processor_agent",
      base_url=processor_url,
      required_extensions={
          EXTENSION_URI,
      },
  )

  message_builder = (
      A2aMessageBuilder()
      .set_context_id(updater.context_id)
      .add_text("initiate_payment")
      .add_data(PAYMENT_MANDATE_DATA_KEY, payment_mandate.model_dump())
      .add_data("risk_data", risk_data)
      .add_data("debug_mode", debug_mode)
  )

  challenge_response = (
      message_utils.find_data_part("challenge_response", data_parts) or ""
  )
  if challenge_response:
    message_builder.add_data("challenge_response", challenge_response)

  payment_processor_task_id = _get_payment_processor_task_id(current_task)
  if payment_processor_task_id:
    message_builder.set_task_id(payment_processor_task_id)

  task = await payment_processor_agent.send_a2a_message(message_builder.build())

  # After payment processor responds, create payment record if successful
  if task.status.state == "completed":
    try:
      payment_record = await _create_payment_record(updater, payment_mandate, transaction_id)

      # Add payment_id to the success message for the shopping agent
      success_message = updater.new_agent_message(
          parts=[
              Part(root=TextPart(text="Payment authorized successfully")),
              Part(root=DataPart(data={
                  "payment_status": "SUCCESS",
                  "payment_id": payment_record.get("payment_id"),
                  "transaction_id": transaction_id
              }))
          ]
      )
      await updater.update_status(state="completed", message=success_message)
      return

    except Exception as e:
      import logging
      logging.error(f"Failed to create payment record: {e}")

  await updater.update_status(
      state=task.status.state,
      message=task.status.message,
  )


async def dpc_finish(
    data_parts: list[dict[str, Any]],
    updater: TaskUpdater,
    current_task: Task | None,
) -> None:
  """Receives and validates a DPC response to finalize payment.

  This tool receives the Digital Payment Credential (DPC) response, in the form
  of an OpenID4VP JSON, validates it, and simulates payment finalization.

  Args:
    data_parts: A list of data part contents from the request.
    updater: The TaskUpdater instance to add artifacts and complete the task.
    current_task: The current task, not used in this function.
  """
  dpc_response = message_utils.find_data_part("dpc_response", data_parts)
  if not dpc_response:
    await _fail_task(updater, "Missing dpc_response.")
    return

  logging.info("Received DPC response for finalization: %s", dpc_response)

  # --- Sample validation and payment finalization logic ---
  # TODO: Validate the nonce, and other merchant-specific attributes from the
  # DPC response.
  # TODO: Pass the DPC response to the payment processor agent for validation.

  # Simulate payment finalization.
  await updater.add_artifact([
      Part(root=DataPart(data={
          "payment_status": "SUCCESS",
          "transaction_id": "txn_1234567890",
      }))
  ])
  await updater.complete()


def _get_payment_processor_task_id(task: Task | None) -> str | None:
  """Returns the task ID of the payment processor task, if it exists.

  Identified by assuming the first message with a task ID that is not the
  merchant's task ID is a payment processor message.
  """
  if task is None:
    return None
  for message in task.history:
    if message.task_id != task.id:
      return message.task_id
  return None


async def _fail_task(updater: TaskUpdater, error_text: str) -> None:
  """A helper function to fail a task with a given error message."""
  error_message = updater.new_agent_message(
      parts=[Part(root=TextPart(text=error_text))]
  )
  await updater.failed(message=error_message)

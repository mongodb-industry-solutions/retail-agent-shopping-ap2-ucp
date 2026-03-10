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

"""A sub-agent that offers items from its 'catalog'.

This agent fabricates catalog content based on the user's request.
"""

from datetime import datetime
from datetime import timedelta
from datetime import timezone
from typing import Any
import uuid

from a2a.server.tasks.task_updater import TaskUpdater
from a2a.types import DataPart
from a2a.types import Part
from a2a.types import Task
from a2a.types import TextPart
from google import genai
from pydantic import ValidationError

from .. import storage
from agents.ap2.types.mandate import CART_MANDATE_DATA_KEY
from agents.ap2.types.mandate import CartContents
from agents.ap2.types.mandate import CartMandate
from agents.ap2.types.mandate import INTENT_MANDATE_DATA_KEY
from agents.ap2.types.mandate import IntentMandate
from agents.ap2.types.payment_request import PaymentDetailsInit
from agents.ap2.types.payment_request import PaymentItem
from agents.ap2.types.payment_request import PaymentMethodData
from agents.ap2.types.payment_request import PaymentOptions
from agents.ap2.types.payment_request import PaymentRequest
from agents.common import message_utils
from agents.common.genai_client_manager import get_genai_client
from agents.common.system_utils import DEBUG_MODE_INSTRUCTIONS


async def find_items_workflow(
    data_parts: list[dict[str, Any]],
    updater: TaskUpdater,
    current_task: Task | None,
) -> None:
  """Finds products that match the user's IntentMandate."""
  llm_client = get_genai_client()

  intent_mandate = message_utils.parse_canonical_object(
      INTENT_MANDATE_DATA_KEY, data_parts, IntentMandate
  )

  # Extract signature from data_parts
  signature = message_utils.find_data_part("intent_signature", data_parts)
  if not signature:
    error_message = updater.new_agent_message(
        parts=[Part(root=TextPart(text="Missing intent_signature from Shopping Agent"))]
    )
    await updater.failed(message=error_message)
    return

  # Write IntentMandate to Mandate Ledger Service
  from agents.common.mandate_ledger_client import MandateLedgerClient
  import os

  ledger_client = MandateLedgerClient(
      base_url=os.getenv("MANDATE_LEDGER_SERVICE_URL", "http://localhost:5000"),
      api_key=os.getenv("MANDATE_LEDGER_API_KEY"),
      agent_id="merchant_agent_dev",
      agent_type="merchant-agent"
  )

  try:
    # Create a transaction ID for this shopping session
    transaction_id = f"txn_{updater.context_id}"
    storage.set_transaction_id(updater.context_id, transaction_id)

    # Write pre-signed IntentMandate to ledger
    ledger_entry = await ledger_client.create_mandate(
        mandate_type="IntentMandate",
        mandate_data=intent_mandate.model_dump(),
        transaction_id=transaction_id,
        initial_signatures=[signature],
        initial_status="signed",
        idempotency_key=f"intent_{updater.context_id}",
        metadata={
            "source": "shopping_agent",
            "context_id": updater.context_id
        }
    )

    # Store entity_id for later use (when creating CartMandate/PaymentMandate)
    storage.set_intent_mandate_entity_id(updater.context_id, ledger_entry["entity_id"])

    # Cache signature for fast payment record creation
    storage.set_intent_signature(updater.context_id, signature)

  except Exception as e:
    error_message = updater.new_agent_message(
        parts=[Part(root=TextPart(text=f"Failed to write IntentMandate to ledger: {str(e)}"))]
    )
    await updater.failed(message=error_message)
    return

  intent = intent_mandate.natural_language_description
  prompt = f"""
        Based on the user's request for '{intent}', your task is to generate 3
        complete, unique and realistic PaymentItem JSON objects.

        You MUST exclude all branding from the PaymentItem `label` field.

    %s
        """ % DEBUG_MODE_INSTRUCTIONS

  llm_response = llm_client.models.generate_content(
      model="gemini-2.5-flash",
      contents=prompt,
      config={
          "response_mime_type": "application/json",
          "response_schema": list[PaymentItem],
      }
  )
  try:
    items: list[PaymentItem] = llm_response.parsed

    current_time = datetime.now(timezone.utc)
    item_count = 0
    for item in items:
      item_count += 1
      await _create_and_add_cart_mandate_artifact(
          item, item_count, current_time, updater
      )
    risk_data = _collect_risk_data(updater)
    updater.add_artifact([
        Part(root=DataPart(data={"risk_data": risk_data})),
    ])
    await updater.complete()
  except ValidationError as e:
    error_message = updater.new_agent_message(
        parts=[Part(root=TextPart(text=f"Invalid CartMandate list: {e}"))]
    )
    await updater.failed(message=error_message)
    return


async def _create_and_add_cart_mandate_artifact(
    item: PaymentItem,
    item_count: int,
    current_time: datetime,
    updater: TaskUpdater,
) -> None:
  """Creates a CartMandate and adds it as an artifact."""
  payment_request = PaymentRequest(
      method_data=[
          PaymentMethodData(
              supported_methods="CARD",
              data={
                  "network": ["mastercard", "paypal", "amex"],
              },
          )
      ],
      details=PaymentDetailsInit(
          id=f"order_{item_count}",
          display_items=[item],
          total=PaymentItem(
              label="Total",
              amount=item.amount,
          ),
      ),
      options=PaymentOptions(request_shipping=True),
  )

  # Generate unique cart_id to prevent cross-session contamination
  unique_cart_id = f"cart_{updater.context_id}_{uuid.uuid4().hex[:8]}"

  cart_contents = CartContents(
      id=unique_cart_id,
      user_cart_confirmation_required=True,
      payment_request=payment_request,
      cart_expiry=(current_time + timedelta(minutes=30)).isoformat(),
      merchant_name="Generic Merchant",
  )

  cart_mandate = CartMandate(contents=cart_contents)

  storage.set_cart_mandate(cart_mandate.contents.id, cart_mandate)

  # Write initial CartMandate to Mandate Ledger Service (status: "proposed", no signatures)
  from agents.common.mandate_ledger_client import MandateLedgerClient
  import os

  ledger_client = MandateLedgerClient(
      base_url=os.getenv("MANDATE_LEDGER_SERVICE_URL", "http://localhost:5000"),
      api_key=os.getenv("MANDATE_LEDGER_API_KEY"),
      agent_id="merchant_agent_dev",
      agent_type="merchant-agent"
  )

  try:
    # Get transaction_id from storage (set during IntentMandate creation)
    transaction_id = storage.get_transaction_id(updater.context_id)
    if not transaction_id:
      transaction_id = f"txn_{updater.context_id}"
      storage.set_transaction_id(updater.context_id, transaction_id)

    # Write proposed CartMandate to ledger (no signatures yet)
    ledger_entry = await ledger_client.create_mandate(
        mandate_type="CartMandate",
        mandate_data=cart_mandate.model_dump(),
        transaction_id=transaction_id,
        initial_status="proposed",  # Status is "proposed" until user selects and shopping agent signs
        idempotency_key=f"cart_proposed_{cart_mandate.contents.id}",
        metadata={
            "source": "merchant_agent",
            "context_id": updater.context_id,
            "cart_id": cart_mandate.contents.id
        }
    )

    # Store entity_id for later updates
    storage.set_cart_mandate_entity_id(updater.context_id, cart_mandate.contents.id, ledger_entry["entity_id"])

  except Exception as e:
    # CRITICAL: If ledger write fails, we must fail the task to maintain data integrity
    import logging
    logging.error(f"Failed to write CartMandate to ledger: {e}")
    await updater.failed(message=updater.new_agent_message(
        parts=[Part(root=TextPart(text=f"Failed to create CartMandate in ledger: {str(e)}"))]
    ))
    return

  await updater.add_artifact([
      Part(
          root=DataPart(data={CART_MANDATE_DATA_KEY: cart_mandate.model_dump()})
      )
  ])


def _collect_risk_data(updater: TaskUpdater) -> dict:
  """Creates a risk_data in the tool_context."""
  # This is a fake risk data for demonstration purposes.
  risk_data = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...fake_risk_data"
  storage.set_risk_data(updater.context_id, risk_data)
  return risk_data

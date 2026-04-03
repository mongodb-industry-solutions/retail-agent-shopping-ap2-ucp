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

"""In-memory storage for CartMandates.

A CartMandate may be updated multiple times during the course of a shopping
journey. This storage system is used to persist CartMandates between
interactions between the shopper and merchant agents.
"""

from typing import Optional

from agents.ap2.types.mandate import CartMandate


def get_cart_mandate(cart_id: str) -> Optional[CartMandate]:
  """Get a cart mandate by cart ID."""
  return _store.get(cart_id)


def set_cart_mandate(cart_id: str, cart_mandate: CartMandate) -> None:
  """Set a cart mandate by cart ID."""
  _store[cart_id] = cart_mandate


def set_risk_data(context_id: str, risk_data: str) -> None:
  """Set risk data by context ID."""
  _store[context_id] = risk_data


def get_risk_data(context_id: str) -> Optional[str]:
  """Get risk data by context ID."""
  return _store.get(context_id)


def set_transaction_id(context_id: str, transaction_id: str) -> None:
  """Set transaction ID for a shopping session."""
  _store[f"txn_{context_id}"] = transaction_id


def get_transaction_id(context_id: str) -> Optional[str]:
  """Get transaction ID for a shopping session."""
  return _store.get(f"txn_{context_id}")


def set_intent_mandate_entity_id(context_id: str, entity_id: str) -> None:
  """Set the IntentMandate entity_id from the ledger."""
  _store[f"intent_entity_{context_id}"] = entity_id


def get_intent_mandate_entity_id(context_id: str) -> Optional[str]:
  """Get the IntentMandate entity_id for a shopping session."""
  return _store.get(f"intent_entity_{context_id}")


def set_cart_mandate_entity_id(context_id: str, cart_id: str, entity_id: str) -> None:
  """Set the CartMandate entity_id from the ledger."""
  _store[f"cart_entity_{context_id}_{cart_id}"] = entity_id


def get_cart_mandate_entity_id(context_id: str, cart_id: str) -> Optional[str]:
  """Get the CartMandate entity_id for a cart."""
  return _store.get(f"cart_entity_{context_id}_{cart_id}")


def set_payment_mandate_entity_id(payment_id: str, entity_id: str) -> None:
  """Set the PaymentMandate entity_id from the ledger."""
  _store[f"payment_entity_{payment_id}"] = entity_id


def get_payment_mandate_entity_id(payment_id: str) -> Optional[str]:
  """Get the PaymentMandate entity_id for a payment."""
  return _store.get(f"payment_entity_{payment_id}")


def set_intent_signature(context_id: str, signature: dict) -> None:
  """Cache intent mandate signature for fast payment record creation."""
  _store[f"intent_sig_{context_id}"] = signature


def get_intent_signature(context_id: str) -> Optional[dict]:
  """Get cached intent mandate signature."""
  return _store.get(f"intent_sig_{context_id}")


def set_cart_signature(context_id: str, cart_id: str, signature: dict) -> None:
  """Cache cart mandate signature for fast payment record creation."""
  _store[f"cart_sig_{context_id}_{cart_id}"] = signature


def get_cart_signature(context_id: str, cart_id: str) -> Optional[dict]:
  """Get cached cart mandate signature."""
  return _store.get(f"cart_sig_{context_id}_{cart_id}")


def set_payment_signature(payment_id: str, signature: dict) -> None:
  """Cache payment mandate signature for fast payment record creation."""
  _store[f"payment_sig_{payment_id}"] = signature


def get_payment_signature(payment_id: str) -> Optional[dict]:
  """Get cached payment mandate signature."""
  return _store.get(f"payment_sig_{payment_id}")


def set_chosen_cart_id(context_id: str, cart_id: str) -> None:
  """Store the chosen cart_id for a shopping session."""
  _store[f"chosen_cart_{context_id}"] = cart_id


def get_chosen_cart_id(context_id: str) -> Optional[str]:
  """Get the chosen cart_id for a shopping session."""
  return _store.get(f"chosen_cart_{context_id}")


def set_session_info(context_id: str, user_id: str, session_id: str) -> None:
  """Store session info for A2A agent tracking."""
  _store[f"session_{context_id}"] = {"user_id": user_id, "session_id": session_id}


def get_user_id(context_id: str) -> Optional[str]:
  """Get user_id for a context."""  
  import logging
  logger = logging.getLogger(__name__)
  logger.info(f"🔍 STORAGE_DEBUG: get_user_id called with context_id={context_id}")
  
  session_info = _store.get(f"session_{context_id}")
  logger.info(f"🔍 STORAGE_DEBUG: session_info retrieved: {session_info}")
  logger.info(f"🔍 STORAGE_DEBUG: _store keys: {list(_store.keys())}")
  
  result = session_info.get("user_id") if session_info else None
  logger.info(f"🔍 STORAGE_DEBUG: get_user_id returning: {result}")
  return result


def get_session_id(context_id: str) -> Optional[str]:
  """Get session_id for a context."""
  import logging
  logger = logging.getLogger(__name__)
  logger.info(f"🔍 STORAGE_DEBUG: get_session_id called with context_id={context_id}")
  
  session_info = _store.get(f"session_{context_id}")
  logger.info(f"🔍 STORAGE_DEBUG: session_info retrieved: {session_info}")
  
  result = session_info.get("session_id") if session_info else None
  logger.info(f"🔍 STORAGE_DEBUG: get_session_id returning: {result}")
  return result


_store = {}

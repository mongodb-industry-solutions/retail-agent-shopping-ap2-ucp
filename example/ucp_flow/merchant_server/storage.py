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
In-memory storage for UCP checkout sessions and mandates.

This is adapted from card_flow's storage.py but uses checkout_id as the
primary key instead of context_id (since we don't have A2A context).
"""

from typing import Optional
from ap2.types.mandate import CartMandate


# ============ Cart Mandate Storage ============

def get_cart_mandate(cart_id: str) -> Optional[CartMandate]:
    """Get a cart mandate by cart ID."""
    return _store.get(f"cart_{cart_id}")


def set_cart_mandate(cart_id: str, cart_mandate: CartMandate) -> None:
    """Set a cart mandate by cart ID."""
    _store[f"cart_{cart_id}"] = cart_mandate


# ============ Checkout Session Storage ============

def set_checkout_session(checkout_id: str, session_data: dict) -> None:
    """Store checkout session data."""
    _store[f"session_{checkout_id}"] = session_data


def get_checkout_session(checkout_id: str) -> Optional[dict]:
    """Get checkout session data."""
    return _store.get(f"session_{checkout_id}")


def update_checkout_session(checkout_id: str, updates: dict) -> None:
    """Update checkout session with new data."""
    session = get_checkout_session(checkout_id) or {}
    session.update(updates)
    set_checkout_session(checkout_id, session)


# ============ Transaction ID Storage ============

def set_transaction_id(checkout_id: str, transaction_id: str) -> None:
    """Set transaction ID for a checkout session."""
    _store[f"txn_{checkout_id}"] = transaction_id


def get_transaction_id(checkout_id: str) -> Optional[str]:
    """Get transaction ID for a checkout session."""
    return _store.get(f"txn_{checkout_id}")


# ============ Mandate Entity ID Storage (from AP2 Ledger) ============

def set_intent_mandate_entity_id(checkout_id: str, entity_id: str) -> None:
    """Set the IntentMandate entity_id from the ledger."""
    _store[f"intent_entity_{checkout_id}"] = entity_id


def get_intent_mandate_entity_id(checkout_id: str) -> Optional[str]:
    """Get the IntentMandate entity_id."""
    return _store.get(f"intent_entity_{checkout_id}")


def set_cart_mandate_entity_id(checkout_id: str, cart_id: str, entity_id: str) -> None:
    """Set the CartMandate entity_id from the ledger."""
    _store[f"cart_entity_{checkout_id}_{cart_id}"] = entity_id


def get_cart_mandate_entity_id(checkout_id: str, cart_id: str) -> Optional[str]:
    """Get the CartMandate entity_id."""
    return _store.get(f"cart_entity_{checkout_id}_{cart_id}")


def set_payment_mandate_entity_id(payment_id: str, entity_id: str) -> None:
    """Set the PaymentMandate entity_id from the ledger."""
    _store[f"payment_entity_{payment_id}"] = entity_id


def get_payment_mandate_entity_id(payment_id: str) -> Optional[str]:
    """Get the PaymentMandate entity_id."""
    return _store.get(f"payment_entity_{payment_id}")


# ============ Signature Caching ============

def set_intent_signature(checkout_id: str, signature: dict) -> None:
    """Cache intent mandate signature for payment record creation."""
    _store[f"intent_sig_{checkout_id}"] = signature


def get_intent_signature(checkout_id: str) -> Optional[dict]:
    """Get cached intent mandate signature."""
    return _store.get(f"intent_sig_{checkout_id}")


def set_cart_signature(checkout_id: str, cart_id: str, signature: dict) -> None:
    """Cache cart mandate signature for payment record creation."""
    _store[f"cart_sig_{checkout_id}_{cart_id}"] = signature


def get_cart_signature(checkout_id: str, cart_id: str) -> Optional[dict]:
    """Get cached cart mandate signature."""
    return _store.get(f"cart_sig_{checkout_id}_{cart_id}")


def set_payment_signature(payment_id: str, signature: dict) -> None:
    """Cache payment mandate signature for payment record creation."""
    _store[f"payment_sig_{payment_id}"] = signature


def get_payment_signature(payment_id: str) -> Optional[dict]:
    """Get cached payment mandate signature."""
    return _store.get(f"payment_sig_{payment_id}")


# ============ Chosen Cart Tracking ============

def set_chosen_cart_id(checkout_id: str, cart_id: str) -> None:
    """Store the chosen cart_id for a checkout session."""
    _store[f"chosen_cart_{checkout_id}"] = cart_id


def get_chosen_cart_id(checkout_id: str) -> Optional[str]:
    """Get the chosen cart_id for a checkout session."""
    return _store.get(f"chosen_cart_{checkout_id}")


# In-memory store
_store = {}


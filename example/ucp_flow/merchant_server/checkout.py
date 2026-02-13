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
UCP Checkout Endpoints with AP2 Ledger Integration.

This module implements the UCP checkout flow:
1. POST /checkout - Create checkout session, return merchant-signed cart
2. POST /checkout/{id}/confirm - Shopper confirms cart, merchant writes to ledger
3. POST /checkout/{id}/complete - Complete payment, write PaymentMandate to ledger

The AP2 Ledger integration is the same as card_flow - the merchant writes
all mandates on behalf of both parties.
"""

import os
import uuid
import logging
import hashlib
import base64
import json
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ap2.types.mandate import (
    CartMandate, CartContents, IntentMandate,
    PaymentMandate, PaymentMandateContents,
    CART_MANDATE_DATA_KEY
)
from ap2.types.payment_request import (
    PaymentRequest, PaymentDetailsInit, PaymentItem,
    PaymentMethodData, PaymentOptions, PaymentResponse,
    PaymentCurrencyAmount
)
from ap2.types.contact_picker import ContactAddress
from common.mandate_ledger_client import MandateLedgerClient

from . import storage

router = APIRouter(tags=["Checkout"])
logger = logging.getLogger(__name__)

# Fake JWT for merchant authorization (same as card_flow)
_FAKE_JWT = "eyJhbGciOiJSUzI1NiIsImtpZIwMjQwOTA..."


def _get_ledger_client() -> MandateLedgerClient:
    """Get configured ledger client."""
    return MandateLedgerClient(
        base_url=os.getenv("MANDATE_LEDGER_SERVICE_URL", "http://localhost:5000"),
        api_key=os.getenv("MANDATE_LEDGER_API_KEY"),
        agent_id="ucp_merchant",
        agent_type="merchant-agent"
    )


def _create_merchant_signature(data: dict) -> dict:
    """Create merchant signature for mandate."""
    return {
        "signature": _FAKE_JWT,
        "signer_id": "ucp_merchant",
        "signer_type": "merchant-agent",
        "algorithm": "JWT",
        "signed_at": datetime.now(timezone.utc).isoformat()
    }


# ============ Request/Response Models ============

class CheckoutCreateRequest(BaseModel):
    """Request to create a checkout session."""
    items: list[PaymentItem]
    intent_description: str
    shopper_id: Optional[str] = None
    intent_signature: Optional[dict] = None  # Shopper's signature on intent


class CheckoutCreateResponse(BaseModel):
    """Response with checkout session and merchant-signed cart."""
    checkout_id: str
    cart: dict
    merchant_authorization: str  # AP2: Merchant's signature on cart
    intent_mandate_id: Optional[str] = None


class CartConfirmRequest(BaseModel):
    """Request to confirm cart selection."""
    cart_id: str
    cart_signature: dict  # Shopper's signature on cart
    shipping_address: Optional[dict] = None


class CartConfirmResponse(BaseModel):
    """Response after cart confirmation."""
    checkout_id: str
    cart_id: str
    cart_mandate_id: str  # Entity ID from AP2 ledger
    status: str
    payment_methods: list[str]


class CompleteCheckoutRequest(BaseModel):
    """Request to complete checkout with payment."""
    payment_method: str
    payment_details: dict
    payment_signature: dict  # Shopper's signature on payment authorization


class CompleteCheckoutResponse(BaseModel):
    """Response after successful payment."""
    checkout_id: str
    order_id: str
    payment_id: str
    transaction_id: str
    status: str
    receipt: dict


# ============ Checkout Endpoints ============

@router.post("/checkout", response_model=CheckoutCreateResponse)
async def create_checkout(request: CheckoutCreateRequest):
    """
    Create a new checkout session.
    
    UCP + AP2 Flow:
    1. Receive items and intent from shopper
    2. Create IntentMandate and write to AP2 Ledger (with shopper's signature)
    3. Build cart with payment details
    4. Sign cart with merchant key (merchant_authorization)
    5. Return checkout_id + signed cart
    
    The shopper will display this to the user for confirmation.
    """
    checkout_id = f"ucp_checkout_{uuid.uuid4().hex[:12]}"
    transaction_id = f"txn_{checkout_id}"
    
    logger.info(f"Creating checkout: {checkout_id}")
    logger.info(f"  Items: {len(request.items)}")
    logger.info(f"  Intent: {request.intent_description}")
    
    try:
        ledger_client = _get_ledger_client()
        
        # 1. Create IntentMandate
        intent_mandate = IntentMandate(
            user_cart_confirmation_required=True,
            natural_language_description=request.intent_description,
            intent_expiry=(datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
        )
        
        # 2. Write IntentMandate to AP2 Ledger
        intent_signatures = []
        if request.intent_signature:
            intent_signatures.append(request.intent_signature)
        
        intent_entry = await ledger_client.create_mandate(
            mandate_type="IntentMandate",
            mandate_data=intent_mandate.model_dump(),
            transaction_id=transaction_id,
            initial_signatures=intent_signatures if intent_signatures else None,
            initial_status="signed" if intent_signatures else "created",
            idempotency_key=f"intent_{checkout_id}",
            metadata={
                "source": "ucp_merchant",
                "checkout_id": checkout_id,
                "shopper_id": request.shopper_id
            }
        )
        
        logger.info(f"  IntentMandate created: {intent_entry['entity_id']}")
        
        # Store in session
        storage.set_transaction_id(checkout_id, transaction_id)
        storage.set_intent_mandate_entity_id(checkout_id, intent_entry['entity_id'])
        if request.intent_signature:
            storage.set_intent_signature(checkout_id, request.intent_signature)
        
        # 3. Build cart (similar to card_flow catalog_agent)
        cart_id = f"cart_{checkout_id}_{uuid.uuid4().hex[:8]}"
        
        total_value = sum(item.amount.value for item in request.items)
        
        payment_request = PaymentRequest(
            method_data=[
                PaymentMethodData(
                    supported_methods="CARD",
                    data={"network": ["mastercard", "visa", "amex"]}
                )
            ],
            details=PaymentDetailsInit(
                id=f"order_{checkout_id}",
                display_items=request.items,
                total=PaymentItem(
                    label="Total",
                    amount=PaymentCurrencyAmount(currency="USD", value=total_value)
                )
            ),
            options=PaymentOptions(request_shipping=True)
        )
        
        cart_contents = CartContents(
            id=cart_id,
            user_cart_confirmation_required=True,
            payment_request=payment_request,
            cart_expiry=(datetime.now(timezone.utc) + timedelta(minutes=30)).isoformat(),
            merchant_name="UCP Demo Merchant"
        )
        
        cart_mandate = CartMandate(
            contents=cart_contents,
            merchant_authorization=_FAKE_JWT  # Merchant signs the cart
        )
        
        # Store cart in memory
        storage.set_cart_mandate(cart_id, cart_mandate)
        
        # Store session data
        storage.set_checkout_session(checkout_id, {
            "status": "created",
            "cart_id": cart_id,
            "intent_mandate_id": intent_entry['entity_id'],
            "transaction_id": transaction_id,
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        
        logger.info(f"  Cart created: {cart_id}")
        
        return CheckoutCreateResponse(
            checkout_id=checkout_id,
            cart=cart_mandate.model_dump(),
            merchant_authorization=_FAKE_JWT,
            intent_mandate_id=intent_entry['entity_id']
        )
        
    except Exception as e:
        logger.error(f"Checkout creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/checkout/{checkout_id}/confirm", response_model=CartConfirmResponse)
async def confirm_cart(checkout_id: str, request: CartConfirmRequest):
    """
    Confirm cart selection and write to AP2 Ledger.
    
    UCP + AP2 Flow:
    1. Receive shopper's cart signature
    2. Update cart with shipping if provided
    3. Write CartMandate to AP2 Ledger with both signatures
    4. Return confirmation with available payment methods
    """
    logger.info(f"Confirming cart for checkout: {checkout_id}")
    
    session = storage.get_checkout_session(checkout_id)
    if not session:
        raise HTTPException(status_code=404, detail="Checkout session not found")
    
    cart_mandate = storage.get_cart_mandate(request.cart_id)
    if not cart_mandate:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    try:
        ledger_client = _get_ledger_client()
        transaction_id = storage.get_transaction_id(checkout_id)
        
        # Update shipping if provided
        if request.shipping_address:
            cart_mandate.contents.payment_request.shipping_address = (
                ContactAddress.model_validate(request.shipping_address)
            )
            
            # Add shipping and tax
            tax_and_shipping = [
                PaymentItem(
                    label="Shipping",
                    amount=PaymentCurrencyAmount(currency="USD", value=2.00)
                ),
                PaymentItem(
                    label="Tax",
                    amount=PaymentCurrencyAmount(currency="USD", value=1.50)
                )
            ]
            
            pr = cart_mandate.contents.payment_request
            if pr.details.display_items:
                pr.details.display_items.extend(tax_and_shipping)
            else:
                pr.details.display_items = tax_and_shipping
            
            # Recalculate total
            pr.details.total.amount.value = sum(
                item.amount.value for item in pr.details.display_items
            )
            
            storage.set_cart_mandate(request.cart_id, cart_mandate)
        
        # Create merchant signature
        merchant_signature = _create_merchant_signature(cart_mandate.model_dump())
        
        # Write CartMandate to AP2 Ledger with both signatures
        cart_entry = await ledger_client.create_mandate(
            mandate_type="CartMandate",
            mandate_data=cart_mandate.model_dump(),
            transaction_id=transaction_id,
            initial_signatures=[request.cart_signature, merchant_signature],
            initial_status="signed",
            idempotency_key=f"cart_signed_{request.cart_id}",
            metadata={
                "source": "ucp_merchant",
                "checkout_id": checkout_id,
                "cart_id": request.cart_id
            }
        )
        
        logger.info(f"  CartMandate created: {cart_entry['entity_id']}")
        
        # Store for later
        storage.set_cart_mandate_entity_id(checkout_id, request.cart_id, cart_entry['entity_id'])
        storage.set_cart_signature(checkout_id, request.cart_id, request.cart_signature)
        storage.set_chosen_cart_id(checkout_id, request.cart_id)
        
        # Update session
        storage.update_checkout_session(checkout_id, {
            "status": "confirmed",
            "cart_mandate_id": cart_entry['entity_id']
        })
        
        return CartConfirmResponse(
            checkout_id=checkout_id,
            cart_id=request.cart_id,
            cart_mandate_id=cart_entry['entity_id'],
            status="confirmed",
            payment_methods=["CARD"]
        )
        
    except Exception as e:
        logger.error(f"Cart confirmation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/checkout/{checkout_id}/complete", response_model=CompleteCheckoutResponse)
async def complete_checkout(checkout_id: str, request: CompleteCheckoutRequest):
    """
    Complete checkout with payment.
    
    UCP + AP2 Flow:
    1. Receive payment authorization with shopper's signature
    2. Create PaymentMandate and write to AP2 Ledger
    3. Process payment (simulated)
    4. Create Payment Record in AP2 Ledger
    5. Return receipt
    
    This is the final step - all mandates are now in the immutable ledger.
    """
    logger.info(f"Completing checkout: {checkout_id}")
    
    session = storage.get_checkout_session(checkout_id)
    if not session:
        raise HTTPException(status_code=404, detail="Checkout session not found")
    
    if session.get("status") != "confirmed":
        raise HTTPException(status_code=400, detail="Cart not confirmed")
    
    try:
        ledger_client = _get_ledger_client()
        transaction_id = storage.get_transaction_id(checkout_id)
        cart_id = storage.get_chosen_cart_id(checkout_id)
        cart_mandate = storage.get_cart_mandate(cart_id)
        
        if not cart_mandate:
            raise HTTPException(status_code=404, detail="Cart not found")
        
        # 1. Create PaymentMandate
        payment_mandate_id = f"payment_{uuid.uuid4().hex[:12]}"
        
        payment_mandate_contents = PaymentMandateContents(
            payment_mandate_id=payment_mandate_id,
            payment_details_id=cart_mandate.contents.payment_request.details.id,
            payment_details_total=cart_mandate.contents.payment_request.details.total,
            payment_response=PaymentResponse(
                request_id=cart_mandate.contents.payment_request.details.id,
                method_name=request.payment_method,
                details=request.payment_details
            ),
            merchant_agent="ucp_merchant"
        )
        
        payment_mandate = PaymentMandate(
            payment_mandate_contents=payment_mandate_contents
        )
        
        # 2. Write PaymentMandate to AP2 Ledger
        payment_entry = await ledger_client.create_mandate(
            mandate_type="PaymentMandate",
            mandate_data=payment_mandate.model_dump(),
            transaction_id=transaction_id,
            initial_signatures=[request.payment_signature],
            initial_status="authorized",
            idempotency_key=f"payment_{payment_mandate_id}",
            metadata={
                "source": "ucp_shopper",
                "checkout_id": checkout_id,
                "payment_mandate_id": payment_mandate_id
            }
        )
        
        logger.info(f"  PaymentMandate created: {payment_entry['entity_id']}")
        
        storage.set_payment_mandate_entity_id(payment_mandate_id, payment_entry['entity_id'])
        storage.set_payment_signature(payment_mandate_id, request.payment_signature)
        
        # 3. Process payment (simulated)
        logger.info("  Processing payment... (simulated)")
        
        # 4. Create Payment Record in AP2 Ledger
        intent_entity_id = storage.get_intent_mandate_entity_id(checkout_id)
        cart_entity_id = storage.get_cart_mandate_entity_id(checkout_id, cart_id)
        
        payment_record = await ledger_client.create_payment(
            transaction_id=transaction_id,
            intent_mandate_id=intent_entity_id,
            cart_mandate_id=cart_entity_id,
            payment_mandate_id=payment_entry['entity_id'],
            amount=cart_mandate.contents.payment_request.details.total.amount.value,
            currency=cart_mandate.contents.payment_request.details.total.amount.currency,
            status="SUCCESS",
            merchant_agent="ucp_merchant",
            payment_processor_agent="ucp_payment_processor",
            payment_method_type=request.payment_method,
            metadata={
                "checkout_id": checkout_id,
                "protocol": "UCP"
            }
        )
        
        logger.info(f"  Payment record created: {payment_record.get('payment_id')}")
        
        # 5. Update session - use transaction_id as order_id for consistent lookups
        # This allows the auditor agent to look up by either order_id or transaction_id
        order_id = transaction_id
        storage.update_checkout_session(checkout_id, {
            "status": "completed",
            "order_id": order_id,
            "payment_id": payment_record.get('payment_id'),
            "transaction_id": transaction_id,
            "completed_at": datetime.now(timezone.utc).isoformat()
        })
        
        return CompleteCheckoutResponse(
            checkout_id=checkout_id,
            order_id=order_id,  # Same as transaction_id for easy audit lookup
            payment_id=payment_record.get('payment_id', payment_mandate_id),
            transaction_id=transaction_id,
            status="SUCCESS",
            receipt={
                "items": [item.model_dump() for item in cart_mandate.contents.payment_request.details.display_items],
                "total": cart_mandate.contents.payment_request.details.total.model_dump(),
                "payment_method": request.payment_method,
                "order_id": order_id,
                "transaction_id": transaction_id,
                "payment_id": payment_record.get('payment_id'),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"Checkout completion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/checkout/{checkout_id}")
async def get_checkout_status(checkout_id: str):
    """Get the current status of a checkout session."""
    session = storage.get_checkout_session(checkout_id)
    if not session:
        raise HTTPException(status_code=404, detail="Checkout session not found")
    
    return {
        "checkout_id": checkout_id,
        **session
    }


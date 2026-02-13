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
Tools for the UCP Shopper Agent.

These tools use the UCP REST client instead of A2A protocol.
The agent can:
1. Discover merchant capabilities
2. Search for products
3. Create checkout and manage cart
4. Complete payment
"""

import os
from typing import Optional
from .ucp_client import UCPClient, create_signature

# Singleton client instance
_client: Optional[UCPClient] = None

# Session state (in-memory for demo)
_session = {
    "checkout_id": None,
    "cart_id": None,
    "cart": None,
    "merchant_authorization": None
}


def _get_client() -> UCPClient:
    """Get or create UCP client."""
    global _client
    if _client is None:
        merchant_url = os.getenv("UCP_MERCHANT_URL", "http://localhost:8004")
        _client = UCPClient(merchant_url)
    return _client


async def discover_merchant() -> dict:
    """
    Discover the merchant's capabilities via UCP.
    
    This fetches the merchant's /.well-known/ucp.json to understand
    what features are supported, including AP2 mandate support.
    
    Returns:
        Merchant profile with capabilities
    """
    client = _get_client()
    profile = await client.discover()
    
    # Check for AP2 support
    supports_ap2 = client.supports_ap2_mandate()
    
    return {
        "merchant_name": profile.get("name"),
        "capabilities": [c["name"] for c in profile.get("capabilities", [])],
        "supports_ap2_mandate": supports_ap2,
        "payment_methods": profile.get("payment_handlers", [])
    }


async def search_products(query: str) -> dict:
    """
    Search for products matching the user's request.
    
    Args:
        query: Natural language description of what to find
               (e.g., "coffee maker", "running shoes")
    
    Returns:
        List of matching products with prices
    """
    client = _get_client()
    result = await client.search_products(query, max_results=3)
    
    return {
        "query": result.get("query"),
        "products": result.get("products", []),
        "count": len(result.get("products", []))
    }


async def start_checkout(
    product_index: int,
    intent_description: str
) -> dict:
    """
    Start a checkout session for the selected product.
    
    This creates an IntentMandate and CartMandate on the merchant side,
    which are written to the AP2 Ledger.
    
    Args:
        product_index: Index of the selected product (1-based)
        intent_description: Description of what the user wants to buy
    
    Returns:
        Checkout session details with cart for confirmation
    """
    global _session
    
    client = _get_client()
    
    # Get products first
    products_result = await client.search_products(intent_description)
    products = products_result.get("products", [])
    
    if not products or product_index < 1 or product_index > len(products):
        return {"error": f"Invalid product index. Choose 1-{len(products)}"}
    
    selected_product = products[product_index - 1]
    
    # Create intent signature (shopper signs their intent)
    intent_data = {
        "intent": intent_description,
        "product": selected_product
    }
    intent_signature = create_signature(intent_data, "ucp_shopper")
    
    # Create checkout
    result = await client.create_checkout(
        items=[selected_product],
        intent_description=intent_description,
        shopper_id="demo_shopper",
        intent_signature=intent_signature
    )
    
    # Store session
    _session["checkout_id"] = result.get("checkout_id")
    _session["cart"] = result.get("cart")
    _session["cart_id"] = result.get("cart", {}).get("contents", {}).get("id")
    _session["merchant_authorization"] = result.get("merchant_authorization")
    
    return {
        "checkout_id": result.get("checkout_id"),
        "cart_id": _session["cart_id"],
        "product": selected_product,
        "total": result.get("cart", {}).get("contents", {}).get("payment_request", {}).get("details", {}).get("total"),
        "merchant_signed": bool(result.get("merchant_authorization")),
        "intent_mandate_id": result.get("intent_mandate_id"),
        "message": "Cart created. The merchant has signed it. Please confirm to proceed."
    }


async def confirm_cart(
    street: str = "123 Main St",
    city: str = "San Francisco",
    state: str = "CA",
    postal_code: str = "94102",
    country: str = "US"
) -> dict:
    """
    Confirm the cart and provide shipping address.
    
    This writes the CartMandate to the AP2 Ledger with both
    shopper and merchant signatures.
    
    Args:
        street: Street address
        city: City
        state: State/Province
        postal_code: Postal/ZIP code
        country: Country code
    
    Returns:
        Confirmation status with available payment methods
    """
    global _session
    
    if not _session["checkout_id"] or not _session["cart_id"]:
        return {"error": "No active checkout. Start a checkout first."}
    
    client = _get_client()
    
    # Create cart signature (shopper signs the cart)
    cart_signature = create_signature(_session["cart"], "ucp_shopper")
    
    shipping_address = {
        "address_line": [street],
        "city": city,
        "region": state,
        "postal_code": postal_code,
        "country": country
    }
    
    result = await client.confirm_cart(
        checkout_id=_session["checkout_id"],
        cart_id=_session["cart_id"],
        cart_signature=cart_signature,
        shipping_address=shipping_address
    )
    
    return {
        "checkout_id": result.get("checkout_id"),
        "cart_id": result.get("cart_id"),
        "cart_mandate_id": result.get("cart_mandate_id"),
        "status": result.get("status"),
        "payment_methods": result.get("payment_methods", ["CARD"]),
        "message": "Cart confirmed and signed. Ready for payment."
    }


async def complete_payment(
    card_number: str = "4111111111111111",
    expiry: str = "12/28",
    cvv: str = "123"
) -> dict:
    """
    Complete the payment to finish the checkout.
    
    This creates a PaymentMandate and Payment Record in the AP2 Ledger,
    completing the transaction with full audit trail.
    
    Args:
        card_number: Credit card number
        expiry: Expiry date (MM/YY)
        cvv: Security code
    
    Returns:
        Order confirmation with receipt
    """
    global _session
    
    if not _session["checkout_id"]:
        return {"error": "No active checkout. Start a checkout first."}
    
    client = _get_client()
    
    # Payment details (tokenized in production)
    payment_details = {
        "card_last_four": card_number[-4:],
        "card_network": "visa",
        "token": f"tok_{card_number[-4:]}"  # Mock token
    }
    
    # Create payment signature (shopper authorizes payment)
    payment_data = {
        "checkout_id": _session["checkout_id"],
        "cart_id": _session["cart_id"],
        "payment_method": "CARD",
        "amount": _session.get("cart", {}).get("contents", {}).get("payment_request", {}).get("details", {}).get("total")
    }
    payment_signature = create_signature(payment_data, "ucp_shopper")
    
    result = await client.complete_checkout(
        checkout_id=_session["checkout_id"],
        payment_method="CARD",
        payment_details=payment_details,
        payment_signature=payment_signature
    )
    
    # Clear session
    _session = {
        "checkout_id": None,
        "cart_id": None,
        "cart": None,
        "merchant_authorization": None
    }
    
    return {
        "status": result.get("status"),
        "order_id": result.get("order_id"),
        "payment_id": result.get("payment_id"),
        "transaction_id": result.get("transaction_id"),
        "receipt": result.get("receipt"),
        "message": "🎉 Payment complete! All mandates recorded in AP2 Ledger."
    }


async def get_checkout_status() -> dict:
    """
    Get the current status of the active checkout session.
    
    Returns:
        Current checkout state
    """
    if not _session["checkout_id"]:
        return {"status": "no_active_checkout"}
    
    client = _get_client()
    return await client.get_checkout_status(_session["checkout_id"])


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
UCP Client for communicating with UCP-compliant merchants.

This replaces the A2A client used in card_flow with standard HTTP REST calls.
The shopper agent uses this client to:
1. Discover merchant capabilities
2. Search for products
3. Create and complete checkout sessions
"""

import os
import httpx
import logging
from typing import Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# Default merchant URL (can be overridden via environment)
DEFAULT_MERCHANT_URL = os.getenv("UCP_MERCHANT_URL", "http://localhost:8004")


class UCPClient:
    """Client for UCP-compliant merchant servers."""
    
    def __init__(self, merchant_url: str = None):
        self.merchant_url = merchant_url or DEFAULT_MERCHANT_URL
        self.timeout = 30.0
        self._capabilities = None
        
    async def discover(self) -> dict:
        """
        Discover merchant capabilities via UCP well-known endpoint.
        
        Returns:
            UCP profile with capabilities, endpoints, signing keys
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(f"{self.merchant_url}/.well-known/ucp.json")
            resp.raise_for_status()
            self._capabilities = resp.json()
            
            logger.info(f"Discovered merchant: {self._capabilities.get('name')}")
            logger.info(f"  Capabilities: {[c['name'] for c in self._capabilities.get('capabilities', [])]}")
            
            return self._capabilities
    
    def supports_ap2_mandate(self) -> bool:
        """Check if merchant supports AP2 mandates."""
        if not self._capabilities:
            return False
        
        caps = self._capabilities.get("capabilities", [])
        return any(c.get("name") == "dev.ucp.shopping.ap2_mandate" for c in caps)
    
    async def search_products(self, query: str, max_results: int = 3) -> dict:
        """
        Search for products matching a query.
        
        Args:
            query: Natural language search query
            max_results: Maximum number of results
            
        Returns:
            Search results with products
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(
                f"{self.merchant_url}/api/products",
                params={"q": query, "max_results": max_results}
            )
            resp.raise_for_status()
            return resp.json()
    
    async def create_checkout(
        self,
        items: list[dict],
        intent_description: str,
        shopper_id: str = None,
        intent_signature: dict = None
    ) -> dict:
        """
        Create a new checkout session.
        
        Args:
            items: List of PaymentItem dictionaries
            intent_description: Natural language description of intent
            shopper_id: Optional shopper identifier
            intent_signature: Shopper's signature on intent
            
        Returns:
            Checkout response with checkout_id, cart, merchant_authorization
        """
        payload = {
            "items": items,
            "intent_description": intent_description,
            "shopper_id": shopper_id,
            "intent_signature": intent_signature
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(
                f"{self.merchant_url}/api/checkout",
                json=payload
            )
            resp.raise_for_status()
            result = resp.json()
            
            logger.info(f"Checkout created: {result.get('checkout_id')}")
            return result
    
    async def confirm_cart(
        self,
        checkout_id: str,
        cart_id: str,
        cart_signature: dict,
        shipping_address: dict = None
    ) -> dict:
        """
        Confirm cart selection with signature.
        
        Args:
            checkout_id: Checkout session ID
            cart_id: Cart ID to confirm
            cart_signature: Shopper's signature on cart
            shipping_address: Optional shipping address
            
        Returns:
            Confirmation response with cart_mandate_id
        """
        payload = {
            "cart_id": cart_id,
            "cart_signature": cart_signature,
            "shipping_address": shipping_address
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(
                f"{self.merchant_url}/api/checkout/{checkout_id}/confirm",
                json=payload
            )
            resp.raise_for_status()
            result = resp.json()
            
            logger.info(f"Cart confirmed: {result.get('cart_mandate_id')}")
            return result
    
    async def complete_checkout(
        self,
        checkout_id: str,
        payment_method: str,
        payment_details: dict,
        payment_signature: dict
    ) -> dict:
        """
        Complete checkout with payment.
        
        Args:
            checkout_id: Checkout session ID
            payment_method: Payment method (e.g., "CARD")
            payment_details: Payment method specific details
            payment_signature: Shopper's payment authorization signature
            
        Returns:
            Completion response with order_id, receipt
        """
        payload = {
            "payment_method": payment_method,
            "payment_details": payment_details,
            "payment_signature": payment_signature
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(
                f"{self.merchant_url}/api/checkout/{checkout_id}/complete",
                json=payload
            )
            resp.raise_for_status()
            result = resp.json()
            
            logger.info(f"Checkout completed: {result.get('order_id')}")
            return result
    
    async def get_checkout_status(self, checkout_id: str) -> dict:
        """Get current status of a checkout session."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(
                f"{self.merchant_url}/api/checkout/{checkout_id}"
            )
            resp.raise_for_status()
            return resp.json()


def create_signature(data: dict, signer_id: str = "ucp_shopper") -> dict:
    """
    Create a signature for mandate data.
    
    In production, this would use proper cryptographic signing (JWT/SD-JWT).
    For demo purposes, we create a mock signature structure.
    
    Args:
        data: Data to sign
        signer_id: Identifier of the signer
        
    Returns:
        Signature dictionary
    """
    import hashlib
    import json
    
    # Create a hash of the data (mock signature)
    data_str = json.dumps(data, sort_keys=True)
    data_hash = hashlib.sha256(data_str.encode()).hexdigest()
    
    return {
        "signature": f"sig_{data_hash[:32]}",  # Mock signature
        "signer_id": signer_id,
        "signer_type": "consumer-agent",
        "algorithm": "SHA256",
        "signed_at": datetime.now(timezone.utc).isoformat()
    }


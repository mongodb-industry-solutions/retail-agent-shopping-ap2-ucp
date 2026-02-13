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
UCP Well-Known Discovery Endpoint.

This endpoint allows shopping agents to discover the merchant's capabilities,
including support for AP2 mandates. This is the UCP equivalent of the
A2A agent.json file.

Reference: https://ucp.dev/specification/overview/
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter(tags=["Discovery"])


class UCPCapability(BaseModel):
    """A UCP capability declaration."""
    name: str
    version: str
    extends: Optional[str] = None


class UCPSigningKey(BaseModel):
    """A JWK public key for signature verification."""
    kid: str
    kty: str
    crv: str
    x: str
    y: str


class UCPService(BaseModel):
    """A UCP service declaration."""
    transport: str
    endpoint: str


class UCPProfile(BaseModel):
    """The complete UCP business profile."""
    name: str
    ucp_version: str
    capabilities: list[UCPCapability]
    services: dict[str, UCPService]
    payment_handlers: list[str]
    signing_keys: list[UCPSigningKey]


# Merchant's public signing key (for demo purposes)
# In production, this would be a real EC key pair
MERCHANT_SIGNING_KEY = UCPSigningKey(
    kid="merchant-demo-key-2026",
    kty="EC",
    crv="P-256",
    x="MKBCTNIcKUSDii11ySs3526iDZ8AiTo7Tu6KPAqv7D4",  # Demo key
    y="4Etl6SRW2YiLUrN5vfvVHuhp7x8PxltmWWlbbM4IFyM"   # Demo key
)


@router.get("/.well-known/ucp.json", response_model=UCPProfile)
async def ucp_discovery():
    """
    UCP Capability Discovery Endpoint.
    
    Shopping agents fetch this to discover:
    - What capabilities the merchant supports
    - Whether AP2 mandates are supported (dev.ucp.shopping.ap2_mandate)
    - Public keys for verifying merchant signatures
    - Endpoint URLs for API calls
    
    This is analogous to the agent.json in A2A, but uses UCP's standard format.
    """
    return UCPProfile(
        name="Demo UCP Merchant",
        ucp_version="2026-01-11",
        capabilities=[
            # Base checkout capability
            UCPCapability(
                name="dev.ucp.shopping.checkout",
                version="2026-01-11"
            ),
            # AP2 Mandate Extension - enables secure, auditable transactions
            UCPCapability(
                name="dev.ucp.shopping.ap2_mandate",
                version="2026-01-11",
                extends="dev.ucp.shopping.checkout"
            ),
            # Order management capability
            UCPCapability(
                name="dev.ucp.shopping.order",
                version="2026-01-11"
            )
        ],
        services={
            "shopping": UCPService(
                transport="rest",
                endpoint="/api"
            )
        },
        payment_handlers=["CARD", "GOOGLE_PAY"],
        signing_keys=[MERCHANT_SIGNING_KEY]
    )


@router.get("/.well-known/ucp.json/keys")
async def get_signing_keys():
    """
    Return merchant's public signing keys in JWK Set format.
    
    Used by shoppers to verify merchant_authorization signatures.
    """
    return {
        "keys": [MERCHANT_SIGNING_KEY.model_dump()]
    }


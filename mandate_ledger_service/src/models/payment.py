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
Payment Record Models - Ultra-Lean Design

Payment records contain ONLY:
- Payment identifiers (payment_id, transaction_id)
- Mandate references (ID + signature + timestamp)
- Payment summary (amount, currency, status)

All detailed mandate content is retrieved from the mandates collection using IDs.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class MandateReference(BaseModel):
    """
    Ultra-lean mandate reference.
    Contains only ID, signature, and timestamp - NO content.
    """
    mandate_id: str = Field(..., description="Mandate entity ID")
    signature: str = Field(..., description="Cryptographic signature")
    timestamp: str = Field(..., description="When mandate was signed (ISO 8601)")


class PaymentRecord(BaseModel):
    """
    Ultra-lean payment record - references only, NO content.

    To get full mandate details, query:
    GET /api/v1/mandates/{intent_mandate.mandate_id}
    GET /api/v1/mandates/{cart_mandate.mandate_id}
    GET /api/v1/mandates/{payment_mandate.mandate_id}
    """

    # Payment identifiers
    payment_id: str = Field(..., description="Unique payment ID (e.g., pay_xxx)")
    transaction_id: str = Field(..., description="Session/flow ID spanning all mandates")

    # User & session context
    user_id: Optional[str] = Field(None, description="User who initiated this payment")
    session_id: Optional[str] = Field(None, description="Session in which payment occurred")

    # Mandate references (ID + signature + timestamp ONLY)
    intent_mandate: MandateReference = Field(..., description="Intent mandate reference")
    cart_mandate: MandateReference = Field(..., description="Cart mandate reference")
    payment_mandate: MandateReference = Field(..., description="Payment mandate reference")

    # Payment summary (NOT in mandates)
    amount: float = Field(..., description="Payment amount")
    currency: str = Field(default="USD", description="Currency code")
    status: str = Field(..., description="Payment status (SUCCESS, FAILED, PENDING)")

    # Metadata
    merchant_agent: str = Field(..., description="Merchant agent ID")
    payment_processor_agent: str = Field(..., description="Payment processor agent ID")
    processed_at: datetime = Field(..., description="When payment was processed")

    # Optional
    payment_method_type: Optional[str] = Field(None, description="Payment method (card, wallet, etc.)")
    error_message: Optional[str] = Field(None, description="Error message if status=FAILED")
    metadata: Optional[dict] = Field(None, description="Additional metadata")


class PaymentResponse(BaseModel):
    """Response when retrieving a payment"""
    payment_id: str
    transaction_id: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    intent_mandate: MandateReference
    cart_mandate: MandateReference
    payment_mandate: MandateReference
    amount: float
    currency: str
    status: str
    merchant_agent: str
    payment_processor_agent: str
    processed_at: datetime
    payment_method_type: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Optional[dict] = None


class CreatePaymentRequest(BaseModel):
    """Request to manually create a payment record"""
    transaction_id: str = Field(..., description="Transaction ID")
    user_id: Optional[str] = Field(None, description="User who initiated this payment")
    session_id: Optional[str] = Field(None, description="Session in which payment occurred")
    intent_mandate_id: str = Field(..., description="Intent mandate entity ID")
    cart_mandate_id: str = Field(..., description="Cart mandate entity ID")
    payment_mandate_id: str = Field(..., description="Payment mandate entity ID")
    amount: float = Field(..., description="Payment amount")
    currency: str = Field(default="USD", description="Currency code")
    status: str = Field(..., description="Payment status (SUCCESS, FAILED, PENDING)")
    merchant_agent: str = Field(..., description="Merchant agent ID")
    payment_processor_agent: str = Field(..., description="Payment processor agent ID")
    payment_method_type: Optional[str] = Field(None, description="Payment method type")
    metadata: Optional[dict] = Field(None, description="Additional metadata")


class PaymentListResponse(BaseModel):
    """Response for listing payments"""
    payments: list[PaymentResponse]
    total_count: int


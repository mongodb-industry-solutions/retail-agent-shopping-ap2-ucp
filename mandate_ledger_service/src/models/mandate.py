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
Mandate-related Pydantic models.

These models wrap AP2 mandate types with ledger metadata.
"""

from datetime import datetime, timezone
from typing import Optional, Union
from pydantic import BaseModel, Field, field_validator

from src.types import IntentMandate, CartMandate, PaymentMandate
from src.models.enums import MandateType, MandateStatus


class SignatureEntry(BaseModel):
    """
    A cryptographic signature for a mandate version.

    Signatures prove that an agent attested to the mandate content.
    Multiple agents can sign the same mandate version.
    """

    signature: str = Field(
        ...,
        description="The cryptographic signature (hex string, JWT, or verifiable credential)"
    )
    signer_id: str = Field(
        ...,
        description="Agent ID that created this signature"
    )
    signer_type: str = Field(
        ...,
        description="Type of agent (shopping_agent, merchant_agent, payment_processor)"
    )
    algorithm: str = Field(
        default="EdDSA",
        description="Signature algorithm (EdDSA, ES256, RS256, etc.)"
    )
    signed_at: datetime = Field(
        ...,
        description="When the signature was created (UTC)"
    )
    metadata: Optional[dict] = Field(
        None,
        description="Additional signature metadata (key ID, verification URL, etc.)"
    )


class MandateLedgerEntry(BaseModel):
    """
    A single version entry in the immutable mandate ledger.

    Every change to a mandate creates a new ledger entry with an incremented version.
    Entries are never modified or deleted - only appended.
    """

    # Identity & versioning
    entity_id: str = Field(
        ...,
        description="Unique identifier for the mandate entity (all versions share this ID)"
    )
    entity_type: MandateType = Field(
        ...,
        description="Type of mandate (IntentMandate, CartMandate, PaymentMandate)"
    )
    version: int = Field(
        ...,
        ge=1,
        description="Version number (starts at 1, increments with each change)"
    )

    # The actual AP2 mandate data (strict validation via AP2 types)
    mandate_data: Union[IntentMandate, CartMandate, PaymentMandate] = Field(
        ...,
        description="The validated AP2 mandate data"
    )

    # Status & lifecycle
    status: MandateStatus = Field(
        ...,
        description="Current status of this version"
    )

    # Chain integrity (blockchain-style)
    parent_version: Optional[int] = Field(
        None,
        description="Version number of the parent (None for v1)"
    )
    parent_version_hash: Optional[str] = Field(
        None,
        description="SHA-256 hash of parent version's canonical JSON (ensures chain integrity)"
    )
    current_version_hash: str = Field(
        ...,
        description="SHA-256 hash of this version's canonical JSON"
    )

    # Transaction context
    transaction_id: str = Field(
        ...,
        description="Transaction ID grouping related mandates (Intent + Cart + Payment)"
    )

    # Actor & audit
    created_by_agent: str = Field(
        ...,
        description="Agent ID that created this version (e.g., 'shopping-agent-123')"
    )
    created_by_agent_type: str = Field(
        default="unknown",
        description="Type of agent (shopping-agent, merchant-agent, payment-processor)"
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When this version was created (UTC)"
    )

    # Metadata
    metadata: dict = Field(
        default_factory=dict,
        description="Additional metadata (IP address, user agent, etc.)"
    )

    # Idempotency
    idempotency_key: Optional[str] = Field(
        None,
        description="Client-provided idempotency key to prevent duplicate operations"
    )

    # Signatures
    signatures: list[SignatureEntry] = Field(
        default_factory=list,
        description="Cryptographic signatures for this mandate version"
    )

    @field_validator("mandate_data")
    @classmethod
    def validate_mandate_type_matches(cls, v, info):
        """Ensure mandate_data type matches entity_type."""
        if "entity_type" not in info.data:
            return v

        entity_type = info.data["entity_type"]
        type_map = {
            MandateType.INTENT: IntentMandate,
            MandateType.CART: CartMandate,
            MandateType.PAYMENT: PaymentMandate,
        }

        expected_type = type_map[entity_type]
        if not isinstance(v, expected_type):
            raise ValueError(
                f"mandate_data must be {expected_type.__name__} for entity_type {entity_type}"
            )

        return v


class MandateCurrentState(BaseModel):
    """
    Denormalized current state of a mandate for fast queries.

    This is the "hot" data - latest version only.
    Optimized for read performance with all commonly queried fields.
    """

    # Identity (same as ledger entry)
    entity_id: str = Field(..., description="Mandate entity ID")
    entity_type: MandateType = Field(..., description="Mandate type")

    # Current version info
    current_version: int = Field(..., ge=1, description="Current version number")
    version: int = Field(..., ge=1, description="Alias for current_version (for compatibility)")
    status: MandateStatus = Field(..., description="Current status")

    # The current mandate data
    mandate_data: Union[IntentMandate, CartMandate, PaymentMandate] = Field(
        ...,
        description="Current mandate data"
    )

    # Transaction context
    transaction_id: str = Field(..., description="Transaction ID")

    # Audit trail summary
    created_at: datetime = Field(..., description="When first version was created")
    created_by_agent: str = Field(..., description="Agent that created v1")
    updated_at: datetime = Field(..., description="When current version was created")
    updated_by_agent: str = Field(..., description="Agent that created current version")

    # Integrity
    current_version_hash: str = Field(..., description="Hash of current version")

    # Denormalized fields for fast queries
    merchant_name: Optional[str] = Field(
        None,
        description="Merchant name (for CartMandate)"
    )
    total_amount: Optional[float] = Field(
        None,
        description="Total amount (for CartMandate/PaymentMandate)"
    )
    currency: Optional[str] = Field(
        None,
        description="Currency code (for CartMandate/PaymentMandate)"
    )

    # Metadata
    metadata: dict = Field(default_factory=dict, description="Additional metadata")

    # Signatures (for current version)
    signatures: list[SignatureEntry] = Field(
        default_factory=list,
        description="Signatures for the current version"
    )


class MandateCreateRequest(BaseModel):
    """Request model for creating a new mandate."""

    mandate_type: MandateType = Field(..., description="Type of mandate to create")
    mandate_data: Union[IntentMandate, CartMandate, PaymentMandate] = Field(
        ...,
        description="The mandate data (must match mandate_type)"
    )
    transaction_id: str = Field(..., description="Transaction ID")
    created_by_agent: str = Field(..., description="Agent ID creating this mandate")
    created_by_agent_type: str = Field(..., description="Agent type")
    idempotency_key: Optional[str] = Field(None, description="Idempotency key")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")


class MandateUpdateRequest(BaseModel):
    """Request model for updating an existing mandate."""

    expected_version: int = Field(
        ...,
        ge=1,
        description="Expected current version (for optimistic locking)"
    )
    mandate_data: Union[IntentMandate, CartMandate, PaymentMandate] = Field(
        ...,
        description="Updated mandate data"
    )
    new_status: Optional[MandateStatus] = Field(
        None,
        description="New status (if changing status)"
    )
    updated_by_agent: str = Field(..., description="Agent ID performing update")
    updated_by_agent_type: str = Field(..., description="Agent type")
    idempotency_key: Optional[str] = Field(None, description="Idempotency key")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")


class MandateSignRequest(BaseModel):
    """Request model for signing a mandate."""

    expected_version: int = Field(
        ...,
        ge=1,
        description="Expected current version (for optimistic locking)"
    )
    signature: str = Field(
        ...,
        description="Signature (JWT for CartMandate, verifiable credential for PaymentMandate)"
    )
    signed_by_agent: str = Field(..., description="Agent ID performing signature")
    signed_by_agent_type: str = Field(..., description="Agent type")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")


class MandateResponse(BaseModel):
    """Response model for mandate operations."""

    entity_id: str
    entity_type: MandateType
    version: int
    status: MandateStatus
    mandate_data: Union[IntentMandate, CartMandate, PaymentMandate]
    transaction_id: str
    created_at: datetime
    updated_at: datetime
    current_version_hash: str


class MandateHistoryResponse(BaseModel):
    """Response model for mandate version history."""

    entity_id: str
    entity_type: MandateType
    total_versions: int
    versions: list[dict]  # List of version summaries


class MandateSearchRequest(BaseModel):
    """Request model for searching mandates."""

    entity_type: Optional[MandateType] = None
    status: Optional[MandateStatus] = None
    transaction_id: Optional[str] = None
    created_by_agent: Optional[str] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    limit: int = Field(default=50, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


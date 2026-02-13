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
Authentication and authorization models.

API key management for agent authentication.
"""

from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field

from src.models.enums import ApiKeyStatus


class ApiKey(BaseModel):
    """
    API key for agent authentication.

    Keys are hashed before storage (never store plaintext).
    """

    # Identity
    key_id: str = Field(
        ...,
        description="Unique identifier for this API key"
    )
    key_hash: str = Field(
        ...,
        description="Bcrypt hash of the API key (never store plaintext)"
    )
    key_prefix: str = Field(
        ...,
        description="First 8 characters of the key (for identification)"
    )

    # Agent information
    agent_id: str = Field(
        ...,
        description="ID of the agent this key belongs to"
    )
    agent_type: str = Field(
        ...,
        description=(
            "Type of agent (free-form string, kebab-case recommended). "
            "Examples: 'shopping-agent', 'merchant-agent', or any custom type"
        ),
        min_length=1,
        max_length=100,
        pattern=r'^[a-z0-9-]+$'
    )
    agent_name: Optional[str] = Field(
        None,
        description="Human-readable name of the agent"
    )

    # Status
    status: ApiKeyStatus = Field(
        default=ApiKeyStatus.ACTIVE,
        description="Current status of this key"
    )

    # Lifecycle
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When this key was created"
    )
    created_by: str = Field(
        ...,
        description="Admin who created this key"
    )
    expires_at: Optional[datetime] = Field(
        None,
        description="When this key expires (None = never)"
    )
    revoked_at: Optional[datetime] = Field(
        None,
        description="When this key was revoked (None = not revoked)"
    )
    revoked_by: Optional[str] = Field(
        None,
        description="Admin who revoked this key"
    )

    # Usage tracking
    last_used_at: Optional[datetime] = Field(
        None,
        description="When this key was last used"
    )
    total_requests: int = Field(
        default=0,
        description="Total number of requests made with this key"
    )

    # Permissions (for future fine-grained access control)
    permissions: list[str] = Field(
        default_factory=list,
        description="List of permissions (e.g., ['mandates.create', 'mandates.read'])"
    )

    # Rate limiting
    rate_limit_per_minute: int = Field(
        default=60,
        description="Rate limit for this key (requests per minute)"
    )

    # Metadata
    metadata: dict = Field(
        default_factory=dict,
        description="Additional metadata"
    )


class ApiKeyCreateRequest(BaseModel):
    """Request model for creating a new API key."""

    agent_id: str = Field(..., description="Agent ID")
    agent_type: str = Field(
        ...,
        description=(
            "Type of agent (free-form string, kebab-case recommended). "
            "Examples: 'shopping-agent', 'merchant-agent', or any custom type"
        ),
        min_length=1,
        max_length=100,
        pattern=r'^[a-z0-9-]+$'
    )
    agent_name: str = Field(..., description="Agent name")
    expires_in_days: Optional[int] = Field(
        None,
        ge=1,
        description="Key expiration in days (None = never expires)"
    )
    rate_limit_per_minute: int = Field(
        default=60,
        ge=1,
        le=1000,
        description="Rate limit (requests per minute)"
    )
    permissions: list[str] = Field(
        default_factory=list,
        description="List of permissions"
    )
    metadata: dict = Field(default_factory=dict, description="Additional metadata")


class ApiKeyCreateResponse(BaseModel):
    """Response model for API key creation."""

    key_id: str
    api_key: str = Field(
        ...,
        description="The plaintext API key (ONLY shown once at creation)"
    )
    agent_id: str
    agent_name: str
    expires_at: Optional[datetime]
    rate_limit_per_minute: int

    class Config:
        json_schema_extra = {
            "example": {
                "key_id": "key_abc123",
                "api_key": "mlsk_1234567890abcdef1234567890abcdef",
                "agent_id": "shopping-agent-001",
                "agent_name": "Shopping Agent",
                "expires_at": "2026-11-14T00:00:00Z",
                "rate_limit_per_minute": 60
            }
        }


class ApiKeyListResponse(BaseModel):
    """Response model for listing API keys."""

    total_count: int
    keys: list[dict]  # Redacted key info (no hashes)


class AuthenticatedAgent(BaseModel):
    """
    Information about an authenticated agent.

    This is attached to requests after successful authentication.
    When used with Depends(), FastAPI will not include this in the
    request body schema - it's only used internally for dependency injection.
    """

    agent_id: str = Field(..., description="Agent ID")
    agent_type: str = Field(..., description="Agent type")
    key_id: str = Field(..., description="API key ID used for authentication")
    permissions: list[str] = Field(
        default_factory=list,
        description="List of permissions"
    )
    rate_limit_per_minute: int = Field(..., description="Rate limit for this agent")
    agent_name: Optional[str] = Field(None, description="Human-readable agent name")

    model_config = {"frozen": True}  # Make immutable for safety


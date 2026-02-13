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
Audit log models.

Complete audit trail of all operations in the system.
"""

from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field

from src.models.enums import EventType


class AuditLogEntry(BaseModel):
    """
    A single audit log entry.

    Immutable record of an event that occurred in the system.
    """

    # Event identification
    event_id: str = Field(
        ...,
        description="Unique identifier for this audit event"
    )
    event_type: EventType = Field(
        ...,
        description="Type of event that occurred"
    )

    # Entity tracking
    entity_id: Optional[str] = Field(
        None,
        description="ID of the entity this event relates to (mandate ID, API key ID, etc.)"
    )
    entity_type: Optional[str] = Field(
        None,
        description="Type of entity (IntentMandate, CartMandate, etc.)"
    )
    entity_version: Optional[int] = Field(
        None,
        description="Version of the entity when this event occurred"
    )

    # Transaction context
    transaction_id: Optional[str] = Field(
        None,
        description="Transaction ID grouping related events"
    )

    # Actor information
    actor_id: str = Field(
        ...,
        description="ID of the actor that performed this action"
    )
    actor_type: str = Field(
        ...,
        description=(
            "Type of actor (free-form string). "
            "Examples: 'shopping-agent', 'merchant-agent', 'system', 'admin', or any custom type"
        ),
        min_length=1,
        max_length=100
    )

    # Timestamp
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When this event occurred (UTC)"
    )

    # Event details
    details: dict = Field(
        default_factory=dict,
        description="Event-specific details (status changes, error messages, etc.)"
    )

    # Request context
    request_id: Optional[str] = Field(
        None,
        description="Request ID from the API call that triggered this event"
    )
    ip_address: Optional[str] = Field(
        None,
        description="IP address of the requester"
    )
    user_agent: Optional[str] = Field(
        None,
        description="User agent of the requester"
    )

    # Success/failure
    success: bool = Field(
        default=True,
        description="Whether the operation succeeded"
    )
    error_message: Optional[str] = Field(
        None,
        description="Error message if the operation failed"
    )

    # Metadata
    metadata: dict = Field(
        default_factory=dict,
        description="Additional metadata"
    )


class AuditLogSearchRequest(BaseModel):
    """Request model for searching audit logs."""

    event_type: Optional[EventType] = None
    entity_id: Optional[str] = None
    entity_type: Optional[str] = None
    transaction_id: Optional[str] = None
    actor_id: Optional[str] = None
    actor_type: Optional[str] = None
    success: Optional[bool] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


class AuditLogResponse(BaseModel):
    """Response model for audit log queries."""

    total_count: int
    logs: list[AuditLogEntry]


class EntityAuditTrailResponse(BaseModel):
    """Response model for entity-specific audit trail."""

    entity_id: str
    entity_type: str
    total_events: int
    events: list[AuditLogEntry]


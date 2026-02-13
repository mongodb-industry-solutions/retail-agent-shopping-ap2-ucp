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
Admin and system monitoring models.

Data consistency checks, health checks, and system statistics.
"""

from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field

from src.models.enums import ConsistencyIssueType


class ConsistencyCheckResult(BaseModel):
    """
    Result of a data consistency check.

    Stored for audit trail and trend analysis.
    """

    # Check identification
    check_id: str = Field(
        ...,
        description="Unique identifier for this consistency check"
    )
    check_timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When this check was performed"
    )

    # Results summary
    total_mandates_checked: int = Field(
        ...,
        ge=0,
        description="Total number of mandates checked"
    )
    issues_found: int = Field(
        ...,
        ge=0,
        description="Number of consistency issues found"
    )
    passed: bool = Field(
        ...,
        description="Whether the check passed (no issues found)"
    )

    # Issue details
    issues: list[dict] = Field(
        default_factory=list,
        description="List of consistency issues found"
    )

    # Performance
    duration_seconds: float = Field(
        ...,
        description="How long the check took to run"
    )

    # Metadata
    triggered_by: str = Field(
        ...,
        description="Who triggered this check (admin ID or 'system')"
    )
    metadata: dict = Field(
        default_factory=dict,
        description="Additional metadata"
    )


class ConsistencyIssue(BaseModel):
    """A single data consistency issue."""

    issue_type: ConsistencyIssueType = Field(
        ...,
        description="Type of consistency issue"
    )
    entity_id: str = Field(
        ...,
        description="ID of the entity with the issue"
    )
    description: str = Field(
        ...,
        description="Human-readable description of the issue"
    )
    severity: str = Field(
        ...,
        description="Severity level (low, medium, high, critical)"
    )
    auto_repairable: bool = Field(
        ...,
        description="Whether this issue can be automatically repaired"
    )
    details: dict = Field(
        default_factory=dict,
        description="Additional details about the issue"
    )


class ConsistencyRepairRequest(BaseModel):
    """Request model for repairing consistency issues."""

    check_id: str = Field(
        ...,
        description="ID of the consistency check that found the issues"
    )
    issue_ids: list[str] = Field(
        ...,
        description="List of issue IDs to repair"
    )
    dry_run: bool = Field(
        default=True,
        description="If True, simulate repair without making changes"
    )
    repaired_by: str = Field(
        ...,
        description="Admin ID performing the repair"
    )


class ConsistencyRepairResponse(BaseModel):
    """Response model for consistency repair operations."""

    check_id: str
    issues_repaired: int
    issues_failed: int
    dry_run: bool
    repair_details: list[dict]


class HealthCheckResponse(BaseModel):
    """Response model for health check endpoint."""

    status: str = Field(
        ...,
        description="Overall status (healthy, degraded, unhealthy)"
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When this health check was performed"
    )
    version: str = Field(
        ...,
        description="Service version"
    )

    # Component health
    database: dict = Field(
        ...,
        description="Database health (status, latency, connection_count)"
    )

    # Metrics
    uptime_seconds: float = Field(
        ...,
        description="Service uptime in seconds"
    )
    total_mandates: int = Field(
        ...,
        description="Total number of mandates in the system"
    )

    # Optional details
    details: Optional[dict] = Field(
        None,
        description="Additional health check details"
    )


class StorageStatsResponse(BaseModel):
    """Response model for storage statistics."""

    # Collection stats
    collections: dict = Field(
        ...,
        description="Stats for each collection (document count, size, indexes)"
    )

    # Overall stats
    total_documents: int = Field(
        ...,
        description="Total documents across all collections"
    )
    total_size_bytes: int = Field(
        ...,
        description="Total storage size in bytes"
    )
    total_indexes: int = Field(
        ...,
        description="Total number of indexes"
    )

    # Database info
    database_name: str = Field(
        ...,
        description="Name of the database"
    )
    mongodb_version: str = Field(
        ...,
        description="MongoDB server version"
    )

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When these stats were collected"
    )


class IdempotencyRecord(BaseModel):
    """
    Record for idempotent request handling.

    Prevents duplicate operations from retried requests.
    """

    idempotency_key: str = Field(
        ...,
        description="Client-provided idempotency key"
    )
    agent_id: str = Field(
        ...,
        description="Agent that made the request"
    )
    endpoint: str = Field(
        ...,
        description="API endpoint called"
    )

    # Response cached
    response_status_code: int = Field(
        ...,
        description="HTTP status code of the cached response"
    )
    response_body: dict = Field(
        ...,
        description="Cached response body"
    )

    # Metadata
    first_request_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When the first request was made"
    )
    expires_at: datetime = Field(
        ...,
        description="When this record expires (TTL)"
    )


class RateLimitRecord(BaseModel):
    """
    Rate limiting state for an API key.

    Tracks request counts in sliding time windows.
    """

    key_id: str = Field(
        ...,
        description="API key ID"
    )
    window_start: datetime = Field(
        ...,
        description="Start of the current time window"
    )
    request_count: int = Field(
        default=0,
        description="Number of requests in current window"
    )
    limit: int = Field(
        ...,
        description="Maximum requests allowed in window"
    )
    expires_at: datetime = Field(
        ...,
        description="When this window expires (TTL)"
    )


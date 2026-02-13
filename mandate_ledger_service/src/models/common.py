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
Common models and utilities shared across the API.

Pagination, error responses, and base models.
"""

from typing import Generic, TypeVar, Optional
from pydantic import BaseModel, Field


T = TypeVar('T')


class PaginationParams(BaseModel):
    """
    Query parameters for paginated requests.

    Example:
        ?limit=50&offset=100
    """

    limit: int = Field(
        default=50,
        ge=1,
        le=1000,
        description="Maximum number of items to return (1-1000)"
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Number of items to skip (for pagination)"
    )

    @property
    def skip(self) -> int:
        """Alias for offset (MongoDB uses 'skip')."""
        return self.offset


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Generic paginated response model.

    Example:
        {
            "total": 235,
            "limit": 50,
            "offset": 100,
            "has_more": true,
            "items": [...]
        }
    """

    total: int = Field(
        ...,
        description="Total number of items available"
    )
    limit: int = Field(
        ...,
        description="Maximum items returned in this response"
    )
    offset: int = Field(
        ...,
        description="Number of items skipped"
    )
    has_more: bool = Field(
        ...,
        description="Whether more items are available"
    )
    items: list[T] = Field(
        ...,
        description="List of items in this page"
    )

    @classmethod
    def create(
        cls,
        items: list[T],
        total: int,
        pagination: PaginationParams
    ) -> "PaginatedResponse[T]":
        """
        Create a paginated response from items and pagination params.

        Args:
            items: List of items for this page
            total: Total number of items available
            pagination: Pagination parameters used

        Returns:
            PaginatedResponse instance
        """
        has_more = (pagination.offset + len(items)) < total

        return cls(
            total=total,
            limit=pagination.limit,
            offset=pagination.offset,
            has_more=has_more,
            items=items
        )


class ErrorDetail(BaseModel):
    """
    Detailed error information.

    Example:
        {
            "field": "expected_version",
            "message": "Version mismatch",
            "code": "VERSION_CONFLICT"
        }
    """

    field: Optional[str] = Field(
        None,
        description="Field that caused the error (if applicable)"
    )
    message: str = Field(
        ...,
        description="Human-readable error message"
    )
    code: Optional[str] = Field(
        None,
        description="Machine-readable error code"
    )


class ErrorResponse(BaseModel):
    """
    Standard error response format.

    Example:
        {
            "error": {
                "message": "Mandate not found: mandate_123",
                "code": "MANDATE_NOT_FOUND",
                "details": {"entity_id": "mandate_123"},
                "errors": [...]
            }
        }
    """

    error: "ErrorInfo"


class ErrorInfo(BaseModel):
    """Error information."""

    message: str = Field(
        ...,
        description="Human-readable error message"
    )
    code: str = Field(
        ...,
        description="Machine-readable error code"
    )
    details: dict = Field(
        default_factory=dict,
        description="Additional context about the error"
    )
    errors: list[ErrorDetail] = Field(
        default_factory=list,
        description="List of detailed error information (for validation errors)"
    )


class SuccessResponse(BaseModel):
    """
    Generic success response.

    Example:
        {
            "success": true,
            "message": "Operation completed successfully"
        }
    """

    success: bool = Field(
        default=True,
        description="Whether the operation succeeded"
    )
    message: str = Field(
        ...,
        description="Success message"
    )
    data: Optional[dict] = Field(
        None,
        description="Optional additional data"
    )


class HealthStatus(BaseModel):
    """
    Health check status.

    Example:
        {
            "status": "healthy",
            "checks": {
                "database": "healthy",
                "cache": "healthy"
            }
        }
    """

    status: str = Field(
        ...,
        description="Overall status (healthy, degraded, unhealthy)"
    )
    checks: dict[str, str] = Field(
        default_factory=dict,
        description="Individual component health statuses"
    )
    version: Optional[str] = Field(
        None,
        description="Service version"
    )
    uptime_seconds: Optional[float] = Field(
        None,
        description="Service uptime in seconds"
    )


class SortOrder(BaseModel):
    """
    Sort order specification.

    Example:
        {
            "field": "created_at",
            "direction": "desc"
        }
    """

    field: str = Field(
        ...,
        description="Field to sort by"
    )
    direction: str = Field(
        default="asc",
        description="Sort direction (asc or desc)"
    )

    @property
    def mongodb_direction(self) -> int:
        """Convert to MongoDB sort direction (1 or -1)."""
        return -1 if self.direction.lower() == "desc" else 1





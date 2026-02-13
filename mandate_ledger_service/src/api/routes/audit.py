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
Audit API endpoints.

Provides access to audit logs and entity audit trails.
"""

from typing import Optional, Annotated
from datetime import datetime
from fastapi import APIRouter, Body, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel, Field

from src.api.dependencies import get_authenticated_agent, check_rate_limit
from src.repositories import AuditRepository
from src.models.auth import AuthenticatedAgent
from src.models.audit import AuditLogEntry
from src.models.enums import EventType
from src.models.common import ErrorResponse


router = APIRouter(prefix="/api/v1/audit", tags=["audit"])


# ==================== Request/Response Models ====================

class SearchAuditLogsRequest(BaseModel):
    """Request to search audit logs."""
    entity_id: Optional[str] = Field(None, description="Filter by entity ID")
    entity_type: Optional[str] = Field(None, description="Filter by entity type")
    actor_id: Optional[str] = Field(None, description="Filter by actor ID")
    event_type: Optional[EventType] = Field(None, description="Filter by event type")
    start_time: Optional[datetime] = Field(None, description="Filter from this time")
    end_time: Optional[datetime] = Field(None, description="Filter until this time")
    limit: Optional[int] = Field(100, ge=1, le=1000, description="Max results")
    offset: Optional[int] = Field(0, ge=0, description="Results offset")


class AuditTrailSummary(BaseModel):
    """Summary of audit trail for an entity."""
    entity_id: str
    entity_type: str
    total_events: int
    first_event_at: Optional[datetime]
    last_event_at: Optional[datetime]
    event_type_counts: dict[str, int]
    actor_counts: dict[str, int]


# ==================== Endpoints ====================

@router.post(
    "/logs/search",
    response_model=list[AuditLogEntry],
    responses={
        200: {"description": "Audit logs retrieved"},
        401: {"model": ErrorResponse, "description": "Authentication required"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"}
    },
    summary="Search audit logs",
    description="Query audit logs with filters for entity, actor, event type, and time range"
)
async def search_audit_logs(
    request_body: SearchAuditLogsRequest = Body(...),
    request: Request = None,
    response: Response = None,
    agent: AuthenticatedAgent = Depends(get_authenticated_agent),
    _rate_limit: None = Depends(check_rate_limit)
):
    """
    Search audit logs with flexible filters.

    - Filter by entity_id, entity_type, actor_id, event_type
    - Time range filtering (start_time to end_time)
    - Pagination support
    - Ordered by timestamp (newest first)
    """
    audit_repo = AuditRepository()

    try:
        logs, total_count = await audit_repo.search_logs(
            entity_id=request_body.entity_id,
            entity_type=request_body.entity_type,
            actor_id=request_body.actor_id,
            event_type=request_body.event_type,
            start_time=request_body.start_time,
            end_time=request_body.end_time,
            limit=request_body.limit,
            offset=request_body.offset
        )

        # Add rate limit headers
        if hasattr(request.state, 'rate_limit_remaining'):
            response.headers["X-RateLimit-Limit"] = str(request.state.rate_limit_limit)
            response.headers["X-RateLimit-Remaining"] = str(request.state.rate_limit_remaining)

        response.headers["X-Total-Count"] = str(total_count)

        return logs

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search audit logs: {str(e)}"
        )


@router.get(
    "/entities/{entity_id}/trail",
    response_model=list[AuditLogEntry],
    responses={
        200: {"description": "Audit trail retrieved"},
        401: {"model": ErrorResponse, "description": "Authentication required"},
        404: {"model": ErrorResponse, "description": "Entity not found"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"}
    },
    summary="Get entity audit trail",
    description="Returns complete audit trail for a specific entity (all events)"
)
async def get_entity_audit_trail(
    entity_id: str,
    request: Request = None,
    response: Response = None,
    agent: AuthenticatedAgent = Depends(get_authenticated_agent),
    _rate_limit: None = Depends(check_rate_limit),
    limit: Optional[int] = None,
    offset: Optional[int] = None
):
    """
    Get complete audit trail for an entity.

    - Returns all audit events for the entity
    - Ordered by timestamp (oldest to newest)
    - Pagination support
    - Shows who did what and when
    """
    audit_repo = AuditRepository()

    try:
        logs, total_count = await audit_repo.get_logs_by_entity(
            entity_id=entity_id,
            limit=limit,
            offset=offset
        )

        response.headers["X-Total-Count"] = str(total_count)
        results = logs

        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No audit trail found for entity: {entity_id}"
            )

        # Add rate limit headers
        if hasattr(request.state, 'rate_limit_remaining'):
            response.headers["X-RateLimit-Limit"] = str(request.state.rate_limit_limit)
            response.headers["X-RateLimit-Remaining"] = str(request.state.rate_limit_remaining)

        return results

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get audit trail: {str(e)}"
        )


@router.get(
    "/entities/{entity_id}/summary",
    response_model=AuditTrailSummary,
    responses={
        200: {"description": "Audit summary retrieved"},
        401: {"model": ErrorResponse, "description": "Authentication required"},
        404: {"model": ErrorResponse, "description": "Entity not found"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"}
    },
    summary="Get entity audit summary",
    description="Returns statistical summary of audit trail for an entity"
)
async def get_entity_audit_summary(
    entity_id: str,
    request: Request = None,
    response: Response = None,
    agent: AuthenticatedAgent = Depends(get_authenticated_agent),
    _rate_limit: None = Depends(check_rate_limit)
):
    """
    Get statistical summary of entity audit trail.

    - Total event count
    - First and last event timestamps
    - Event type distribution
    - Actor activity summary
    """
    audit_repo = AuditRepository()

    try:
        summary = await audit_repo.get_entity_activity_summary(entity_id)

        if not summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No audit trail found for entity: {entity_id}"
            )

        # Add rate limit headers
        if hasattr(request.state, 'rate_limit_remaining'):
            response.headers["X-RateLimit-Limit"] = str(request.state.rate_limit_limit)
            response.headers["X-RateLimit-Remaining"] = str(request.state.rate_limit_remaining)

        return AuditTrailSummary(**summary)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get audit summary: {str(e)}"
        )


@router.get(
    "/actors/{actor_id}/activity",
    response_model=list[AuditLogEntry],
    responses={
        200: {"description": "Actor activity retrieved"},
        401: {"model": ErrorResponse, "description": "Authentication required"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"}
    },
    summary="Get actor activity",
    description="Returns all actions performed by a specific actor (agent)"
)
async def get_actor_activity(
    actor_id: str,
    request: Request = None,
    response: Response = None,
    agent: AuthenticatedAgent = Depends(get_authenticated_agent),
    _rate_limit: None = Depends(check_rate_limit),
    limit: Optional[int] = 100,
    offset: Optional[int] = 0
):
    """
    Get all actions performed by an actor.

    - Returns audit logs for specific actor (agent)
    - Ordered by timestamp (newest first)
    - Pagination support
    - Useful for agent activity monitoring
    """
    audit_repo = AuditRepository()

    try:
        logs, total_count = await audit_repo.get_logs_by_actor(
            actor_id=actor_id,
            limit=limit,
            offset=offset
        )

        response.headers["X-Total-Count"] = str(total_count)
        results = logs

        # Add rate limit headers
        if hasattr(request.state, 'rate_limit_remaining'):
            response.headers["X-RateLimit-Limit"] = str(request.state.rate_limit_limit)
            response.headers["X-RateLimit-Remaining"] = str(request.state.rate_limit_remaining)

        return results

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get actor activity: {str(e)}"
        )


@router.get(
    "/recent",
    response_model=list[AuditLogEntry],
    responses={
        200: {"description": "Recent activity retrieved"},
        401: {"model": ErrorResponse, "description": "Authentication required"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"}
    },
    summary="Get recent activity",
    description="Returns most recent audit events across all entities"
)
async def get_recent_activity(
    request: Request = None,
    response: Response = None,
    agent: AuthenticatedAgent = Depends(get_authenticated_agent),
    _rate_limit: None = Depends(check_rate_limit),
    limit: int = 50
):
    """
    Get most recent audit events.

    - Returns N most recent events across all entities
    - Ordered by timestamp (newest first)
    - Useful for activity monitoring dashboard
    """
    audit_repo = AuditRepository()

    try:
        results = await audit_repo.get_recent_logs(limit=limit)

        # Add rate limit headers
        if hasattr(request.state, 'rate_limit_remaining'):
            response.headers["X-RateLimit-Limit"] = str(request.state.rate_limit_limit)
            response.headers["X-RateLimit-Remaining"] = str(request.state.rate_limit_remaining)

        return results

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get recent activity: {str(e)}"
        )


@router.get(
    "/stats/event-types",
    response_model=dict[str, int],
    responses={
        200: {"description": "Event type statistics"},
        401: {"model": ErrorResponse, "description": "Authentication required"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"}
    },
    summary="Get event type statistics",
    description="Returns count of audit events by event type"
)
async def get_event_type_stats(
    request: Request = None,
    response: Response = None,
    agent: AuthenticatedAgent = Depends(get_authenticated_agent),
    _rate_limit: None = Depends(check_rate_limit)
):
    """
    Get statistics by event type.

    - Returns count for each event type
    - Useful for monitoring system usage
    - Example: {"MANDATE_CREATED": 150, "MANDATE_SIGNED": 100, ...}
    """
    audit_repo = AuditRepository()

    try:
        stats = await audit_repo.count_logs_by_event_type()

        # Add rate limit headers
        if hasattr(request.state, 'rate_limit_remaining'):
            response.headers["X-RateLimit-Limit"] = str(request.state.rate_limit_limit)
            response.headers["X-RateLimit-Remaining"] = str(request.state.rate_limit_remaining)

        return stats

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get event type stats: {str(e)}"
        )




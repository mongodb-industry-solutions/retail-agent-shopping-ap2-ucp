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
Admin API endpoints.

Provides administrative endpoints for consistency checks, health monitoring,
and system statistics.
"""

from typing import Optional, Annotated
from fastapi import APIRouter, Body, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel, Field

from src.api.dependencies import get_authenticated_agent, check_rate_limit
from src.repositories import ConsistencyRepository
from src.models.auth import AuthenticatedAgent
from src.models.admin import ConsistencyCheckResult
from src.models.enums import ConsistencyIssueType
from src.models.common import ErrorResponse


router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


# ==================== Request/Response Models ====================

class ConsistencyCheckRequest(BaseModel):
    """Request to query consistency checks."""
    entity_id: Optional[str] = None
    entity_type: Optional[str] = None
    issue_type: Optional[ConsistencyIssueType] = None
    severity: Optional[str] = Field(None, pattern="^(info|warning|error|critical)$")
    resolved: Optional[bool] = None
    limit: Optional[int] = Field(100, ge=1, le=1000)


class ResolveConsistencyRequest(BaseModel):
    """Request to mark consistency issue as resolved."""
    entity_id: str
    issue_type: ConsistencyIssueType
    resolved_by: str
    resolution_notes: Optional[str] = None


class ConsistencyStatsResponse(BaseModel):
    """Consistency check statistics."""
    by_type: list[dict]
    by_severity: list[dict]
    resolved_vs_unresolved: list[dict]
    total_checks: int
    unresolved_count: int


# ==================== Endpoints ====================

@router.get(
    "/consistency-checks",
    response_model=list[ConsistencyCheckResult],
    responses={
        200: {"description": "Consistency checks retrieved"},
        401: {"model": ErrorResponse, "description": "Authentication required"},
        403: {"model": ErrorResponse, "description": "Admin access required"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"}
    },
    summary="Get consistency checks",
    description="Query consistency check results with optional filters"
)
async def get_consistency_checks(
    request: Request = None,
    response: Response = None,
    agent: AuthenticatedAgent = Depends(get_authenticated_agent),
    _rate_limit: None = Depends(check_rate_limit),
    entity_id: Optional[str] = None,
    entity_type: Optional[str] = None,
    issue_type: Optional[str] = None,
    severity: Optional[str] = None,
    resolved: Optional[bool] = None,
    limit: int = 100
):
    """
    Get consistency check results.

    - Filter by entity, type, severity
    - Show resolved or unresolved issues
    - Useful for monitoring data integrity

    Note: Requires admin permissions
    """
    # Check admin scope
    if "admin" not in agent.permissions and "admin:read" not in agent.permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    consistency_repo = ConsistencyRepository()

    try:
        # Convert issue_type string to enum if provided
        issue_type_enum = None
        if issue_type:
            try:
                issue_type_enum = ConsistencyIssueType(issue_type)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid issue_type: {issue_type}"
                )

        # Get unresolved or all issues
        if resolved is False or resolved is None:
            results = await consistency_repo.get_unresolved_issues(
                entity_id=entity_id,
                entity_type=entity_type,
                issue_type=issue_type_enum,
                severity=severity,
                limit=limit
            )
        else:
            # For resolved=True, we'd need a different method
            # For now, just get unresolved
            results = await consistency_repo.get_unresolved_issues(
                entity_id=entity_id,
                entity_type=entity_type,
                issue_type=issue_type_enum,
                severity=severity,
                limit=limit
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
            detail=f"Failed to get consistency checks: {str(e)}"
        )


@router.post(
    "/consistency-checks/resolve",
    response_model=dict,
    responses={
        200: {"description": "Consistency issue marked as resolved"},
        401: {"model": ErrorResponse, "description": "Authentication required"},
        403: {"model": ErrorResponse, "description": "Admin access required"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"}
    },
    summary="Resolve consistency issue",
    description="Mark a consistency issue as resolved with notes"
)
async def resolve_consistency_issue(
    request_body: ResolveConsistencyRequest = Body(...),
    request: Request = None,
    response: Response = None,
    agent: AuthenticatedAgent = Depends(get_authenticated_agent),
    _rate_limit: None = Depends(check_rate_limit)
):
    """
    Mark consistency issue as resolved.

    - Records who resolved it
    - Adds resolution notes
    - Updates resolved timestamp

    Note: Requires admin permissions
    """
    # Check admin scope
    if "admin" not in agent.permissions and "admin:write" not in agent.permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin write access required"
        )

    consistency_repo = ConsistencyRepository()

    try:
        modified_count = await consistency_repo.mark_resolved(
            entity_id=request_body.entity_id,
            issue_type=request_body.issue_type,
            resolved_by=request_body.resolved_by,
            resolution_notes=request_body.resolution_notes
        )

        # Add rate limit headers
        if hasattr(request.state, 'rate_limit_remaining'):
            response.headers["X-RateLimit-Limit"] = str(request.state.rate_limit_limit)
            response.headers["X-RateLimit-Remaining"] = str(request.state.rate_limit_remaining)

        return {
            "success": True,
            "issues_resolved": modified_count,
            "entity_id": request_body.entity_id,
            "issue_type": request_body.issue_type.value
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resolve consistency issue: {str(e)}"
        )


@router.get(
    "/consistency-checks/stats",
    response_model=ConsistencyStatsResponse,
    responses={
        200: {"description": "Consistency statistics retrieved"},
        401: {"model": ErrorResponse, "description": "Authentication required"},
        403: {"model": ErrorResponse, "description": "Admin access required"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"}
    },
    summary="Get consistency statistics",
    description="Returns statistics about consistency checks (by type, severity, resolution status)"
)
async def get_consistency_stats(
    request: Request = None,
    response: Response = None,
    agent: AuthenticatedAgent = Depends(get_authenticated_agent),
    _rate_limit: None = Depends(check_rate_limit)
):
    """
    Get consistency check statistics.

    - Breakdown by issue type
    - Breakdown by severity
    - Resolved vs unresolved counts

    Note: Requires admin permissions
    """
    # Check admin scope
    if "admin" not in agent.permissions and "admin:read" not in agent.permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    consistency_repo = ConsistencyRepository()

    try:
        stats = await consistency_repo.get_consistency_stats()

        # Calculate totals
        total_checks = sum(item.get('count', 0) for item in stats.get('resolved_vs_unresolved', []))
        unresolved_count = next(
            (item.get('count', 0) for item in stats.get('resolved_vs_unresolved', [])
             if item.get('_id') == 'unresolved'),
            0
        )

        # Add rate limit headers
        if hasattr(request.state, 'rate_limit_remaining'):
            response.headers["X-RateLimit-Limit"] = str(request.state.rate_limit_limit)
            response.headers["X-RateLimit-Remaining"] = str(request.state.rate_limit_remaining)

        return ConsistencyStatsResponse(
            by_type=stats.get('by_type', []),
            by_severity=stats.get('by_severity', []),
            resolved_vs_unresolved=stats.get('resolved_vs_unresolved', []),
            total_checks=total_checks,
            unresolved_count=unresolved_count
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get consistency stats: {str(e)}"
        )


@router.get(
    "/consistency-checks/{entity_id}/history",
    response_model=list[ConsistencyCheckResult],
    responses={
        200: {"description": "Consistency history retrieved"},
        401: {"model": ErrorResponse, "description": "Authentication required"},
        403: {"model": ErrorResponse, "description": "Admin access required"},
        404: {"model": ErrorResponse, "description": "Entity not found"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"}
    },
    summary="Get entity consistency history",
    description="Returns consistency check history for a specific entity"
)
async def get_entity_consistency_history(
    entity_id: str,
    request: Request = None,
    response: Response = None,
    agent: AuthenticatedAgent = Depends(get_authenticated_agent),
    _rate_limit: None = Depends(check_rate_limit),
    limit: Optional[int] = None
):
    """
    Get consistency check history for an entity.

    - All consistency checks for this entity
    - Includes resolved and unresolved
    - Ordered by check timestamp (newest first)

    Note: Requires admin permissions
    """
    # Check admin scope
    if "admin" not in agent.permissions and "admin:read" not in agent.permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    consistency_repo = ConsistencyRepository()

    try:
        results = await consistency_repo.get_entity_consistency_history(
            entity_id=entity_id,
            limit=limit
        )

        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No consistency checks found for entity: {entity_id}"
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
            detail=f"Failed to get consistency history: {str(e)}"
        )




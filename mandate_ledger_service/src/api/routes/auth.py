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
Auth API endpoints.

Provides API key management endpoints for creating, listing, and revoking keys.
"""

from typing import Optional, Annotated
from fastapi import APIRouter, Body, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel, Field

from src.api.dependencies import get_authenticated_agent, check_rate_limit
from src.services.auth_service import AuthService
from src.models.auth import AuthenticatedAgent, ApiKey
from src.models.common import ErrorResponse


router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


# ==================== Request/Response Models ====================

class CreateApiKeyRequest(BaseModel):
    """Request to create a new API key."""
    agent_id: str = Field(..., description="Agent identifier", min_length=1, max_length=200)
    agent_type: str = Field(
        ...,
        description="Type of agent (e.g., 'shopping-agent', 'merchant-agent')",
        min_length=1,
        max_length=100,
        pattern=r'^[a-z0-9-]+$'
    )
    scopes: list[str] = Field(
        ...,
        description="Permission scopes (e.g., ['mandate:read', 'mandate:write'])",
        min_items=1
    )
    expires_in_days: Optional[int] = Field(
        None,
        description="Optional expiration in days (default: no expiration)",
        ge=1,
        le=3650
    )
    metadata: Optional[dict] = Field(None, description="Optional metadata")


class CreateApiKeyResponse(BaseModel):
    """Response after creating an API key."""
    key_id: str
    api_key: str = Field(..., description="⚠️ SAVE THIS! Won't be shown again")
    key_prefix: str
    agent_id: str
    agent_type: str
    scopes: list[str]
    expires_at: Optional[str]
    created_at: str


class ApiKeyDetailResponse(BaseModel):
    """Detailed API key information (without plaintext key)."""
    key_id: str
    key_prefix: str
    agent_id: str
    agent_type: str
    scopes: list[str]
    is_active: bool
    created_at: str
    expires_at: Optional[str]
    revoked_at: Optional[str]
    revoked_by: Optional[str]
    revocation_reason: Optional[str]
    last_used_at: Optional[str]
    metadata: Optional[dict]


class RevokeApiKeyRequest(BaseModel):
    """Request to revoke an API key."""
    reason: Optional[str] = Field(None, description="Reason for revocation", max_length=500)


# ==================== Endpoints ====================

@router.post(
    "/api-keys",
    response_model=CreateApiKeyResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "API key created successfully"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        401: {"model": ErrorResponse, "description": "Authentication required"},
        403: {"model": ErrorResponse, "description": "Admin access required"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"}
    },
    summary="Create new API key",
    description="Creates a new API key for an agent with specified scopes and optional expiration"
)
async def create_api_key(
    request_body: CreateApiKeyRequest,
    request: Request = None,
    response: Response = None,
    agent: AuthenticatedAgent = Depends(get_authenticated_agent),
    _rate_limit: None = Depends(check_rate_limit)
):
    """
    Create a new API key.

    - Generates secure random key (mlsk_xxx format)
    - Stores bcrypt hash (never plaintext)
    - Returns plaintext key ONLY ONCE
    - Requires admin or admin:write scope

    ⚠️ IMPORTANT: Save the api_key from response immediately!
    It will not be shown again.
    """
    # Check admin scope
    if "admin" not in agent.permissions and "admin:write" not in agent.permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin write access required to create API keys"
        )

    auth_service = AuthService()

    try:
        # Create API key
        api_key_record, plaintext_key = await auth_service.create_api_key(
            agent_id=request_body.agent_id,
            agent_type=request_body.agent_type,
            scopes=request_body.scopes,
            created_by=agent.agent_id,
            expires_in_days=request_body.expires_in_days,
            metadata=request_body.metadata
        )

        # Build response
        result = CreateApiKeyResponse(
            key_id=api_key_record.key_id,
            api_key=plaintext_key,
            key_prefix=api_key_record.key_prefix,
            agent_id=api_key_record.agent_id,
            agent_type=api_key_record.agent_type,
            scopes=api_key_record.permissions,
            expires_at=api_key_record.expires_at.isoformat() if api_key_record.expires_at else None,
            created_at=api_key_record.created_at.isoformat()
        )

        # Add rate limit headers
        if hasattr(request.state, 'rate_limit_remaining'):
            response.headers["X-RateLimit-Limit"] = str(request.state.rate_limit_limit)
            response.headers["X-RateLimit-Remaining"] = str(request.state.rate_limit_remaining)

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create API key: {str(e)}"
        )


@router.get(
    "/api-keys",
    response_model=list[ApiKeyDetailResponse],
    responses={
        200: {"description": "API keys retrieved"},
        401: {"model": ErrorResponse, "description": "Authentication required"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"}
    },
    summary="List API keys",
    description="Lists API keys (agent sees their own, admin sees all)"
)
async def list_api_keys(
    request: Request = None,
    response: Response = None,
    agent_id: Optional[str] = None,
    include_revoked: bool = False,
    agent: AuthenticatedAgent = Depends(get_authenticated_agent),
    _rate_limit: None = Depends(check_rate_limit)
):
    """
    List API keys.

    - Agents see only their own keys
    - Admins can see all keys or filter by agent_id
    - Optional: include revoked keys
    """
    auth_service = AuthService()

    try:
        # Determine which agent's keys to list
        is_admin = "admin" in agent.permissions or "admin:read" in agent.permissions

        if agent_id and not is_admin:
            # Non-admin trying to list another agent's keys
            if agent_id != agent.agent_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cannot list other agents' keys"
                )

        target_agent_id = agent_id if is_admin else agent.agent_id

        # List keys
        keys = await auth_service.list_agent_keys(
            agent_id=target_agent_id,
            include_revoked=include_revoked
        )

        # Convert to response models
        results = [
            ApiKeyDetailResponse(
                key_id=key.key_id,
                key_prefix=key.key_prefix,
                agent_id=key.agent_id,
                agent_type=key.agent_type,
                scopes=key.permissions,
                is_active=(key.status == "active"),
                created_at=key.created_at.isoformat(),
                expires_at=key.expires_at.isoformat() if key.expires_at else None,
                revoked_at=key.revoked_at.isoformat() if key.revoked_at else None,
                revoked_by=key.revoked_by,
                revocation_reason=key.revocation_reason,
                last_used_at=key.last_used_at.isoformat() if key.last_used_at else None,
                metadata=key.metadata
            )
            for key in keys
        ]

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
            detail=f"Failed to list API keys: {str(e)}"
        )


@router.get(
    "/api-keys/{key_id}",
    response_model=ApiKeyDetailResponse,
    responses={
        200: {"description": "API key details retrieved"},
        401: {"model": ErrorResponse, "description": "Authentication required"},
        403: {"model": ErrorResponse, "description": "Access denied"},
        404: {"model": ErrorResponse, "description": "API key not found"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"}
    },
    summary="Get API key details",
    description="Get detailed information about a specific API key"
)
async def get_api_key_details(
    key_id: str,
    request: Request = None,
    response: Response = None,
    agent: AuthenticatedAgent = Depends(get_authenticated_agent),
    _rate_limit: None = Depends(check_rate_limit)
):
    """
    Get API key details.

    - Agents can view their own keys
    - Admins can view any key
    - Does NOT return plaintext key (never stored)
    - Shows usage statistics
    """
    auth_service = AuthService()

    try:
        # Get key
        key = await auth_service.auth_repo.get_api_key_by_id(key_id)

        if not key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"API key not found: {key_id}"
            )

        # Check permissions
        is_admin = "admin" in agent.permissions or "admin:read" in agent.permissions
        if not is_admin and key.agent_id != agent.agent_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot access other agents' keys"
            )

        # Build response
        result = ApiKeyDetailResponse(
            key_id=key.key_id,
            key_prefix=key.key_prefix,
            agent_id=key.agent_id,
            agent_type=key.agent_type,
            scopes=key.permissions,
            is_active=(key.status == "active"),
            created_at=key.created_at.isoformat(),
            expires_at=key.expires_at.isoformat() if key.expires_at else None,
            revoked_at=key.revoked_at.isoformat() if key.revoked_at else None,
            revoked_by=key.revoked_by,
            revocation_reason=None,  # TODO: Add to ApiKey model
            last_used_at=key.last_used_at.isoformat() if key.last_used_at else None,
            metadata=key.metadata
        )

        # Add rate limit headers
        if hasattr(request.state, 'rate_limit_remaining'):
            response.headers["X-RateLimit-Limit"] = str(request.state.rate_limit_limit)
            response.headers["X-RateLimit-Remaining"] = str(request.state.rate_limit_remaining)

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get API key details: {str(e)}"
        )


@router.delete(
    "/api-keys/{key_id}",
    response_model=dict,
    responses={
        200: {"description": "API key revoked successfully"},
        401: {"model": ErrorResponse, "description": "Authentication required"},
        403: {"model": ErrorResponse, "description": "Access denied"},
        404: {"model": ErrorResponse, "description": "API key not found"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"}
    },
    summary="Revoke API key",
    description="Revokes an API key (marks as inactive, cannot be undone)"
)
async def revoke_api_key(
    key_id: str,
    request: Request = None,
    response: Response = None,
    request_body: Optional[RevokeApiKeyRequest] = None,
    agent: AuthenticatedAgent = Depends(get_authenticated_agent),
    _rate_limit: None = Depends(check_rate_limit)
):
    """
    Revoke an API key.

    - Agents can revoke their own keys
    - Admins can revoke any key
    - Adds revocation reason to audit log
    - Cannot be undone (must create new key)
    """
    auth_service = AuthService()

    try:
        # Get key to check permissions
        key = await auth_service.auth_repo.get_api_key_by_id(key_id)

        if not key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"API key not found: {key_id}"
            )

        # Check permissions
        is_admin = "admin" in agent.permissions or "admin:write" in agent.permissions
        if not is_admin and key.agent_id != agent.agent_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot revoke other agents' keys"
            )

        # Revoke key
        reason = request_body.reason if request_body else None
        await auth_service.revoke_api_key(
            key_id=key_id,
            revoked_by=agent.agent_id,
            reason=reason
        )

        # Add rate limit headers
        if hasattr(request.state, 'rate_limit_remaining'):
            response.headers["X-RateLimit-Limit"] = str(request.state.rate_limit_limit)
            response.headers["X-RateLimit-Remaining"] = str(request.state.rate_limit_remaining)

        return {
            "success": True,
            "key_id": key_id,
            "message": "API key revoked successfully",
            "revoked_by": agent.agent_id,
            "reason": reason
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to revoke API key: {str(e)}"
        )


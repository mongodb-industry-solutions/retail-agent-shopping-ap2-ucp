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
Mandate API endpoints.

Handles CRUD operations for mandates (Intent, Cart, Payment).
"""

from typing import Optional, Annotated
from fastapi import APIRouter, Body, Depends, HTTPException, Request, Response, status, Header
from pydantic import BaseModel, Field

from src.api.dependencies import (
    get_authenticated_agent,
    check_rate_limit,
    check_idempotency
)
from src.services.mandate_service import MandateService
from src.repositories import IdempotencyRepository
from src.models.auth import AuthenticatedAgent
from src.models.mandate import MandateLedgerEntry, MandateCurrentState
from src.models.enums import MandateType, MandateStatus
from src.models.common import PaginationParams, ErrorResponse
from src.core.errors import (
    MandateNotFoundError,
    VersionConflictError,
    InvalidStateTransitionError,
    InvalidMandateDataError
)


router = APIRouter(prefix="/api/v1/mandates", tags=["mandates"])


# ==================== Request/Response Models ====================

class CreateMandateRequest(BaseModel):
    """Request to create a new mandate."""
    mandate_type: MandateType = Field(..., description="Type of mandate (INTENT, CART, PAYMENT)")
    mandate_data: dict = Field(..., description="AP2 mandate data")
    transaction_id: Optional[str] = Field(None, description="Optional transaction ID")
    user_id: Optional[str] = Field(None, description="User who owns this mandate")
    session_id: Optional[str] = Field(None, description="Session in which mandate was created")
    metadata: Optional[dict] = Field(None, description="Optional metadata")
    initial_signatures: Optional[list] = Field(None, description="Initial signatures (for pre-signed mandates)")
    initial_status: Optional[MandateStatus] = Field(None, description="Override initial status (e.g., 'signed' for pre-signed mandates)")


class CreateMandateResponse(BaseModel):
    """Response after creating a mandate."""
    entity_id: str
    version: int
    mandate_type: str
    status: str
    created_at: str
    created_by_agent: str


class SignMandateRequest(BaseModel):
    """Request to sign a mandate."""
    transaction_id: Optional[str] = Field(None, description="Optional transaction ID")
    signature_data: Optional[dict] = Field(None, description="Signature metadata")


class SearchMandatesRequest(BaseModel):
    """Request to search mandates."""
    mandate_type: Optional[MandateType] = None
    status: Optional[MandateStatus] = None
    created_by_agent: Optional[str] = None
    limit: Optional[int] = Field(50, ge=1, le=100)
    offset: Optional[int] = Field(0, ge=0)


# ==================== Endpoints ====================

@router.post(
    "",
    response_model=CreateMandateResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Mandate created successfully"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        401: {"model": ErrorResponse, "description": "Authentication required"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    },
    summary="Create a new mandate",
    description="Creates a new Intent, Cart, or Payment mandate with version 1"
)
async def create_mandate(
    request_body: CreateMandateRequest = Body(...),
    request: Request = None,
    response: Response = None,
    x_idempotency_key: Optional[str] = Header(None),
    agent: AuthenticatedAgent = Depends(get_authenticated_agent),
    _rate_limit: None = Depends(check_rate_limit)
):
    """
    Create a new mandate.

    - Supports idempotency via X-Idempotency-Key header
    - Rate limited per agent
    - Creates version 1 with initial status
    - Logs creation in audit trail
    """
    # Check for duplicate request via idempotency
    idempotency_record = None
    if x_idempotency_key:
        idempotency_repo = IdempotencyRepository()
        idempotency_record = await idempotency_repo.check_idempotency_key(
            idempotency_key=x_idempotency_key,
            agent_id=agent.agent_id
        )

    if idempotency_record:
        response.status_code = idempotency_record.response_status_code
        return idempotency_record.response_body

    mandate_service = MandateService()

    try:
        # Create mandate
        ledger_entry = await mandate_service.create_mandate(
            entity_type=request_body.mandate_type,
            mandate_data=request_body.mandate_data,
            created_by_agent=agent.agent_id,
            agent_type=agent.agent_type,
            transaction_id=request_body.transaction_id,
            metadata=request_body.metadata,
            initial_signatures=request_body.initial_signatures,
            initial_status=request_body.initial_status,
            user_id=request_body.user_id,
            session_id=request_body.session_id
        )

        # Build response
        result = CreateMandateResponse(
            entity_id=ledger_entry.entity_id,
            version=ledger_entry.version,
            mandate_type=ledger_entry.entity_type.value,
            status=ledger_entry.status.value,
            created_at=ledger_entry.created_at.isoformat(),
            created_by_agent=ledger_entry.created_by_agent
        )

        # Store idempotency record if key provided
        if x_idempotency_key:
            idempotency_repo = IdempotencyRepository()
            await idempotency_repo.store_idempotency_record(
                idempotency_key=x_idempotency_key,
                agent_id=agent.agent_id,
                request_method="POST",
                request_path="/api/v1/mandates",
                request_body=request_body.model_dump(),
                response_status=201,
                response_body=result.model_dump()
            )

        # Add rate limit headers
        if hasattr(request.state, 'rate_limit_remaining'):
            response.headers["X-RateLimit-Limit"] = str(request.state.rate_limit_limit)
            response.headers["X-RateLimit-Remaining"] = str(request.state.rate_limit_remaining)

        return result

    except InvalidMandateDataError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid mandate data: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create mandate: {str(e)}"
        )


# REMOVED: PUT /{entity_id} endpoint
# The ledger is immutable - use POST /mandates with initial_signatures for all mandate creation
# Pre-signed mandates eliminate the need for separate "update" operations

# REMOVED: POST /{entity_id}/sign endpoint
# Use pre-signed mandate creation instead (POST /mandates with initial_signatures)


@router.get(
    "/{entity_id}",
    response_model=list[MandateLedgerEntry],
    responses={
        200: {"description": "Mandate versions retrieved"},
        401: {"model": ErrorResponse, "description": "Authentication required"},
        404: {"model": ErrorResponse, "description": "Mandate not found"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"}
    },
    summary="Get mandate by ID",
    description="Returns all versions of a mandate (latest first). Use [0] for current state."
)
async def get_mandate(
    entity_id: str,
    request: Request = None,
    response: Response = None,
    agent: AuthenticatedAgent = Depends(get_authenticated_agent),
    _rate_limit: None = Depends(check_rate_limit),
    limit: Optional[int] = None,
    offset: Optional[int] = None
):
    """
    Get all versions of a mandate.

    - Returns all versions from immutable ledger (latest first)
    - Supports pagination with limit/offset
    - Latest version is always at index [0]
    """
    mandate_service = MandateService()

    try:
        history = await mandate_service.get_mandate_history(
            entity_id=entity_id,
            limit=limit,
            offset=offset
        )

        # Add rate limit headers
        if hasattr(request.state, 'rate_limit_remaining'):
            response.headers["X-RateLimit-Limit"] = str(request.state.rate_limit_limit)
            response.headers["X-RateLimit-Remaining"] = str(request.state.rate_limit_remaining)

        return history

    except MandateNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mandate not found: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get mandate history: {str(e)}"
        )


# REMOVED: POST /search endpoint
# Use GET /transaction/{transaction_id} instead to get all mandates for a payment flow


@router.get(
    "/transaction/{transaction_id}",
    response_model=list[MandateLedgerEntry],
    responses={
        200: {"description": "Mandates for transaction retrieved"},
        401: {"model": ErrorResponse, "description": "Authentication required"},
        404: {"model": ErrorResponse, "description": "Transaction not found"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"}
    },
    summary="Get mandates by transaction ID",
    description="Returns all mandates (Intent, Cart, Payment) for a transaction in chronological order"
)
async def get_mandates_by_transaction(
    transaction_id: str,
    request: Request = None,
    response: Response = None,
    agent: AuthenticatedAgent = Depends(get_authenticated_agent),
    _rate_limit: None = Depends(check_rate_limit)
):
    """
    Get all mandates for a transaction.

    - Returns all mandates (Intent, Cart, Payment) in chronological order
    - Each mandate is the latest version
    - Useful for viewing the complete payment flow
    """
    mandate_service = MandateService()

    try:
        mandates = await mandate_service.get_mandates_by_transaction(transaction_id)

        # Add rate limit headers
        if hasattr(request.state, 'rate_limit_remaining'):
            response.headers["X-RateLimit-Limit"] = str(request.state.rate_limit_limit)
            response.headers["X-RateLimit-Remaining"] = str(request.state.rate_limit_remaining)

        return mandates

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get mandates for transaction: {str(e)}"
        )


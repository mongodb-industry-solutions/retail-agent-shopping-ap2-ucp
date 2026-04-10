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
Payment API Endpoints

Provides access to payment records:
- GET endpoints for querying
- POST endpoint for manual creation (until Change Streams enabled)

Payment records are designed to be auto-created by Change Streams when PaymentMandates are signed.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body, status
from typing import Optional

from src.api.dependencies import get_authenticated_agent
from src.models.auth import AuthenticatedAgent
from src.models.payment import PaymentResponse, PaymentListResponse, CreatePaymentRequest
from src.services.payment_service import PaymentService

router = APIRouter(prefix="/api/v1/payments", tags=["payments"])


@router.post("", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(
    request_body: CreatePaymentRequest = Body(...),
    agent: AuthenticatedAgent = Depends(get_authenticated_agent)
):
    """
    Manually create a payment record.

    **Temporary endpoint** - In production, payment records should be auto-created
    by Change Streams when PaymentMandates are signed.

    This endpoint:
    1. Validates all 3 mandates exist (Intent, Cart, Payment)
    2. Extracts signatures from mandates
    3. Creates ultra-lean payment record (IDs + signatures + timestamps only)
    4. Logs creation in audit trail

    Required fields:
    - transaction_id: Transaction/session ID
    - intent_mandate_id, cart_mandate_id, payment_mandate_id: Mandate entity IDs
    - amount, currency: Payment amount details
    - status: Payment status (SUCCESS, FAILED, PENDING)
    - merchant_agent, payment_processor_agent: Agent IDs
    """
    service = PaymentService()

    try:
        payment_record = await service.create_payment_record(
            transaction_id=request_body.transaction_id,
            intent_mandate_id=request_body.intent_mandate_id,
            cart_mandate_id=request_body.cart_mandate_id,
            payment_mandate_id=request_body.payment_mandate_id,
            amount=request_body.amount,
            currency=request_body.currency,
            status=request_body.status,
            merchant_agent=request_body.merchant_agent,
            payment_processor_agent=request_body.payment_processor_agent,
            payment_method_type=request_body.payment_method_type,
            metadata=request_body.metadata,
            user_id=request_body.user_id,
            session_id=request_body.session_id
        )

        return PaymentResponse(
            payment_id=payment_record.payment_id,
            transaction_id=payment_record.transaction_id,
            user_id=payment_record.user_id,
            session_id=payment_record.session_id,
            intent_mandate=payment_record.intent_mandate,
            cart_mandate=payment_record.cart_mandate,
            payment_mandate=payment_record.payment_mandate,
            amount=payment_record.amount,
            currency=payment_record.currency,
            status=payment_record.status,
            merchant_agent=payment_record.merchant_agent,
            payment_processor_agent=payment_record.payment_processor_agent,
            processed_at=payment_record.processed_at,
            payment_method_type=payment_record.payment_method_type,
            error_message=payment_record.error_message,
            metadata=payment_record.metadata
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create payment: {str(e)}"
        )


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: str,
    agent: AuthenticatedAgent = Depends(get_authenticated_agent)
):
    """
    Get payment by payment_id.

    Returns ultra-lean payment record with mandate references.
    To get full mandate details, use:
    - GET /api/v1/mandates/{intent_mandate.mandate_id}
    - GET /api/v1/mandates/{cart_mandate.mandate_id}
    - GET /api/v1/mandates/{payment_mandate.mandate_id}
    """
    service = PaymentService()
    payment = await service.payment_repo.get_by_payment_id(payment_id)

    if not payment:
        raise HTTPException(status_code=404, detail=f"Payment {payment_id} not found")

    return PaymentResponse(
        payment_id=payment.payment_id,
        transaction_id=payment.transaction_id,
        user_id=payment.user_id,
        session_id=payment.session_id,
        intent_mandate=payment.intent_mandate,
        cart_mandate=payment.cart_mandate,
        payment_mandate=payment.payment_mandate,
        amount=payment.amount,
        currency=payment.currency,
        status=payment.status,
        merchant_agent=payment.merchant_agent,
        payment_processor_agent=payment.payment_processor_agent,
        processed_at=payment.processed_at,
        payment_method_type=payment.payment_method_type,
        error_message=payment.error_message,
        metadata=payment.metadata
    )


@router.get("/session/{transaction_id}", response_model=PaymentListResponse)
async def get_payments_by_session(
    transaction_id: str,
    agent: AuthenticatedAgent = Depends(get_authenticated_agent)
):
    """
    Get all payments for a transaction/session.

    Useful when a user retries payment - shows all payment attempts.
    """
    service = PaymentService()
    payments = await service.payment_repo.get_by_transaction_id(transaction_id)

    payment_responses = [
        PaymentResponse(
            payment_id=p.payment_id,
            transaction_id=p.transaction_id,
            user_id=p.user_id,
            session_id=p.session_id,
            intent_mandate=p.intent_mandate,
            cart_mandate=p.cart_mandate,
            payment_mandate=p.payment_mandate,
            amount=p.amount,
            currency=p.currency,
            status=p.status,
            merchant_agent=p.merchant_agent,
            payment_processor_agent=p.payment_processor_agent,
            processed_at=p.processed_at,
            payment_method_type=p.payment_method_type,
            error_message=p.error_message,
            metadata=p.metadata
        )
        for p in payments
    ]

    return PaymentListResponse(
        payments=payment_responses,
        total_count=len(payment_responses)
    )


@router.get("", response_model=PaymentListResponse)
async def search_payments(
    status: Optional[str] = Query(None, description="Filter by payment status"),
    merchant_agent: Optional[str] = Query(None, description="Filter by merchant agent"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    session_id: Optional[str] = Query(None, description="Filter by session ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    agent: AuthenticatedAgent = Depends(get_authenticated_agent)
):
    """
    Search payments with filters.

    Supports filtering by status and merchant agent.
    """
    service = PaymentService()
    payments, total = await service.payment_repo.search_payments(
        status=status,
        merchant_agent=merchant_agent,
        user_id=user_id,
        session_id=session_id,
        skip=skip,
        limit=limit
    )

    payment_responses = [
        PaymentResponse(
            payment_id=p.payment_id,
            transaction_id=p.transaction_id,
            user_id=p.user_id,
            session_id=p.session_id,
            intent_mandate=p.intent_mandate,
            cart_mandate=p.cart_mandate,
            payment_mandate=p.payment_mandate,
            amount=p.amount,
            currency=p.currency,
            status=p.status,
            merchant_agent=p.merchant_agent,
            payment_processor_agent=p.payment_processor_agent,
            processed_at=p.processed_at,
            payment_method_type=p.payment_method_type,
            error_message=p.error_message,
            metadata=p.metadata
        )
        for p in payments
    ]

    return PaymentListResponse(
        payments=payment_responses,
        total_count=total
    )


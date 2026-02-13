# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is# distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
State machine for mandate lifecycle management.

Enforces valid status transitions for each mandate type.
"""

from typing import Optional
from src.models.enums import MandateType, MandateStatus
from src.core.errors import InvalidStateTransitionError


# Define valid state transitions for each mandate type
INTENT_MANDATE_TRANSITIONS = {
    MandateStatus.CREATED: [MandateStatus.SIGNED, MandateStatus.EXPIRED, MandateStatus.CANCELLED],
    MandateStatus.SIGNED: [MandateStatus.EXPIRED, MandateStatus.CANCELLED],
    MandateStatus.EXPIRED: [],  # Terminal state
    MandateStatus.CANCELLED: [],  # Terminal state
}

CART_MANDATE_TRANSITIONS = {
    MandateStatus.PROPOSED: [MandateStatus.UPDATED, MandateStatus.SIGNED, MandateStatus.EXPIRED, MandateStatus.CANCELLED],
    MandateStatus.UPDATED: [MandateStatus.SIGNED, MandateStatus.EXPIRED, MandateStatus.CANCELLED],
    MandateStatus.SIGNED: [MandateStatus.COMPLETED, MandateStatus.EXPIRED, MandateStatus.CANCELLED],
    MandateStatus.COMPLETED: [MandateStatus.REFUNDED],
    MandateStatus.REFUNDED: [],  # Terminal state
    MandateStatus.EXPIRED: [],  # Terminal state
    MandateStatus.CANCELLED: [],  # Terminal state
}

PAYMENT_MANDATE_TRANSITIONS = {
    MandateStatus.CREATED: [MandateStatus.SIGNED, MandateStatus.AUTHORIZED, MandateStatus.FAILED, MandateStatus.CANCELLED],
    MandateStatus.SIGNED: [MandateStatus.AUTHORIZED, MandateStatus.FAILED, MandateStatus.CANCELLED],
    MandateStatus.AUTHORIZED: [MandateStatus.CAPTURED, MandateStatus.FAILED, MandateStatus.CANCELLED],
    MandateStatus.CAPTURED: [MandateStatus.SETTLED, MandateStatus.REFUNDED, MandateStatus.FAILED],
    MandateStatus.SETTLED: [MandateStatus.REFUNDED],
    MandateStatus.REFUNDED: [],  # Terminal state
    MandateStatus.FAILED: [],  # Terminal state
    MandateStatus.CANCELLED: [],  # Terminal state
}

# Map mandate types to their transition rules
STATE_MACHINE = {
    MandateType.INTENT: INTENT_MANDATE_TRANSITIONS,
    MandateType.CART: CART_MANDATE_TRANSITIONS,
    MandateType.PAYMENT: PAYMENT_MANDATE_TRANSITIONS,
}


def is_valid_transition(
    mandate_type: MandateType,
    current_status: MandateStatus,
    new_status: MandateStatus
) -> bool:
    """
    Check if a status transition is valid for the given mandate type.

    Args:
        mandate_type: Type of mandate (INTENT, CART, PAYMENT)
        current_status: Current status
        new_status: Requested new status

    Returns:
        True if transition is valid, False otherwise

    Example:
        >>> is_valid_transition(
        ...     MandateType.CART,
        ...     MandateStatus.PROPOSED,
        ...     MandateStatus.SIGNED
        ... )
        True
        >>> is_valid_transition(
        ...     MandateType.CART,
        ...     MandateStatus.SIGNED,
        ...     MandateStatus.PROPOSED  # Can't go backwards
        ... )
        False
    """
    transitions = STATE_MACHINE.get(mandate_type, {})
    allowed_statuses = transitions.get(current_status, [])
    return new_status in allowed_statuses


def validate_transition(
    mandate_type: MandateType,
    current_status: MandateStatus,
    new_status: MandateStatus,
    entity_id: Optional[str] = None
) -> None:
    """
    Validate a status transition, raising an error if invalid.

    Args:
        mandate_type: Type of mandate
        current_status: Current status
        new_status: Requested new status
        entity_id: Optional entity ID for error context

    Raises:
        InvalidStateTransitionError: If transition is not allowed

    Example:
        >>> validate_transition(
        ...     MandateType.CART,
        ...     MandateStatus.EXPIRED,
        ...     MandateStatus.SIGNED,
        ...     "cart_123"
        ... )
        Traceback (most recent call last):
        InvalidStateTransitionError: Invalid state transition for cart_123: expired → signed
    """
    if not is_valid_transition(mandate_type, current_status, new_status):
        allowed = get_allowed_transitions(mandate_type, current_status)
        raise InvalidStateTransitionError(
            entity_id=entity_id or "unknown",
            current_status=current_status.value,
            requested_status=new_status.value,
            details={
                "mandate_type": mandate_type.value,
                "allowed_transitions": [s.value for s in allowed]
            }
        )


def get_allowed_transitions(
    mandate_type: MandateType,
    current_status: MandateStatus
) -> list[MandateStatus]:
    """
    Get list of allowed status transitions from the current status.

    Args:
        mandate_type: Type of mandate
        current_status: Current status

    Returns:
        List of allowed status values

    Example:
        >>> get_allowed_transitions(MandateType.CART, MandateStatus.PROPOSED)
        [<MandateStatus.UPDATED>, <MandateStatus.SIGNED>, ...]
    """
    transitions = STATE_MACHINE.get(mandate_type, {})
    return transitions.get(current_status, [])


def is_terminal_status(
    mandate_type: MandateType,
    status: MandateStatus
) -> bool:
    """
    Check if a status is terminal (no further transitions possible).

    Args:
        mandate_type: Type of mandate
        status: Status to check

    Returns:
        True if status is terminal, False otherwise

    Example:
        >>> is_terminal_status(MandateType.CART, MandateStatus.COMPLETED)
        False  # Can still be refunded
        >>> is_terminal_status(MandateType.CART, MandateStatus.EXPIRED)
        True  # No further transitions
    """
    transitions = STATE_MACHINE.get(mandate_type, {})
    allowed = transitions.get(status, [])
    return len(allowed) == 0


def get_initial_status(mandate_type: MandateType) -> MandateStatus:
    """
    Get the initial status for a new mandate of the given type.

    Args:
        mandate_type: Type of mandate

    Returns:
        Initial status for this mandate type

    Example:
        >>> get_initial_status(MandateType.INTENT)
        <MandateStatus.CREATED>
        >>> get_initial_status(MandateType.CART)
        <MandateStatus.PROPOSED>
        >>> get_initial_status(MandateType.PAYMENT)
        <MandateStatus.CREATED>
    """
    if mandate_type == MandateType.INTENT:
        return MandateStatus.CREATED
    elif mandate_type == MandateType.CART:
        return MandateStatus.PROPOSED
    elif mandate_type == MandateType.PAYMENT:
        return MandateStatus.CREATED
    else:
        raise ValueError(f"Unknown mandate type: {mandate_type}")


def can_sign(mandate_type: MandateType, current_status: MandateStatus) -> bool:
    """
    Check if a mandate can be signed in its current status.

    Args:
        mandate_type: Type of mandate
        current_status: Current status

    Returns:
        True if signing is allowed, False otherwise

    Example:
        >>> can_sign(MandateType.INTENT, MandateStatus.CREATED)
        True
        >>> can_sign(MandateType.INTENT, MandateStatus.SIGNED)
        False  # Already signed
    """
    return is_valid_transition(mandate_type, current_status, MandateStatus.SIGNED)


def can_cancel(mandate_type: MandateType, current_status: MandateStatus) -> bool:
    """
    Check if a mandate can be cancelled in its current status.

    Args:
        mandate_type: Type of mandate
        current_status: Current status

    Returns:
        True if cancellation is allowed, False otherwise

    Example:
        >>> can_cancel(MandateType.CART, MandateStatus.PROPOSED)
        True
        >>> can_cancel(MandateType.CART, MandateStatus.COMPLETED)
        False  # Can't cancel completed transactions
    """
    return is_valid_transition(mandate_type, current_status, MandateStatus.CANCELLED)


def get_lifecycle_stage(mandate_type: MandateType, status: MandateStatus) -> str:
    """
    Get the lifecycle stage for a given status.

    Returns a human-readable stage: 'draft', 'active', 'completed', or 'terminated'.

    Args:
        mandate_type: Type of mandate
        status: Current status

    Returns:
        Lifecycle stage name

    Example:
        >>> get_lifecycle_stage(MandateType.CART, MandateStatus.PROPOSED)
        'draft'
        >>> get_lifecycle_stage(MandateType.CART, MandateStatus.SIGNED)
        'active'
        >>> get_lifecycle_stage(MandateType.CART, MandateStatus.COMPLETED)
        'completed'
    """
    draft_statuses = [MandateStatus.CREATED, MandateStatus.PROPOSED, MandateStatus.UPDATED]
    active_statuses = [MandateStatus.SIGNED, MandateStatus.AUTHORIZED, MandateStatus.CAPTURED]
    completed_statuses = [MandateStatus.COMPLETED, MandateStatus.SETTLED, MandateStatus.REFUNDED]
    terminated_statuses = [MandateStatus.EXPIRED, MandateStatus.CANCELLED, MandateStatus.FAILED]

    if status in draft_statuses:
        return "draft"
    elif status in active_statuses:
        return "active"
    elif status in completed_statuses:
        return "completed"
    elif status in terminated_statuses:
        return "terminated"
    else:
        return "unknown"




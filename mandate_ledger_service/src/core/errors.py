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
Error hierarchy for the Mandate Ledger Service.

All custom exceptions inherit from MandateLedgerError for consistent error handling.
"""

from typing import Optional, Any


class MandateLedgerError(Exception):
    """
    Base exception for all Mandate Ledger Service errors.

    All custom exceptions should inherit from this class.
    """

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[dict[str, Any]] = None
    ):
        """
        Initialize the error.

        Args:
            message: Human-readable error message
            error_code: Machine-readable error code (e.g., 'MANDATE_NOT_FOUND')
            details: Additional context about the error
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__.upper()
        self.details = details or {}


# ==================== Mandate Errors ====================

class MandateNotFoundError(MandateLedgerError):
    """Raised when a mandate cannot be found."""

    def __init__(self, entity_id: str, details: Optional[dict] = None):
        super().__init__(
            message=f"Mandate not found: {entity_id}",
            error_code="MANDATE_NOT_FOUND",
            details={"entity_id": entity_id, **(details or {})}
        )


class MandateVersionNotFoundError(MandateLedgerError):
    """Raised when a specific mandate version cannot be found."""

    def __init__(self, entity_id: str, version: int, details: Optional[dict] = None):
        super().__init__(
            message=f"Mandate version not found: {entity_id} v{version}",
            error_code="MANDATE_VERSION_NOT_FOUND",
            details={"entity_id": entity_id, "version": version, **(details or {})}
        )


class VersionConflictError(MandateLedgerError):
    """
    Raised when optimistic locking fails.

    This occurs when the expected version doesn't match the current version,
    indicating that another operation modified the mandate concurrently.
    """

    def __init__(
        self,
        entity_id: str,
        expected_version: int,
        current_version: int,
        details: Optional[dict] = None
    ):
        super().__init__(
            message=(
                f"Version conflict for {entity_id}: "
                f"expected v{expected_version}, current v{current_version}"
            ),
            error_code="VERSION_CONFLICT",
            details={
                "entity_id": entity_id,
                "expected_version": expected_version,
                "current_version": current_version,
                **(details or {})
            }
        )


class InvalidMandateDataError(MandateLedgerError):
    """Raised when mandate data fails validation."""

    def __init__(self, message: str, validation_errors: Optional[list] = None):
        super().__init__(
            message=f"Invalid mandate data: {message}",
            error_code="INVALID_MANDATE_DATA",
            details={"validation_errors": validation_errors or []}
        )


class MandateTypeMismatchError(MandateLedgerError):
    """Raised when mandate data type doesn't match entity_type."""

    def __init__(
        self,
        entity_id: str,
        expected_type: str,
        actual_type: str,
        details: Optional[dict] = None
    ):
        super().__init__(
            message=(
                f"Mandate type mismatch for {entity_id}: "
                f"expected {expected_type}, got {actual_type}"
            ),
            error_code="MANDATE_TYPE_MISMATCH",
            details={
                "entity_id": entity_id,
                "expected_type": expected_type,
                "actual_type": actual_type,
                **(details or {})
            }
        )


# ==================== Chain Integrity Errors ====================

class ChainIntegrityError(MandateLedgerError):
    """
    Raised when the version chain integrity is violated.

    This indicates potential data corruption or tampering.
    """

    def __init__(self, entity_id: str, version: int, reason: str):
        super().__init__(
            message=f"Chain integrity error for {entity_id} v{version}: {reason}",
            error_code="CHAIN_INTEGRITY_ERROR",
            details={"entity_id": entity_id, "version": version, "reason": reason}
        )


class InvalidParentHashError(ChainIntegrityError):
    """Raised when parent version hash doesn't match."""

    def __init__(
        self,
        entity_id: str,
        version: int,
        expected_hash: str,
        actual_hash: str
    ):
        super().__init__(
            entity_id=entity_id,
            version=version,
            reason=(
                f"Parent hash mismatch: expected {expected_hash[:8]}..., "
                f"got {actual_hash[:8]}..."
            )
        )
        self.details.update({
            "expected_hash": expected_hash,
            "actual_hash": actual_hash
        })


# ==================== State Machine Errors ====================

class InvalidStateTransitionError(MandateLedgerError):
    """Raised when an invalid state transition is attempted."""

    def __init__(
        self,
        entity_id: str,
        current_status: str,
        requested_status: str,
        details: Optional[dict] = None
    ):
        super().__init__(
            message=(
                f"Invalid state transition for {entity_id}: "
                f"{current_status} → {requested_status}"
            ),
            error_code="INVALID_STATE_TRANSITION",
            details={
                "entity_id": entity_id,
                "current_status": current_status,
                "requested_status": requested_status,
                **(details or {})
            }
        )


# ==================== Authentication Errors ====================

class AuthenticationError(MandateLedgerError):
    """Base class for authentication errors."""
    pass


class InvalidApiKeyError(AuthenticationError):
    """Raised when an API key is invalid or not found."""

    def __init__(self, key_prefix: Optional[str] = None):
        message = "Invalid API key"
        if key_prefix:
            message += f" (prefix: {key_prefix})"
        super().__init__(
            message=message,
            error_code="INVALID_API_KEY",
            details={"key_prefix": key_prefix} if key_prefix else {}
        )


class ApiKeyExpiredError(AuthenticationError):
    """Raised when an API key has expired."""

    def __init__(self, key_id: str, expired_at: str):
        super().__init__(
            message=f"API key expired: {key_id}",
            error_code="API_KEY_EXPIRED",
            details={"key_id": key_id, "expired_at": expired_at}
        )


class ApiKeyRevokedError(AuthenticationError):
    """Raised when an API key has been revoked."""

    def __init__(self, key_id: str, revoked_at: str):
        super().__init__(
            message=f"API key revoked: {key_id}",
            error_code="API_KEY_REVOKED",
            details={"key_id": key_id, "revoked_at": revoked_at}
        )


class InsufficientPermissionsError(AuthenticationError):
    """Raised when an agent lacks required permissions."""

    def __init__(self, agent_id: str, required_permission: str):
        super().__init__(
            message=f"Agent {agent_id} lacks permission: {required_permission}",
            error_code="INSUFFICIENT_PERMISSIONS",
            details={"agent_id": agent_id, "required_permission": required_permission}
        )


# ==================== Rate Limiting Errors ====================

class RateLimitExceededError(MandateLedgerError):
    """Raised when rate limit is exceeded."""

    def __init__(
        self,
        agent_id: str,
        limit: int,
        window_seconds: int,
        retry_after: int
    ):
        super().__init__(
            message=f"Rate limit exceeded for {agent_id}: {limit} req/{window_seconds}s",
            error_code="RATE_LIMIT_EXCEEDED",
            details={
                "agent_id": agent_id,
                "limit": limit,
                "window_seconds": window_seconds,
                "retry_after": retry_after
            }
        )


# ==================== Idempotency Errors ====================

class IdempotencyConflictError(MandateLedgerError):
    """
    Raised when an idempotency key is reused with different request data.

    This prevents replay attacks and ensures request consistency.
    """

    def __init__(self, idempotency_key: str, original_request_id: str):
        super().__init__(
            message=f"Idempotency key conflict: {idempotency_key}",
            error_code="IDEMPOTENCY_CONFLICT",
            details={
                "idempotency_key": idempotency_key,
                "original_request_id": original_request_id
            }
        )


# ==================== Database Errors ====================

class DatabaseError(MandateLedgerError):
    """Base class for database errors."""
    pass


class DatabaseConnectionError(DatabaseError):
    """Raised when database connection fails."""

    def __init__(self, reason: str):
        super().__init__(
            message=f"Database connection error: {reason}",
            error_code="DATABASE_CONNECTION_ERROR",
            details={"reason": reason}
        )


class DatabaseOperationError(DatabaseError):
    """Raised when a database operation fails."""

    def __init__(self, operation: str, reason: str):
        super().__init__(
            message=f"Database operation failed: {operation} - {reason}",
            error_code="DATABASE_OPERATION_ERROR",
            details={"operation": operation, "reason": reason}
        )


class TransactionError(DatabaseError):
    """Raised when a database transaction fails."""

    def __init__(self, reason: str, transaction_id: Optional[str] = None):
        super().__init__(
            message=f"Transaction failed: {reason}",
            error_code="TRANSACTION_ERROR",
            details={"reason": reason, "transaction_id": transaction_id}
        )


# ==================== Consistency Errors ====================

class ConsistencyError(MandateLedgerError):
    """Base class for data consistency errors."""
    pass


class MissingCurrentStateError(ConsistencyError):
    """Raised when current state record is missing for a ledger entry."""

    def __init__(self, entity_id: str):
        super().__init__(
            message=f"Missing current state for mandate: {entity_id}",
            error_code="MISSING_CURRENT_STATE",
            details={"entity_id": entity_id}
        )


class OrphanedCurrentStateError(ConsistencyError):
    """Raised when current state exists without ledger entries."""

    def __init__(self, entity_id: str):
        super().__init__(
            message=f"Orphaned current state (no ledger entries): {entity_id}",
            error_code="ORPHANED_CURRENT_STATE",
            details={"entity_id": entity_id}
        )


# ==================== Validation Errors ====================

class ValidationError(MandateLedgerError):
    """Base class for validation errors."""
    pass


class InvalidInputError(ValidationError):
    """Raised when input data is invalid."""

    def __init__(self, field: str, reason: str, value: Any = None):
        super().__init__(
            message=f"Invalid input for {field}: {reason}",
            error_code="INVALID_INPUT",
            details={"field": field, "reason": reason, "value": str(value)}
        )


class MissingRequiredFieldError(ValidationError):
    """Raised when a required field is missing."""

    def __init__(self, field: str, context: Optional[str] = None):
        message = f"Missing required field: {field}"
        if context:
            message += f" (context: {context})"
        super().__init__(
            message=message,
            error_code="MISSING_REQUIRED_FIELD",
            details={"field": field, "context": context}
        )





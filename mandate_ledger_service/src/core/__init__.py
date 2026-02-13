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
Core utilities for the Mandate Ledger Service.

Day 4 modules:
- errors: Error hierarchy for consistent error handling
- hashing: SHA-256 and bcrypt utilities for mandate and API key hashing
- state_machine: Mandate lifecycle state transition validation
- monitoring: Prometheus metrics for observability
"""

from src.core.errors import (
    MandateLedgerError,
    MandateNotFoundError,
    VersionConflictError,
    InvalidMandateDataError,
    ChainIntegrityError,
    InvalidStateTransitionError,
    AuthenticationError,
    InvalidApiKeyError,
    RateLimitExceededError,
    DatabaseError,
)

from src.core.hashing import (
    compute_sha256,
    compute_mandate_hash,
    hash_api_key,
    verify_api_key,
    verify_chain_integrity,
)

from src.core.state_machine import (
    is_valid_transition,
    validate_transition,
    get_allowed_transitions,
    is_terminal_status,
    get_initial_status,
    can_sign,
    can_cancel,
)

from src.core.monitoring import (
    track_request,
    track_mandate_operation,
    track_db_operation,
    track_auth_attempt,
    track_error,
)

__all__ = [
    # Errors
    "MandateLedgerError",
    "MandateNotFoundError",
    "VersionConflictError",
    "InvalidMandateDataError",
    "ChainIntegrityError",
    "InvalidStateTransitionError",
    "AuthenticationError",
    "InvalidApiKeyError",
    "RateLimitExceededError",
    "DatabaseError",
    # Hashing
    "compute_sha256",
    "compute_mandate_hash",
    "hash_api_key",
    "verify_api_key",
    "verify_chain_integrity",
    # State Machine
    "is_valid_transition",
    "validate_transition",
    "get_allowed_transitions",
    "is_terminal_status",
    "get_initial_status",
    "can_sign",
    "can_cancel",
    # Monitoring
    "track_request",
    "track_mandate_operation",
    "track_db_operation",
    "track_auth_attempt",
    "track_error",
]

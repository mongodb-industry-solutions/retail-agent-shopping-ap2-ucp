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
Enumerations for the Mandate Ledger Service.

All enums used across models, state machines, and business logic.
"""

from enum import Enum


class MandateType(str, Enum):
    """Types of mandates in the AP2 protocol."""

    INTENT = "IntentMandate"
    CART = "CartMandate"
    PAYMENT = "PaymentMandate"


class MandateStatus(str, Enum):
    """
    Lifecycle status of a mandate.

    State transitions (enforced by state machine):
    - IntentMandate: created -> signed -> expired/cancelled
    - CartMandate: proposed -> updated -> signed -> completed/expired/cancelled
    - PaymentMandate: created -> authorized -> captured -> settled/failed
    """

    # Common states
    CREATED = "created"
    PROPOSED = "proposed"
    UPDATED = "updated"
    SIGNED = "signed"
    COMPLETED = "completed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

    # Payment-specific states
    AUTHORIZED = "authorized"
    CAPTURED = "captured"
    SETTLED = "settled"
    FAILED = "failed"
    REFUNDED = "refunded"


class EventType(str, Enum):
    """Types of audit log events."""

    # Mandate lifecycle events
    MANDATE_CREATED = "mandate.created"
    MANDATE_UPDATED = "mandate.updated"
    MANDATE_SIGNED = "mandate.signed"
    MANDATE_COMPLETED = "mandate.completed"
    MANDATE_EXPIRED = "mandate.expired"
    MANDATE_CANCELLED = "mandate.cancelled"

    # Payment events
    PAYMENT_AUTHORIZED = "payment.authorized"
    PAYMENT_CAPTURED = "payment.captured"
    PAYMENT_SETTLED = "payment.settled"
    PAYMENT_FAILED = "payment.failed"
    PAYMENT_REFUNDED = "payment.refunded"

    # System events
    CONSISTENCY_CHECK_PASSED = "system.consistency_check_passed"
    CONSISTENCY_CHECK_FAILED = "system.consistency_check_failed"
    CONSISTENCY_REPAIRED = "system.consistency_repaired"

    # Auth events
    API_KEY_CREATED = "auth.api_key_created"
    API_KEY_REVOKED = "auth.api_key_revoked"
    UNAUTHORIZED_ACCESS = "auth.unauthorized_access"

    # Payment events
    PAYMENT_CREATED = "payment.created"


"""
Agent Type Naming Convention
=============================

Agent types are free-form strings with no predefined enum or whitelist.
This allows the service to work with any current or future agent types
without requiring code changes, config updates, or service restarts.

Naming Convention (recommended but not enforced):
- Use kebab-case: 'shopping-agent', 'logistics-agent'
- Be descriptive: 'fraud-detection-agent', 'refund-processor'
- Keep it concise: < 100 characters

Common Examples (not exhaustive):
- shopping-agent: Handles user shopping intent
- merchant-agent: Manages merchant cart and catalog
- payment-processor: Processes payments
- credentials-provider: Manages payment credentials
- logistics-agent: Handles shipping and fulfillment
- fraud-detection-agent: Monitors for fraudulent activity
- compliance-agent: Ensures regulatory compliance
- refund-processor: Handles refunds and returns
- user: User-initiated actions
- system: Automated system actions
- admin: Administrative actions

Custom agent types are fully supported with no registration required.
"""


class ConsistencyIssueType(str, Enum):
    """Types of data consistency issues that can be detected."""

    MISSING_LEDGER_ENTRY = "missing_ledger_entry"
    VERSION_MISMATCH = "version_mismatch"
    BROKEN_VERSION_CHAIN = "broken_version_chain"
    HASH_MISMATCH = "hash_mismatch"
    INVALID_HASH = "invalid_hash"
    MISSING_AUDIT_LOG = "missing_audit_log"


class ApiKeyStatus(str, Enum):
    """Status of an API key."""

    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"


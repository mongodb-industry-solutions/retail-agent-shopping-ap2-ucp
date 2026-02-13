"""
MongoDB collection references.

Provides type-safe accessors for all 6 collections in the mandate ledger.
"""

from motor.motor_asyncio import AsyncIOMotorCollection
from src.db.mongodb import get_database


# Collection names (constants for consistency)
MANDATE_LEDGER = "mandate_ledger"
API_KEYS = "api_keys"
AUDIT_LOG = "audit_log"
IDEMPOTENCY_RECORDS = "idempotency_records"
CONSISTENCY_CHECKS = "consistency_checks"
RATE_LIMITS = "rate_limits"


def get_mandate_ledger_collection() -> AsyncIOMotorCollection:
    """
    Get the mandate_ledger collection.

    Stores immutable version history of all mandates.
    Each document is a version of a mandate (IntentMandate, CartMandate, PaymentMandate).

    Key fields:
    - entity_id: Stable ID across versions
    - version: Incremental version number
    - parent_version_id: Link to previous version
    - mandate_data: The actual mandate (strict validated)

    Returns:
        AsyncIOMotorCollection: mandate_ledger collection
    """
    return get_database()[MANDATE_LEDGER]


def get_api_keys_collection() -> AsyncIOMotorCollection:
    """
    Get the api_keys collection.

    Stores API keys for agent authentication.
    Keys are hashed with bcrypt before storage.

    Key fields:
    - key_hash: Bcrypt hash of the API key (indexed)
    - agent_id: Agent identifier
    - scopes: List of permissions
    - is_active: Whether key is still valid

    Returns:
        AsyncIOMotorCollection: api_keys collection
    """
    return get_database()[API_KEYS]


def get_audit_log_collection() -> AsyncIOMotorCollection:
    """
    Get the audit_log collection.

    Stores all API operations for compliance and debugging.
    Has TTL index for automatic deletion after 90 days.

    Key fields:
    - event_type: Type of event (mandate.created, etc.)
    - entity_id: Related mandate ID
    - actor_agent_id: Who performed the action
    - event_timestamp: When it happened (indexed with TTL)
    - expires_at: When to auto-delete (TTL)

    Returns:
        AsyncIOMotorCollection: audit_log collection
    """
    return get_database()[AUDIT_LOG]


def get_idempotency_records_collection() -> AsyncIOMotorCollection:
    """
    Get the idempotency_records collection.

    Stores idempotency keys to prevent duplicate operations.
    Has TTL index for automatic deletion after 24 hours.

    Key fields:
    - idempotency_key: Unique key from client (indexed)
    - agent_id: Agent that made the request
    - ledger_entry_id: Created mandate reference
    - expires_at: When to auto-delete (TTL)

    Returns:
        AsyncIOMotorCollection: idempotency_records collection
    """
    return get_database()[IDEMPOTENCY_RECORDS]


def get_consistency_checks_collection() -> AsyncIOMotorCollection:
    """
    Get the consistency_checks collection.

    Stores detected inconsistencies in the ledger.
    Used for monitoring and auto-repair.

    Key fields:
    - entity_id: Mandate with inconsistency
    - issue_type: Type of inconsistency
    - resolved_at: When it was fixed (null if unresolved)
    - auto_fixable: Whether it can be auto-repaired

    Returns:
        AsyncIOMotorCollection: consistency_checks collection
    """
    return get_database()[CONSISTENCY_CHECKS]


def get_rate_limits_collection() -> AsyncIOMotorCollection:
    """
    Get the rate_limits collection.

    Stores rate limiting state per agent.
    Uses sliding window algorithm.

    Key fields:
    - agent_id: Agent identifier
    - window_start: Start of current time window
    - request_count: Number of requests in window
    - limit: Maximum allowed requests

    Returns:
        AsyncIOMotorCollection: rate_limits collection
    """
    return get_database()[RATE_LIMITS]


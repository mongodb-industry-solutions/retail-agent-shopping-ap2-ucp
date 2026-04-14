"""
MongoDB index creation.

Defines and creates all indexes for the 6 collections.
This module is called at application startup to ensure indexes exist.

Total: 15 indexes across 6 collections
"""

import logging
from pymongo import ASCENDING, DESCENDING, IndexModel
from src.db import collections

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
# INDEX DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════════

# Collection 1: mandate_ledger (3 indexes)
MANDATE_LEDGER_INDEXES = [
    IndexModel(
        [("entity_id", ASCENDING), ("version", DESCENDING)],
        name="entity_versions_idx",
        background=True
    ),
    IndexModel(
        [("transaction_id", ASCENDING)],
        name="transaction_idx",
        background=True
    ),
    IndexModel(
        [("entity_id", ASCENDING), ("entity_type", ASCENDING), ("created_at", DESCENDING)],
        name="entity_type_time_idx",
        background=True
    ),
    IndexModel(
        [("user_id", ASCENDING), ("session_id", ASCENDING)],
        name="user_session_idx",
        background=True
    ),
]

# Collection 2: api_keys (2 indexes)
API_KEYS_INDEXES = [
    IndexModel(
        [("key_hash", ASCENDING)],
        name="key_hash_unique_idx",
        unique=True,
        background=True
    ),
    IndexModel(
        [("agent_id", ASCENDING), ("is_active", ASCENDING)],
        name="agent_active_idx",
        background=True
    ),
]

# Collection 3: idempotency_records (2 indexes)
IDEMPOTENCY_RECORDS_INDEXES = [
    IndexModel(
        [("idempotency_key", ASCENDING), ("agent_id", ASCENDING)],
        name="idempotency_unique_idx",
        unique=True,
        background=True
    ),
    IndexModel(
        [("expires_at", ASCENDING)],
        name="ttl_idx",
        expireAfterSeconds=0,  # TTL: auto-delete when expires_at is reached
        background=True
    ),
]

# Collection 4: audit_log (4 indexes)
AUDIT_LOG_INDEXES = [
    IndexModel(
        [("event_timestamp", DESCENDING)],
        name="timestamp_idx",
        background=True
    ),
    IndexModel(
        [("entity_id", ASCENDING), ("event_timestamp", DESCENDING)],
        name="entity_timeline_idx",
        background=True
    ),
    IndexModel(
        [("actor_agent_id", ASCENDING), ("success", ASCENDING)],
        name="agent_success_idx",
        background=True
    ),
    IndexModel(
        [("expires_at", ASCENDING)],
        name="ttl_idx",
        expireAfterSeconds=0,  # TTL: auto-delete when expires_at is reached
        background=True
    ),
]

# Collection 5: consistency_checks (2 indexes)
CONSISTENCY_CHECKS_INDEXES = [
    IndexModel(
        [("resolved_at", ASCENDING)],
        name="resolved_idx",
        background=True
    ),
    IndexModel(
        [("entity_id", ASCENDING)],
        name="entity_idx",
        background=True
    ),
]

# Collection 6: rate_limits (1 index)
RATE_LIMITS_INDEXES = [
    IndexModel(
        [("agent_id", ASCENDING), ("window_start", DESCENDING)],
        name="agent_window_unique_idx",
        unique=True,
        background=True
    ),
]


# ═══════════════════════════════════════════════════════════════════════════
# INDEX CREATION
# ═══════════════════════════════════════════════════════════════════════════

async def create_all_indexes() -> None:
    """
    Create all indexes for all collections.

    This is called at application startup.
    Index creation is idempotent - if an index already exists, it's not recreated.

    Creates:
    - 4 indexes on mandate_ledger
    - 2 indexes on api_keys
    - 2 indexes on idempotency_records
    - 4 indexes on audit_log (including TTL)
    - 2 indexes on consistency_checks
    - 1 index on rate_limits

    Total: 15 indexes
    """
    logger.info("Creating MongoDB indexes...")

    try:
        # 1. mandate_ledger (3 indexes)
        logger.info("  Creating indexes for mandate_ledger...")
        mandate_ledger = collections.get_mandate_ledger_collection()
        result = await mandate_ledger.create_indexes(MANDATE_LEDGER_INDEXES)
        logger.info(f"    Created {len(result)} indexes: {result}")

        # 2. api_keys (2 indexes)
        logger.info("  Creating indexes for api_keys...")
        api_keys = collections.get_api_keys_collection()
        result = await api_keys.create_indexes(API_KEYS_INDEXES)
        logger.info(f"    Created {len(result)} indexes: {result}")

        # 3. idempotency_records (2 indexes, including TTL)
        logger.info("  Creating indexes for idempotency_records (with TTL)...")
        idempotency = collections.get_idempotency_records_collection()
        result = await idempotency.create_indexes(IDEMPOTENCY_RECORDS_INDEXES)
        logger.info(f"    Created {len(result)} indexes: {result}")

        # 4. audit_log (4 indexes, including TTL)
        logger.info("  Creating indexes for audit_log (with TTL)...")
        audit_log = collections.get_audit_log_collection()
        result = await audit_log.create_indexes(AUDIT_LOG_INDEXES)
        logger.info(f"    Created {len(result)} indexes: {result}")

        # 5. consistency_checks (2 indexes)
        logger.info("  Creating indexes for consistency_checks...")
        consistency = collections.get_consistency_checks_collection()
        result = await consistency.create_indexes(CONSISTENCY_CHECKS_INDEXES)
        logger.info(f"    Created {len(result)} indexes: {result}")

        # 6. rate_limits (1 index)
        logger.info("  Creating indexes for rate_limits...")
        rate_limits = collections.get_rate_limits_collection()
        result = await rate_limits.create_indexes(RATE_LIMITS_INDEXES)
        logger.info(f"    Created {len(result)} indexes: {result}")

        logger.info("All 15 indexes created successfully!")

    except Exception as e:
        logger.error(f"Error creating indexes: {e}")
        raise


async def list_all_indexes() -> dict[str, list[str]]:
    """
    List all indexes for all collections.

    Useful for debugging and verification.

    Returns:
        dict: Collection name → list of index names
    """
    collections_map = {
        "mandate_ledger": collections.get_mandate_ledger_collection(),
        "api_keys": collections.get_api_keys_collection(),
        "idempotency_records": collections.get_idempotency_records_collection(),
        "audit_log": collections.get_audit_log_collection(),
        "consistency_checks": collections.get_consistency_checks_collection(),
        "rate_limits": collections.get_rate_limits_collection(),
    }

    result = {}
    for name, collection in collections_map.items():
        indexes = await collection.index_information()
        result[name] = list(indexes.keys())

    return result


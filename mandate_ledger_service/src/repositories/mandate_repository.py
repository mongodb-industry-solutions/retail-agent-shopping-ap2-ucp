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
Mandate repository for ledger and current state operations.

Handles all database operations for mandate management.
"""

from typing import Optional
from datetime import datetime, timezone

from src.repositories.base_repository import BaseRepository
from src.db.mongodb import MongoDB
from src.models.mandate import MandateLedgerEntry, MandateCurrentState
from src.models.enums import MandateType, MandateStatus
from src.core.errors import (
    MandateNotFoundError,
    MandateVersionNotFoundError,
    VersionConflictError
)
from src.core.hashing import compute_mandate_hash


class MandateRepository:
    """
    Repository for mandate ledger and current state operations.

    Provides methods for:
    - Creating mandates
    - Updating mandates (with optimistic locking)
    - Querying ledger history
    - Managing current state
    """

    def __init__(self):
        """Initialize the mandate repository."""
        self.ledger_repo = BaseRepository(MongoDB.mandate_ledger)
        # NOTE: current_state_repo removed - current state queried from ledger

    # ==================== Ledger Operations ====================

    async def create_ledger_entry(
        self,
        entity_id: str,
        entity_type: MandateType,
        mandate_data: dict,
        status: MandateStatus,
        created_by_agent: str,
        created_by_agent_type: str,
        transaction_id: str,
        metadata: Optional[dict] = None,
        signatures: Optional[list] = None
    ) -> MandateLedgerEntry:
        """
        Create the first version of a mandate in the ledger.

        Args:
            entity_id: Unique mandate identifier
            entity_type: Type of mandate (INTENT, CART, PAYMENT)
            mandate_data: The AP2 mandate data
            status: Initial status
            created_by_agent: Agent that created the mandate
            created_by_agent_type: Type of agent (e.g., 'shopping-agent')
            transaction_id: Transaction identifier
            metadata: Optional metadata
            signatures: Optional list of signature dicts

        Returns:
            Created ledger entry
        """
        created_at = datetime.now(timezone.utc)

        entry_dict = {
            "entity_id": entity_id,
            "version": 1,
            "entity_type": entity_type.value,
            "mandate_data": mandate_data,
            "status": status.value,
            "created_at": created_at,
            "created_by_agent": created_by_agent,
            "created_by_agent_type": created_by_agent_type,
            "transaction_id": transaction_id,
            "parent_version": None,
            "parent_version_hash": None,
            "metadata": metadata or {},
            "signatures": signatures or []
        }

        # Compute hash for this entry (must serialize datetime for hashing)
        hashable_dict = {**entry_dict, "created_at": created_at.isoformat()}
        current_hash = compute_mandate_hash(hashable_dict)
        entry_dict["current_version_hash"] = current_hash

        # Insert into ledger
        await self.ledger_repo.insert_one(entry_dict)

        return MandateLedgerEntry(**entry_dict)

    async def append_ledger_entry(
        self,
        entity_id: str,
        mandate_data: dict,
        status: MandateStatus,
        created_by_agent: str,
        created_by_agent_type: str,
        transaction_id: str,
        parent_version: int,
        parent_version_hash: str,
        metadata: Optional[dict] = None,
        signatures: Optional[list] = None
    ) -> MandateLedgerEntry:
        """
        Append a new version to the mandate ledger.

        Args:
            entity_id: Mandate identifier
            mandate_data: Updated AP2 mandate data
            status: New status
            created_by_agent: Agent making the update
            created_by_agent_type: Type of agent (e.g., 'shopping-agent')
            transaction_id: Transaction identifier
            parent_version: Parent version number
            parent_version_hash: Hash of parent version (for chain integrity)
            metadata: Optional metadata
            signatures: Optional list of signature dicts

        Returns:
            New ledger entry
        """
        # Get latest version to determine next version number
        latest = await self.get_latest_ledger_entry(entity_id)
        if not latest:
            raise MandateNotFoundError(entity_id)

        next_version = latest.version + 1

        created_at = datetime.now(timezone.utc)

        entry_dict = {
            "entity_id": entity_id,
            "version": next_version,
            "entity_type": latest.entity_type.value,
            "mandate_data": mandate_data,
            "status": status.value,
            "created_at": created_at,
            "created_by_agent": created_by_agent,
            "created_by_agent_type": created_by_agent_type,
            "transaction_id": transaction_id,
            "parent_version": parent_version,
            "parent_version_hash": parent_version_hash,
            "metadata": metadata or {},
            "signatures": signatures or []
        }

        # Compute hash for this entry (must serialize datetime for hashing)
        hashable_dict = {**entry_dict, "created_at": created_at.isoformat()}
        current_hash = compute_mandate_hash(hashable_dict)
        entry_dict["current_version_hash"] = current_hash

        # Insert into ledger
        await self.ledger_repo.insert_one(entry_dict)

        return MandateLedgerEntry(**entry_dict)

    async def get_ledger_entry(
        self,
        entity_id: str,
        version: int
    ) -> Optional[MandateLedgerEntry]:
        """
        Get a specific version from the ledger.

        Args:
            entity_id: Mandate identifier
            version: Version number

        Returns:
            Ledger entry or None
        """
        doc = await self.ledger_repo.find_one({
            "entity_id": entity_id,
            "version": version
        })

        if doc:
            doc.pop("_id", None)
            return MandateLedgerEntry(**doc)
        return None

    async def get_latest_ledger_entry(
        self,
        entity_id: str
    ) -> Optional[MandateLedgerEntry]:
        """
        Get the latest version from the ledger.

        Args:
            entity_id: Mandate identifier

        Returns:
            Latest ledger entry or None
        """
        results = await self.ledger_repo.find_many(
            filter_dict={"entity_id": entity_id},
            sort=[("version", -1)],
            limit=1
        )

        if results:
            doc = results[0]
            doc.pop("_id", None)
            return MandateLedgerEntry(**doc)
        return None

    async def get_ledger_history(
        self,
        entity_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> list[MandateLedgerEntry]:
        """
        Get full version history for a mandate.

        Args:
            entity_id: Mandate identifier
            limit: Maximum number of entries
            offset: Number of entries to skip

        Returns:
            List of ledger entries (newest first)
        """
        docs = await self.ledger_repo.find_many(
            filter_dict={"entity_id": entity_id},
            sort=[("version", -1)],
            limit=limit,
            skip=offset
        )

        entries = []
        for doc in docs:
            doc.pop("_id", None)
            entries.append(MandateLedgerEntry(**doc))

        return entries

    async def count_ledger_versions(self, entity_id: str) -> int:
        """
        Count number of versions for a mandate.

        Args:
            entity_id: Mandate identifier

        Returns:
            Number of versions
        """
        return await self.ledger_repo.count_documents({
            "entity_id": entity_id
        })

    # ==================== Current State Operations ====================

    # NOTE: create_current_state() removed - no longer needed
    # NOTE: update_current_state() removed - no longer needed
    # Current state is now queried directly from the ledger (latest version)

    async def get_current_state(
        self,
        entity_id: str
    ) -> Optional[MandateCurrentState]:
        """
        Get current state for a mandate by querying the ledger.

        Returns the latest version (highest version number) from the ledger.
        No longer uses mandate_current_state collection.

        Args:
            entity_id: Mandate identifier

        Returns:
            Current state or None
        """
        # Query ledger for latest version (sort by version descending)
        # Use collection directly since BaseRepository doesn't support sort
        doc = await self.ledger_repo.collection.find_one(
            {"entity_id": entity_id},
            sort=[("version", -1)]  # Get highest version
        )

        if not doc:
            return None

        doc.pop("_id", None)

        # Convert to MandateCurrentState format
        return MandateCurrentState(
            entity_id=doc["entity_id"],
            entity_type=doc["entity_type"],
            current_version=doc["version"],
            version=doc["version"],
            status=doc["status"],
            mandate_data=doc["mandate_data"],
            transaction_id=doc["transaction_id"],
            created_at=doc["created_at"],
            created_by_agent=doc["created_by_agent"],
            updated_at=doc.get("created_at"),  # Use created_at of this version
            updated_by_agent=doc["created_by_agent"],
            current_version_hash=doc["current_version_hash"],
            signatures=doc.get("signatures", []),
            metadata=doc.get("metadata", {})
        )

    async def get_mandates_by_transaction(
        self,
        transaction_id: str
    ) -> list[MandateLedgerEntry]:
        """
        Get all mandates for a transaction.

        Returns the latest version of each mandate in chronological order.

        Args:
            transaction_id: Transaction identifier

        Returns:
            List of latest mandate versions for this transaction
        """
        # Aggregation pipeline to get latest version of each mandate for this transaction
        pipeline = [
            # Stage 1: Match transaction
            {"$match": {"transaction_id": transaction_id}},

            # Stage 2: Sort by version descending
            {"$sort": {"entity_id": 1, "version": -1}},

            # Stage 3: Group by entity_id to get latest version
            {
                "$group": {
                    "_id": "$entity_id",
                    "latest": {"$first": "$$ROOT"}
                }
            },

            # Stage 4: Replace root with latest document
            {"$replaceRoot": {"newRoot": "$latest"}},

            # Stage 5: Sort by created_at (chronological order)
            {"$sort": {"created_at": 1}}
        ]

        # Execute aggregation
        docs = await self.ledger_repo.aggregate(pipeline)

        mandates = []
        for doc in docs:
            doc.pop("_id", None)
            mandates.append(MandateLedgerEntry(**doc))

        return mandates

    async def cancel_mandate(
        self,
        entity_id: str,
        cancelled_by_agent: str,
        transaction_id: str,
        reason: Optional[str] = None
    ) -> MandateLedgerEntry:
        """
        Cancel a mandate by creating a new version with CANCELLED status.

        This is the proper way to "remove" a mandate - by appending
        a cancellation event to the immutable ledger. The mandate is
        not deleted; instead, a new version is created with CANCELLED status.

        Args:
            entity_id: Mandate identifier
            cancelled_by_agent: Agent cancelling the mandate
            transaction_id: Transaction identifier
            reason: Optional reason for cancellation

        Returns:
            New ledger entry with CANCELLED status

        Raises:
            MandateNotFoundError: If mandate doesn't exist
            InvalidStateTransitionError: If cancellation is not allowed
        """
        from src.core.state_machine import can_cancel, validate_transition

        # Get current state
        current = await self.get_current_state(entity_id)
        if not current:
            raise MandateNotFoundError(entity_id)

        # Validate cancellation is allowed
        validate_transition(
            mandate_type=MandateType(current.entity_type),
            current_status=MandateStatus(current.status),
            new_status=MandateStatus.CANCELLED,
            entity_id=entity_id
        )

        # Create new version with CANCELLED status
        metadata = {}
        if reason:
            metadata["cancellation_reason"] = reason

        new_entry = await self.append_ledger_entry(
            entity_id=entity_id,
            mandate_data=current.mandate_data,  # Keep same data
            status=MandateStatus.CANCELLED,
            created_by_agent=cancelled_by_agent,
            transaction_id=transaction_id,
            parent_version=current.current_version,
            parent_version_hash=current.current_version_hash,
            metadata=metadata
        )

        # NOTE: No longer updating current_state - it's queried from ledger

        return new_entry


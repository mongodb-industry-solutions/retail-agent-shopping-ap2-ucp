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
Audit repository for audit log operations.

Handles all database operations for audit logging.
"""

from typing import Optional
from datetime import datetime, timezone
from uuid import uuid4

from src.repositories.base_repository import BaseRepository
from src.db.mongodb import MongoDB
from src.models.audit import AuditLogEntry
from src.models.enums import EventType


class AuditRepository:
    """
    Repository for audit log operations.

    Provides methods for:
    - Creating audit log entries
    - Querying audit logs
    - Searching by entity, agent, or event type
    """

    def __init__(self):
        """Initialize the audit repository."""
        self.repo = BaseRepository(MongoDB.audit_logs)

    def _normalize_audit_doc(self, doc: dict) -> dict:
        """
        Normalize audit log document to match AuditLogEntry model.

        Handles migration from old format (action/changes as top-level fields)
        to new format (action/changes inside details dict).
        """
        doc.pop("_id", None)

        # If old format with action/changes as top-level fields, move to details
        if "action" in doc or "changes" in doc:
            if "details" not in doc:
                doc["details"] = {}
            if "action" in doc:
                doc["details"]["action"] = doc.pop("action")
            if "changes" in doc:
                doc["details"]["changes"] = doc.pop("changes")

        # Ensure required fields have defaults
        if "details" not in doc:
            doc["details"] = {}
        if "metadata" not in doc:
            doc["metadata"] = {}
        if "success" not in doc:
            doc["success"] = True

        return doc

    async def create_audit_log(
        self,
        event_type: EventType,
        entity_id: str,
        entity_type: str,
        entity_version: Optional[int],
        actor_id: str,
        actor_type: str,
        action: str,
        changes: Optional[dict] = None,
        metadata: Optional[dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        transaction_id: Optional[str] = None
    ) -> AuditLogEntry:
        """
        Create a new audit log entry.

        Args:
            event_type: Type of event
            entity_id: ID of affected entity
            entity_type: Type of entity
            entity_version: Version of entity (if applicable)
            actor_id: ID of actor performing action
            actor_type: Type of actor (agent type)
            action: Description of action
            changes: Changes made (before/after)
            metadata: Additional context
            ip_address: IP address of request
            user_agent: User agent string
            transaction_id: Related transaction ID

        Returns:
            Created audit log entry
        """
        # Build details dict from action and changes
        details = {}
        if action:
            details["action"] = action
        if changes:
            details["changes"] = changes

        log_dict = {
            "event_id": f"evt_{uuid4()}",
            "event_type": event_type.value,
            "entity_id": entity_id,
            "entity_type": entity_type,
            "entity_version": entity_version,
            "actor_id": actor_id,
            "actor_type": actor_type,
            "details": details,
            "metadata": metadata or {},
            "timestamp": datetime.now(timezone.utc),
            "ip_address": ip_address,
            "user_agent": user_agent,
            "transaction_id": transaction_id,
            "success": True  # Default to True, caller can override
        }

        await self.repo.insert_one(log_dict)

        return AuditLogEntry(**log_dict)

    async def get_logs_by_entity(
        self,
        entity_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> tuple[list[AuditLogEntry], int]:
        """
        Get all audit logs for a specific entity.

        Args:
            entity_id: Entity identifier
            limit: Maximum results
            offset: Results to skip

        Returns:
            Tuple of (logs, total_count)
        """
        filter_dict = {"entity_id": entity_id}

        # Get total count
        total = await self.repo.count_documents(filter_dict)

        # Get paginated results
        docs = await self.repo.find_many(
            filter_dict=filter_dict,
            sort=[("timestamp", -1)],
            limit=limit,
            skip=offset
        )

        logs = []
        for doc in docs:
            normalized_doc = self._normalize_audit_doc(doc)
            logs.append(AuditLogEntry(**normalized_doc))

        return logs, total

    async def get_logs_by_actor(
        self,
        actor_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> tuple[list[AuditLogEntry], int]:
        """
        Get all audit logs for a specific actor.

        Args:
            actor_id: Actor identifier
            limit: Maximum results
            offset: Results to skip

        Returns:
            Tuple of (logs, total_count)
        """
        filter_dict = {"actor_id": actor_id}

        # Get total count
        total = await self.repo.count_documents(filter_dict)

        # Get paginated results
        docs = await self.repo.find_many(
            filter_dict=filter_dict,
            sort=[("timestamp", -1)],
            limit=limit,
            skip=offset
        )

        logs = []
        for doc in docs:
            normalized_doc = self._normalize_audit_doc(doc)
            logs.append(AuditLogEntry(**normalized_doc))

        return logs, total

    async def search_logs(
        self,
        entity_id: Optional[str] = None,
        entity_type: Optional[str] = None,
        actor_id: Optional[str] = None,
        actor_type: Optional[str] = None,
        event_type: Optional[EventType] = None,
        transaction_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 50,
        offset: int = 0
    ) -> tuple[list[AuditLogEntry], int]:
        """
        Search audit logs by multiple criteria.

        Args:
            entity_id: Filter by entity ID
            entity_type: Filter by entity type
            actor_id: Filter by actor ID
            actor_type: Filter by actor type
            event_type: Filter by event type
            transaction_id: Filter by transaction ID
            start_time: Filter by start timestamp (inclusive)
            end_time: Filter by end timestamp (inclusive)
            limit: Maximum results
            offset: Results to skip

        Returns:
            Tuple of (logs, total_count)
        """
        filter_dict = {}

        if entity_id:
            filter_dict["entity_id"] = entity_id
        if entity_type:
            filter_dict["entity_type"] = entity_type
        if actor_id:
            filter_dict["actor_id"] = actor_id
        if actor_type:
            filter_dict["actor_type"] = actor_type
        if event_type:
            filter_dict["event_type"] = event_type.value
        if transaction_id:
            filter_dict["transaction_id"] = transaction_id

        # Time range filter
        if start_time or end_time:
            time_filter = {}
            if start_time:
                time_filter["$gte"] = start_time
            if end_time:
                time_filter["$lte"] = end_time
            filter_dict["timestamp"] = time_filter

        # Get total count
        total = await self.repo.count_documents(filter_dict)

        # Get paginated results
        docs = await self.repo.find_many(
            filter_dict=filter_dict,
            sort=[("timestamp", -1)],
            limit=limit,
            skip=offset
        )

        logs = []
        for doc in docs:
            normalized_doc = self._normalize_audit_doc(doc)
            logs.append(AuditLogEntry(**normalized_doc))

        return logs, total

    async def get_recent_logs(
        self,
        limit: int = 100
    ) -> list[AuditLogEntry]:
        """
        Get most recent audit logs.

        Args:
            limit: Maximum results

        Returns:
            List of recent audit logs
        """
        docs = await self.repo.find_many(
            filter_dict={},
            sort=[("timestamp", -1)],
            limit=limit
        )

        logs = []
        for doc in docs:
            doc.pop("_id", None)
            logs.append(AuditLogEntry(**doc))

        return logs

    async def count_logs_by_event_type(self) -> dict[str, int]:
        """
        Count audit logs grouped by event type.

        Returns:
            Dict mapping event type to count
        """
        pipeline = [
            {
                "$group": {
                    "_id": "$event_type",
                    "count": {"$sum": 1}
                }
            }
        ]

        results = await self.repo.aggregate(pipeline)

        return {
            result["_id"]: result["count"]
            for result in results
        }

    async def get_entity_activity_summary(
        self,
        entity_id: str
    ) -> dict:
        """
        Get activity summary for an entity.

        Args:
            entity_id: Entity identifier

        Returns:
            Summary dict matching AuditTrailSummary model
        """
        # Get entity info and event data
        logs = await self.repo.find_many(
            filter_dict={"entity_id": entity_id},
            sort=[("timestamp", 1)],  # oldest first for first_event_at
            limit=None
        )

        if not logs:
            return None

        # Extract entity_type from first log
        entity_type = logs[0].get("entity_type", "Unknown")

        # Calculate event type counts
        event_type_counts = {}
        for log in logs:
            event_type = log.get("event_type", "Unknown")
            event_type_counts[event_type] = event_type_counts.get(event_type, 0) + 1

        # Calculate actor counts
        actor_counts = {}
        for log in logs:
            actor_id = log.get("actor_id", "Unknown")
            actor_counts[actor_id] = actor_counts.get(actor_id, 0) + 1

        # Get first and last timestamps
        first_event_at = logs[0].get("timestamp")
        last_event_at = logs[-1].get("timestamp")

        summary = {
            "entity_id": entity_id,
            "entity_type": entity_type,
            "total_events": len(logs),
            "first_event_at": first_event_at,
            "last_event_at": last_event_at,
            "event_type_counts": event_type_counts,
            "actor_counts": actor_counts
        }

        return summary




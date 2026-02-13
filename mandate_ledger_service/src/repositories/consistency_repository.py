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
Consistency repository for data integrity checks.

Handles all database operations for consistency checking.
"""

from typing import Optional
from datetime import datetime, timezone

from src.repositories.base_repository import BaseRepository
from src.db.mongodb import MongoDB
from src.models.admin import ConsistencyCheckResult
from src.models.enums import ConsistencyIssueType


class ConsistencyRepository:
    """
    Repository for consistency check operations.

    Provides methods for:
    - Creating consistency check records
    - Querying unresolved issues
    - Marking issues as resolved
    """

    def __init__(self):
        """Initialize the consistency repository."""
        self.repo = BaseRepository(MongoDB.consistency_checks)

    async def create_consistency_check(
        self,
        entity_id: str,
        entity_type: str,
        issue_type: ConsistencyIssueType,
        issue_description: str,
        ledger_version: Optional[int] = None,
        current_state_version: Optional[int] = None,
        discrepancy_details: Optional[dict] = None,
        severity: str = "error"
    ) -> ConsistencyCheckResult:
        """
        Create a new consistency check record.

        Args:
            entity_id: Entity with consistency issue
            entity_type: Type of entity (INTENT, CART, PAYMENT)
            issue_type: Type of consistency issue
            issue_description: Human-readable description
            ledger_version: Version in ledger
            current_state_version: Version in current_state
            discrepancy_details: Details about the discrepancy
            severity: Severity level (info, warning, error, critical)

        Returns:
            Created consistency check result
        """
        check_dict = {
            "entity_id": entity_id,
            "entity_type": entity_type,
            "issue_type": issue_type.value,
            "issue_description": issue_description,
            "ledger_version": ledger_version,
            "current_state_version": current_state_version,
            "discrepancy_details": discrepancy_details or {},
            "severity": severity,
            "check_timestamp": datetime.now(timezone.utc),
            "resolved_at": None,
            "resolved_by": None,
            "resolution_notes": None
        }

        await self.repo.insert_one(check_dict)
        return ConsistencyCheckResult(**check_dict)

    async def get_unresolved_issues(
        self,
        entity_id: Optional[str] = None,
        entity_type: Optional[str] = None,
        issue_type: Optional[ConsistencyIssueType] = None,
        severity: Optional[str] = None,
        limit: Optional[int] = None
    ) -> list[ConsistencyCheckResult]:
        """
        Get unresolved consistency issues.

        Args:
            entity_id: Optional filter by entity
            entity_type: Optional filter by entity type
            issue_type: Optional filter by issue type
            severity: Optional filter by severity
            limit: Optional limit on results

        Returns:
            List of unresolved consistency check results
        """
        filter_dict = {"resolved_at": None}

        if entity_id:
            filter_dict["entity_id"] = entity_id
        if entity_type:
            filter_dict["entity_type"] = entity_type
        if issue_type:
            filter_dict["issue_type"] = issue_type.value
        if severity:
            filter_dict["severity"] = severity

        results = await self.repo.find_many(
            filter_dict=filter_dict,
            limit=limit,
            sort=[("check_timestamp", -1)]
        )

        return [ConsistencyCheckResult(**r) for r in results]

    async def mark_resolved(
        self,
        entity_id: str,
        issue_type: ConsistencyIssueType,
        resolved_by: str,
        resolution_notes: Optional[str] = None
    ) -> int:
        """
        Mark consistency issues as resolved.

        Args:
            entity_id: Entity identifier
            issue_type: Type of issue to mark resolved
            resolved_by: Who/what resolved the issue
            resolution_notes: Optional notes about resolution

        Returns:
            Number of issues marked as resolved
        """
        return await self.repo.update_many(
            filter_dict={
                "entity_id": entity_id,
                "issue_type": issue_type.value,
                "resolved_at": None
            },
            update={
                "$set": {
                    "resolved_at": datetime.now(timezone.utc),
                    "resolved_by": resolved_by,
                    "resolution_notes": resolution_notes
                }
            }
        )

    async def get_consistency_stats(self) -> dict:
        """
        Get statistics about consistency issues.

        Returns:
            Dict with counts by issue type, severity, etc.
        """
        pipeline = [
            {
                "$facet": {
                    "by_type": [
                        {"$group": {"_id": "$issue_type", "count": {"$sum": 1}}}
                    ],
                    "by_severity": [
                        {"$group": {"_id": "$severity", "count": {"$sum": 1}}}
                    ],
                    "resolved_vs_unresolved": [
                        {
                            "$group": {
                                "_id": {
                                    "$cond": [
                                        {"$eq": ["$resolved_at", None]},
                                        "unresolved",
                                        "resolved"
                                    ]
                                },
                                "count": {"$sum": 1}
                            }
                        }
                    ]
                }
            }
        ]

        cursor = self.repo.collection.aggregate(pipeline)
        results = await cursor.to_list(length=1)

        if results:
            return results[0]
        return {
            "by_type": [],
            "by_severity": [],
            "resolved_vs_unresolved": []
        }

    async def delete_resolved_older_than(self, days: int) -> int:
        """
        Delete resolved consistency checks older than specified days.

        Args:
            days: Delete resolved issues older than this many days

        Returns:
            Number of records deleted
        """
        from datetime import timedelta
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)

        return await self.repo.delete_many({
            "resolved_at": {"$lt": cutoff, "$ne": None}
        })

    async def get_entity_consistency_history(
        self,
        entity_id: str,
        limit: Optional[int] = None
    ) -> list[ConsistencyCheckResult]:
        """
        Get consistency check history for an entity.

        Args:
            entity_id: Entity identifier
            limit: Optional limit on results

        Returns:
            List of consistency check results (newest first)
        """
        results = await self.repo.find_many(
            filter_dict={"entity_id": entity_id},
            limit=limit,
            sort=[("check_timestamp", -1)]
        )

        return [ConsistencyCheckResult(**r) for r in results]





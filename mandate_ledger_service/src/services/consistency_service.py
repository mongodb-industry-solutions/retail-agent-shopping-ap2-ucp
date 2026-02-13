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
Consistency service for data integrity checks.

Orchestrates consistency checking and health monitoring.
Note: Auto-repair functionality removed as current_state collection was deprecated.
Current state is now derived directly from the ledger (latest version).
"""

from typing import Optional
from datetime import datetime, timezone

from src.repositories import (
    ConsistencyRepository,
    MandateRepository,
    AuditRepository
)
from src.models.admin import ConsistencyCheckResult
from src.models.enums import ConsistencyIssueType, EventType


class ConsistencyService:
    """
    Service for data integrity and consistency checking.

    Provides high-level operations for:
    - Running consistency checks on ledger entries
    - Health monitoring
    - Query operations for consistency issues
    """

    def __init__(
        self,
        consistency_repo: Optional[ConsistencyRepository] = None,
        mandate_repo: Optional[MandateRepository] = None,
        audit_repo: Optional[AuditRepository] = None
    ):
        """
        Initialize the consistency service.

        Args:
            consistency_repo: Consistency repository (creates new if None)
            mandate_repo: Mandate repository (creates new if None)
            audit_repo: Audit repository (creates new if None)
        """
        self.consistency_repo = consistency_repo or ConsistencyRepository()
        self.mandate_repo = mandate_repo or MandateRepository()
        self.audit_repo = audit_repo or AuditRepository()

    # ==================== Consistency Checking ====================

    async def check_mandate_consistency(
        self,
        entity_id: str
    ) -> list[ConsistencyCheckResult]:
        """
        Check consistency for a specific mandate.

        Verifies the ledger entry exists and has valid data.

        Args:
            entity_id: Mandate identifier

        Returns:
            List of consistency check results (empty if consistent)
        """
        issues = []

        try:
            # Get latest ledger entry (current state is derived from ledger)
            latest_entry = await self.mandate_repo.get_latest_ledger_entry(entity_id)

            if not latest_entry:
                issue = await self.consistency_repo.create_consistency_check(
                    entity_id=entity_id,
                    entity_type="unknown",
                    issue_type=ConsistencyIssueType.MISSING_LEDGER_ENTRY,
                    issue_description=f"No ledger entry found for entity {entity_id}",
                    ledger_version=None,
                    current_state_version=None,
                    severity="critical"
                )
                issues.append(issue)
                return issues

            # Verify version chain integrity
            history = await self.mandate_repo.get_ledger_history(entity_id)
            if history:
                expected_version = 1
                for entry in sorted(history, key=lambda x: x.version):
                    if entry.version != expected_version:
                        issue = await self.consistency_repo.create_consistency_check(
                            entity_id=entity_id,
                            entity_type=entry.entity_type.value,
                            issue_type=ConsistencyIssueType.VERSION_MISMATCH,
                            issue_description=f"Version gap: expected {expected_version}, found {entry.version}",
                            ledger_version=entry.version,
                            current_state_version=None,
                            severity="error"
                        )
                        issues.append(issue)
                    expected_version = entry.version + 1

            return issues

        except Exception as e:
            import logging
            logging.error(f"Consistency check failed for {entity_id}: {e}")
            return issues

    async def run_full_scan(
        self,
        limit: Optional[int] = None
    ) -> dict:
        """
        Run consistency check across all mandates.

        Args:
            limit: Optional limit on number of mandates to check

        Returns:
            Summary of scan results
        """
        # Get all unique entity IDs from ledger
        pipeline = [
            {"$group": {"_id": "$entity_id"}},
            {"$limit": limit or 10000}
        ]

        cursor = self.mandate_repo.ledger_repo.collection.aggregate(pipeline)
        entity_ids = [doc["_id"] async for doc in cursor]

        total_checked = 0
        issues_found = 0

        for entity_id in entity_ids:
            total_checked += 1
            issues = await self.check_mandate_consistency(entity_id)
            issues_found += len(issues)

        # Log scan in audit trail
        await self.audit_repo.create_audit_log(
            event_type=EventType.SYSTEM_MAINTENANCE,
            entity_id="consistency-scan",
            entity_type="system",
            entity_version=None,
            actor_id="consistency-service",
            actor_type="system",
            action="Full consistency scan completed",
            metadata={
                "total_checked": total_checked,
                "issues_found": issues_found
            }
        )

        return {
            "scan_timestamp": datetime.now(timezone.utc).isoformat(),
            "total_checked": total_checked,
            "issues_found": issues_found
        }

    # ==================== Health Monitoring ====================

    async def get_health_report(self) -> dict:
        """
        Get overall data integrity health report.

        Returns:
            Health metrics and statistics
        """
        stats = await self.consistency_repo.get_consistency_stats()

        unresolved_issues = sum(
            item.get('count', 0)
            for item in stats.get('resolved_vs_unresolved', [])
            if item.get('_id') == 'unresolved'
        )

        total_checks = sum(
            item.get('count', 0)
            for item in stats.get('resolved_vs_unresolved', [])
        )

        health_score = 100 if total_checks == 0 else max(0, 100 - (unresolved_issues / max(1, total_checks) * 100))

        if health_score >= 95:
            health_status = "healthy"
        elif health_score >= 80:
            health_status = "degraded"
        else:
            health_status = "unhealthy"

        return {
            "health_status": health_status,
            "health_score": round(health_score, 2),
            "total_checks": total_checks,
            "unresolved_issues": unresolved_issues,
            "by_severity": stats.get('by_severity', []),
            "by_type": stats.get('by_type', []),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    # ==================== Query Operations ====================

    async def get_unresolved_issues(
        self,
        severity: Optional[str] = None,
        limit: Optional[int] = 100
    ) -> list[ConsistencyCheckResult]:
        """
        Get unresolved consistency issues.

        Args:
            severity: Optional filter by severity
            limit: Maximum results

        Returns:
            List of unresolved consistency check results
        """
        return await self.consistency_repo.get_unresolved_issues(
            severity=severity,
            limit=limit
        )

    async def resolve_issue(
        self,
        entity_id: str,
        issue_type: ConsistencyIssueType,
        resolved_by: str,
        resolution_notes: Optional[str] = None
    ) -> int:
        """
        Mark consistency issue as resolved.

        Args:
            entity_id: Entity identifier
            issue_type: Type of issue
            resolved_by: Who resolved it
            resolution_notes: Optional notes

        Returns:
            Number of issues resolved
        """
        return await self.consistency_repo.mark_resolved(
            entity_id=entity_id,
            issue_type=issue_type,
            resolved_by=resolved_by,
            resolution_notes=resolution_notes
        )

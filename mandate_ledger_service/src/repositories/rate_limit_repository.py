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
Rate limit repository for API rate limiting.

Handles all database operations for rate limit tracking.
"""

from typing import Optional
from datetime import datetime, timezone, timedelta

from src.repositories.base_repository import BaseRepository
from src.db.mongodb import MongoDB
from src.core.errors import RateLimitExceededError


class RateLimitRepository:
    """
    Repository for rate limit operations.

    Provides methods for:
    - Checking and incrementing request counts
    - Managing rate limit windows
    - Querying agent usage
    """

    def __init__(self):
        """Initialize the rate limit repository."""
        self.repo = BaseRepository(MongoDB.rate_limits)

    async def check_and_increment(
        self,
        agent_id: str,
        limit_per_minute: int,
        window_seconds: int = 60
    ) -> tuple[int, datetime]:
        """
        Check rate limit and increment counter atomically.

        This uses MongoDB's upsert with increment to handle concurrency safely.

        Args:
            agent_id: Agent identifier
            limit_per_minute: Maximum requests per minute
            window_seconds: Time window in seconds (default 60)

        Returns:
            Tuple of (current_count, window_start)

        Raises:
            RateLimitExceededError: If rate limit is exceeded
        """
        now = datetime.now(timezone.utc)

        # Calculate window start (truncate to minute)
        window_start = now.replace(second=0, microsecond=0)

        # Try to increment the counter
        result = await self.repo.collection.find_one_and_update(
            {
                "agent_id": agent_id,
                "window_start": window_start
            },
            {
                "$inc": {"request_count": 1},
                "$setOnInsert": {
                    "agent_id": agent_id,
                    "window_start": window_start,
                    "window_end": window_start + timedelta(seconds=window_seconds)
                }
            },
            upsert=True,
            return_document=True
        )

        current_count = result["request_count"]

        # Check if limit exceeded
        if current_count > limit_per_minute:
            window_end = result["window_end"]
            reset_at = window_end.isoformat()

            raise RateLimitExceededError(
                agent_id=agent_id,
                limit=limit_per_minute,
                reset_at=reset_at
            )

        return current_count, window_start

    async def get_agent_usage(
        self,
        agent_id: str,
        window_start: Optional[datetime] = None
    ) -> Optional[dict]:
        """
        Get current rate limit usage for an agent.

        Args:
            agent_id: Agent identifier
            window_start: Optional specific window (defaults to current minute)

        Returns:
            Dict with request_count and window info, or None if no record
        """
        if window_start is None:
            window_start = datetime.now(timezone.utc).replace(second=0, microsecond=0)

        result = await self.repo.find_one({
            "agent_id": agent_id,
            "window_start": window_start
        })

        return result

    async def reset_agent_limits(self, agent_id: str) -> int:
        """
        Reset all rate limit windows for an agent.

        Useful for admin operations or testing.

        Args:
            agent_id: Agent identifier

        Returns:
            Number of records deleted
        """
        return await self.repo.delete_many({"agent_id": agent_id})

    async def cleanup_old_windows(self, older_than_hours: int = 24) -> int:
        """
        Clean up old rate limit windows.

        Args:
            older_than_hours: Delete windows older than this many hours

        Returns:
            Number of records deleted
        """
        cutoff = datetime.now(timezone.utc) - timedelta(hours=older_than_hours)
        return await self.repo.delete_many({
            "window_end": {"$lt": cutoff}
        })

    async def get_top_agents_by_usage(
        self,
        since: Optional[datetime] = None,
        limit: int = 10
    ) -> list[dict]:
        """
        Get agents with highest request counts.

        Args:
            since: Optional start time (default: last hour)
            limit: Maximum number of results

        Returns:
            List of dicts with agent_id and total_requests
        """
        if since is None:
            since = datetime.now(timezone.utc) - timedelta(hours=1)

        pipeline = [
            {"$match": {"window_start": {"$gte": since}}},
            {
                "$group": {
                    "_id": "$agent_id",
                    "total_requests": {"$sum": "$request_count"}
                }
            },
            {"$sort": {"total_requests": -1}},
            {"$limit": limit},
            {
                "$project": {
                    "_id": 0,
                    "agent_id": "$_id",
                    "total_requests": 1
                }
            }
        ]

        cursor = self.repo.collection.aggregate(pipeline)
        return await cursor.to_list(length=limit)





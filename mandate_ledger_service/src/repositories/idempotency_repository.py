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
Idempotency repository for request deduplication.

Handles all database operations for idempotency records.
"""

from typing import Optional
from datetime import datetime, timezone, timedelta

from src.repositories.base_repository import BaseRepository
from src.db.mongodb import MongoDB
from src.models.admin import IdempotencyRecord


class IdempotencyRepository:
    """
    Repository for idempotency record operations.

    Provides methods for:
    - Checking if a request has already been processed
    - Storing request results for deduplication
    - Cleaning up expired records
    """

    def __init__(self):
        """Initialize the idempotency repository."""
        self.repo = BaseRepository(MongoDB.idempotency_records)

    async def check_idempotency_key(
        self,
        idempotency_key: str,
        agent_id: str
    ) -> Optional[IdempotencyRecord]:
        """
        Check if an idempotency key has already been processed.

        Args:
            idempotency_key: Idempotency key from request header
            agent_id: Agent making the request

        Returns:
            IdempotencyRecord if key exists and not expired, None otherwise
        """
        record = await self.repo.find_one({
            "idempotency_key": idempotency_key,
            "agent_id": agent_id,
            "expires_at": {"$gt": datetime.now(timezone.utc)}
        })

        if record:
            return IdempotencyRecord(**record)
        return None

    async def store_idempotency_record(
        self,
        idempotency_key: str,
        agent_id: str,
        request_method: str,
        request_path: str,
        request_body: dict,
        response_status: int,
        response_body: dict,
        ttl_hours: int = 24
    ) -> IdempotencyRecord:
        """
        Store the result of a request for idempotency checking.

        Args:
            idempotency_key: Idempotency key from request header
            agent_id: Agent making the request
            request_method: HTTP method (POST, PUT, etc.)
            request_path: API endpoint path
            request_body: Request body
            response_status: HTTP response status code
            response_body: Response body
            ttl_hours: Time-to-live in hours (default 24h)

        Returns:
            Created idempotency record
        """
        expires_at = datetime.now(timezone.utc) + timedelta(hours=ttl_hours)

        record_dict = {
            "idempotency_key": idempotency_key,
            "agent_id": agent_id,
            "request_method": request_method,
            "endpoint": request_path,
            "request_body": request_body,
            "response_status_code": response_status,
            "response_body": response_body,
            "first_request_at": datetime.now(timezone.utc),
            "expires_at": expires_at
        }

        await self.repo.insert_one(record_dict)
        return IdempotencyRecord(**record_dict)

    async def cleanup_expired_records(self) -> int:
        """
        Clean up expired idempotency records.

        Note: MongoDB TTL index handles this automatically, but this
        method is provided for manual cleanup if needed.

        Returns:
            Number of records deleted
        """
        result = await self.repo.delete_many({
            "expires_at": {"$lt": datetime.now(timezone.utc)}
        })
        return result

    async def get_agent_idempotency_count(
        self,
        agent_id: str,
        since: Optional[datetime] = None
    ) -> int:
        """
        Get count of idempotency records for an agent.

        Args:
            agent_id: Agent identifier
            since: Optional start time (default: last 24 hours)

        Returns:
            Count of idempotency records
        """
        if since is None:
            since = datetime.now(timezone.utc) - timedelta(hours=24)

        return await self.repo.count_documents({
            "agent_id": agent_id,
            "first_request_at": {"$gte": since}
        })

    async def delete_agent_records(self, agent_id: str) -> int:
        """
        Delete all idempotency records for an agent.

        Used when an agent is removed or for cleanup.

        Args:
            agent_id: Agent identifier

        Returns:
            Number of records deleted
        """
        return await self.repo.delete_many({"agent_id": agent_id})





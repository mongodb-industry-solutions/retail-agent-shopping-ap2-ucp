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
Idempotency service for request deduplication.

Encapsulates idempotency checking and storage logic.
"""

import secrets
from typing import Optional
from datetime import datetime, timezone

from src.repositories import IdempotencyRepository
from src.models.admin import IdempotencyRecord


class IdempotencyService:
    """
    Service for idempotency management.

    Provides high-level operations for:
    - Checking for duplicate requests
    - Storing request/response pairs
    - Generating idempotency keys
    - Cleanup and statistics
    """

    def __init__(
        self,
        idempotency_repo: Optional[IdempotencyRepository] = None
    ):
        """
        Initialize the idempotency service.

        Args:
            idempotency_repo: Idempotency repository (creates new if None)
        """
        self.idempotency_repo = idempotency_repo or IdempotencyRepository()

    # ==================== Idempotency Checking ====================

    async def check_request(
        self,
        idempotency_key: str,
        agent_id: str
    ) -> Optional[IdempotencyRecord]:
        """
        Check if a request has already been processed.

        Args:
            idempotency_key: Idempotency key from request header
            agent_id: Agent making the request

        Returns:
            IdempotencyRecord if duplicate request, None otherwise
        """
        return await self.idempotency_repo.check_idempotency_key(
            idempotency_key=idempotency_key,
            agent_id=agent_id
        )

    async def store_result(
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
        Store request/response for idempotency checking.

        Args:
            idempotency_key: Idempotency key from request header
            agent_id: Agent making the request
            request_method: HTTP method (POST, PUT, etc.)
            request_path: API endpoint path
            request_body: Request payload
            response_status: HTTP response status code
            response_body: Response payload
            ttl_hours: Time-to-live in hours (default 24h)

        Returns:
            Created idempotency record
        """
        return await self.idempotency_repo.store_idempotency_record(
            idempotency_key=idempotency_key,
            agent_id=agent_id,
            request_method=request_method,
            request_path=request_path,
            request_body=request_body,
            response_status=response_status,
            response_body=response_body,
            ttl_hours=ttl_hours
        )

    async def check_and_store(
        self,
        idempotency_key: str,
        agent_id: str,
        request_method: str,
        request_path: str,
        request_body: dict,
        process_fn,
        ttl_hours: int = 24
    ) -> tuple[dict, int, bool]:
        """
        Check for duplicate and store result in one operation.

        This is a convenience method that:
        1. Checks for existing idempotency record
        2. Returns cached response if found
        3. Otherwise, calls process_fn and stores result

        Args:
            idempotency_key: Idempotency key
            agent_id: Agent ID
            request_method: HTTP method
            request_path: API path
            request_body: Request payload
            process_fn: Async function to process request (returns status, body)
            ttl_hours: TTL in hours

        Returns:
            Tuple of (response_body, status_code, is_cached)
        """
        # Check for duplicate
        existing = await self.check_request(idempotency_key, agent_id)

        if existing:
            # Return cached response
            return existing.response_body, existing.response_status, True

        # Process request
        status_code, response_body = await process_fn()

        # Store result
        await self.store_result(
            idempotency_key=idempotency_key,
            agent_id=agent_id,
            request_method=request_method,
            request_path=request_path,
            request_body=request_body,
            response_status=status_code,
            response_body=response_body,
            ttl_hours=ttl_hours
        )

        return response_body, status_code, False

    # ==================== Key Generation ====================

    @staticmethod
    def generate_idempotency_key(prefix: str = "req") -> str:
        """
        Generate a unique idempotency key.

        Useful for clients that need to generate idempotency keys.

        Args:
            prefix: Optional prefix for the key

        Returns:
            Unique idempotency key in format: {prefix}_{timestamp}_{random}

        Example:
            req_20251114123045_a1b2c3d4
        """
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        random_part = secrets.token_hex(4)  # 8 characters
        return f"{prefix}_{timestamp}_{random_part}"

    # ==================== Cleanup & Statistics ====================

    async def cleanup_expired(self) -> int:
        """
        Clean up expired idempotency records.

        Note: MongoDB TTL index handles this automatically,
        but this method provides manual cleanup if needed.

        Returns:
            Number of records deleted
        """
        return await self.idempotency_repo.cleanup_expired_records()

    async def get_agent_statistics(
        self,
        agent_id: str,
        since: Optional[datetime] = None
    ) -> dict:
        """
        Get idempotency statistics for an agent.

        Args:
            agent_id: Agent identifier
            since: Optional start time (default: last 24 hours)

        Returns:
            Statistics dictionary
        """
        count = await self.idempotency_repo.get_agent_idempotency_count(
            agent_id=agent_id,
            since=since
        )

        return {
            "agent_id": agent_id,
            "idempotent_requests": count,
            "since": (since or datetime.now(timezone.utc)).isoformat(),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    async def delete_agent_records(self, agent_id: str) -> int:
        """
        Delete all idempotency records for an agent.

        Used when an agent is removed or for cleanup.

        Args:
            agent_id: Agent identifier

        Returns:
            Number of records deleted
        """
        return await self.idempotency_repo.delete_agent_records(agent_id)





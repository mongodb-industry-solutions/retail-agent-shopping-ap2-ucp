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
Auth repository for API key operations.

Handles all database operations for authentication and authorization.
"""

from typing import Optional
from datetime import datetime, timezone

from src.repositories.base_repository import BaseRepository
from src.db.mongodb import MongoDB
from src.models.auth import ApiKey
from src.core.errors import InvalidApiKeyError


class AuthRepository:
    """
    Repository for API key operations.

    Provides methods for:
    - Creating API keys
    - Verifying API keys
    - Managing key lifecycle (revoke, expire)
    - Querying keys by agent
    """

    def __init__(self):
        """Initialize the auth repository."""
        self.repo = BaseRepository(MongoDB.api_keys)

    async def create_api_key(
        self,
        key_id: str,
        agent_id: str,
        agent_type: str,
        hashed_key: str,
        key_prefix: str,
        permissions: list[str],
        created_by: str,
        expires_at: Optional[datetime] = None,
        metadata: Optional[dict] = None
    ) -> ApiKey:
        """
        Create a new API key.

        Args:
            key_id: Unique key identifier
            agent_id: Agent identifier
            agent_type: Type of agent
            hashed_key: Bcrypt hash of the API key
            key_prefix: First 8 chars of key (for display)
            permissions: List of permission scopes
            expires_at: Optional expiration time
            metadata: Optional metadata

        Returns:
            Created API key record
        """
        key_dict = {
            "key_id": key_id,
            "agent_id": agent_id,
            "agent_type": agent_type,
            "key_hash": hashed_key,  # Fixed: model expects key_hash not hashed_key
            "key_prefix": key_prefix,
            "permissions": permissions,  # Fixed: model expects permissions not scopes
            "created_by": created_by,  # Added: required field
            "status": "active",  # Fixed: model expects status not is_active
            "created_at": datetime.now(timezone.utc),
            "expires_at": expires_at,
            "revoked_at": None,
            "last_used_at": None,
            "total_requests": 0,  # Fixed: model expects total_requests not usage_count
            "metadata": metadata or {}
        }

        await self.repo.insert_one(key_dict)

        return ApiKey(**key_dict)

    async def get_api_key_by_id(self, key_id: str) -> Optional[ApiKey]:
        """
        Get API key by key ID.

        Args:
            key_id: Key identifier

        Returns:
            API key or None
        """
        doc = await self.repo.find_one({"key_id": key_id})

        if doc:
            doc.pop("_id", None)
            return ApiKey(**doc)
        return None

    async def get_api_key_by_prefix(self, key_prefix: str) -> Optional[ApiKey]:
        """
        Get API key by key prefix.

        Args:
            key_prefix: First 8 chars of key

        Returns:
            API key or None
        """
        doc = await self.repo.find_one({"key_prefix": key_prefix})

        if doc:
            doc.pop("_id", None)
            return ApiKey(**doc)
        return None

    async def get_active_keys_by_agent(
        self,
        agent_id: str
    ) -> list[ApiKey]:
        """
        Get all active API keys for an agent.

        Args:
            agent_id: Agent identifier

        Returns:
            List of active API keys
        """
        docs = await self.repo.find_many(
            filter_dict={
                "agent_id": agent_id,
                "status": "active",
                "revoked_at": None
            },
            sort=[("created_at", -1)]
        )

        keys = []
        for doc in docs:
            doc.pop("_id", None)
            keys.append(ApiKey(**doc))

        return keys

    async def get_all_keys_by_agent(
        self,
        agent_id: str,
        include_revoked: bool = False
    ) -> list[ApiKey]:
        """
        Get all API keys for an agent.

        Args:
            agent_id: Agent identifier
            include_revoked: Include revoked keys

        Returns:
            List of API keys
        """
        filter_dict = {"agent_id": agent_id}

        if not include_revoked:
            filter_dict["revoked_at"] = None

        docs = await self.repo.find_many(
            filter_dict=filter_dict,
            sort=[("created_at", -1)]
        )

        keys = []
        for doc in docs:
            doc.pop("_id", None)
            keys.append(ApiKey(**doc))

        return keys

    async def update_last_used(self, key_id: str) -> int:
        """
        Update last_used_at and increment total_requests.

        Args:
            key_id: Key identifier

        Returns:
            Number of documents modified
        """
        return await self.repo.update_one(
            filter_dict={"key_id": key_id},
            update={
                "$set": {"last_used_at": datetime.now(timezone.utc)},
                "$inc": {"total_requests": 1}
            }
        )

    async def revoke_api_key(self, key_id: str) -> int:
        """
        Revoke an API key.

        Args:
            key_id: Key identifier

        Returns:
            Number of documents modified
        """
        return await self.repo.update_one(
            filter_dict={"key_id": key_id},
            update={
                "$set": {
                    "status": "revoked",
                    "revoked_at": datetime.now(timezone.utc)
                }
            }
        )

    async def revoke_all_agent_keys(self, agent_id: str) -> int:
        """
        Revoke all API keys for an agent.

        Args:
            agent_id: Agent identifier

        Returns:
            Number of documents modified
        """
        return await self.repo.update_many(
            filter_dict={
                "agent_id": agent_id,
                "status": "active"
            },
            update={
                "$set": {
                    "status": "revoked",
                    "revoked_at": datetime.now(timezone.utc)
                }
            }
        )

    async def delete_api_key(self, key_id: str) -> int:
        """
        Delete an API key (hard delete).

        WARNING: This is a destructive operation. Prefer revoking keys.

        Args:
            key_id: Key identifier

        Returns:
            Number of documents deleted
        """
        return await self.repo.delete_one({"key_id": key_id})

    async def count_active_keys(self) -> int:
        """
        Count total active API keys.

        Returns:
            Count of active keys
        """
        return await self.repo.count_documents({
            "status": "active",
            "revoked_at": None
        })

    async def count_keys_by_agent_type(self, agent_type: str) -> int:
        """
        Count API keys by agent type.

        Args:
            agent_type: Type of agent

        Returns:
            Count of keys
        """
        return await self.repo.count_documents({
            "agent_type": agent_type,
            "status": "active"
        })

    async def cleanup_expired_keys(self) -> int:
        """
        Deactivate expired API keys.

        Returns:
            Number of keys deactivated
        """
        now = datetime.now(timezone.utc)

        return await self.repo.update_many(
            filter_dict={
                "status": "active",
                "expires_at": {"$lte": now}
            },
            update={
                "$set": {"status": "expired"}
            }
        )




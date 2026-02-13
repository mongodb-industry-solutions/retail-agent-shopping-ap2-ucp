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
Authentication and authorization service.

Handles API key management and agent authentication.
"""

import secrets
from typing import Optional
from datetime import datetime, timezone, timedelta
from uuid import uuid4

from src.repositories import AuthRepository, AuditRepository
from src.models.auth import ApiKey, AuthenticatedAgent
from src.models.enums import EventType
from src.core.errors import (
    InvalidApiKeyError,
    ApiKeyExpiredError,
    ApiKeyRevokedError
)
from src.core.hashing import hash_api_key, verify_api_key, generate_api_key_prefix
from src.core.monitoring import track_auth_attempt
from src.config import settings


class AuthService:
    """
    Service for authentication and authorization.

    Provides high-level operations for API key management
    and agent authentication.
    """

    def __init__(
        self,
        auth_repo: Optional[AuthRepository] = None,
        audit_repo: Optional[AuditRepository] = None
    ):
        """
        Initialize the auth service.

        Args:
            auth_repo: Auth repository (creates new if None)
            audit_repo: Audit repository (creates new if None)
        """
        self.auth_repo = auth_repo or AuthRepository()
        self.audit_repo = audit_repo or AuditRepository()

    # ==================== API Key Generation ====================

    def generate_api_key(self) -> str:
        """
        Generate a new API key.

        Returns:
            API key in format: mlsk_<32_random_chars>

        Example:
            mlsk_1234567890abcdef1234567890abcdef
        """
        # Generate random key
        random_part = secrets.token_hex(16)  # 32 characters
        return f"mlsk_{random_part}"

    # ==================== API Key Management ====================

    async def create_api_key(
        self,
        agent_id: str,
        agent_type: str,
        scopes: list[str],
        created_by: str,
        expires_in_days: Optional[int] = None,
        metadata: Optional[dict] = None
    ) -> tuple[ApiKey, str]:
        """
        Create a new API key for an agent.

        Args:
            agent_id: Agent identifier
            agent_type: Type of agent
            scopes: List of permission scopes
            created_by: Admin/agent creating the key
            expires_in_days: Optional expiration in days
            metadata: Optional metadata

        Returns:
            Tuple of (ApiKey record, plaintext_key)
            WARNING: Plaintext key is only returned once!
        """
        # Generate key
        plaintext_key = self.generate_api_key()
        hashed_key = hash_api_key(plaintext_key)
        key_prefix = generate_api_key_prefix(plaintext_key, length=12)

        # Calculate expiration
        expires_at = None
        if expires_in_days:
            expires_at = datetime.now(timezone.utc) + timedelta(days=expires_in_days)

        # Create key record
        key_id = f"key_{uuid4()}"
        api_key = await self.auth_repo.create_api_key(
            key_id=key_id,
            agent_id=agent_id,
            agent_type=agent_type,
            hashed_key=hashed_key,
            key_prefix=key_prefix,
            permissions=scopes,
            created_by=created_by,
            expires_at=expires_at,
            metadata=metadata
        )

        # Log in audit trail
        await self.audit_repo.create_audit_log(
            event_type=EventType.API_KEY_CREATED,
            entity_id=key_id,
            entity_type="ApiKey",
            entity_version=None,
            actor_id=created_by,
            actor_type="admin",
            action=f"Created API key for agent {agent_id}",
            metadata={
                "agent_id": agent_id,
                "agent_type": agent_type,
                "scopes": scopes,
                "expires_at": expires_at.isoformat() if expires_at else None
            }
        )

        track_auth_attempt("key_created")

        return api_key, plaintext_key

    async def authenticate(
        self,
        api_key: str,
        required_scopes: Optional[list[str]] = None
    ) -> AuthenticatedAgent:
        """
        Authenticate an agent using an API key.

        Args:
            api_key: API key to authenticate
            required_scopes: Optional list of required scopes

        Returns:
            AuthenticatedAgent with agent info and permissions

        Raises:
            InvalidApiKeyError: If key is invalid
            ApiKeyExpiredError: If key has expired
            ApiKeyRevokedError: If key has been revoked
        """
        # Extract prefix for lookup
        key_prefix = generate_api_key_prefix(api_key, length=12)

        # Find key by prefix
        key_record = await self.auth_repo.get_api_key_by_prefix(key_prefix)

        if not key_record:
            track_auth_attempt("invalid_key")
            raise InvalidApiKeyError(key_prefix)

        # Verify hash
        if not verify_api_key(api_key, key_record.key_hash):
            track_auth_attempt("invalid_key")
            raise InvalidApiKeyError(key_prefix)

        # Check if revoked
        if key_record.status != "active" or key_record.revoked_at:
            track_auth_attempt("revoked")
            raise ApiKeyRevokedError(
                key_id=key_record.key_id,
                revoked_at=key_record.revoked_at.isoformat() if key_record.revoked_at else "unknown"
            )

        # Check if expired
        if key_record.expires_at:
            # Handle timezone-naive datetime from MongoDB
            expires_at = key_record.expires_at
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)

            if expires_at < datetime.now(timezone.utc):
                track_auth_attempt("expired")
                raise ApiKeyExpiredError(
                key_id=key_record.key_id,
                expired_at=key_record.expires_at.isoformat()
            )

        # Check scopes
        if required_scopes:
            if not all(scope in key_record.permissions for scope in required_scopes):
                track_auth_attempt("insufficient_permissions")
                raise InvalidApiKeyError(key_prefix)

        # Update last used
        await self.auth_repo.update_last_used(key_record.key_id)

        # Track success
        track_auth_attempt("success")

        return AuthenticatedAgent(
            agent_id=key_record.agent_id,
            agent_type=key_record.agent_type,
            agent_name=None,  # Optional - not stored in API key record
            key_id=key_record.key_id,
            permissions=key_record.permissions,  # Fixed: field is now permissions
            rate_limit_per_minute=settings.DEFAULT_RATE_LIMIT_PER_MINUTE
        )

    async def revoke_api_key(
        self,
        key_id: str,
        revoked_by: str,
        reason: Optional[str] = None
    ) -> bool:
        """
        Revoke an API key.

        Args:
            key_id: Key identifier
            revoked_by: Admin/agent revoking the key
            reason: Optional revocation reason

        Returns:
            True if key was revoked, False if not found
        """
        # Get key info before revoking
        key_record = await self.auth_repo.get_api_key_by_id(key_id)
        if not key_record:
            return False

        # Revoke key
        modified = await self.auth_repo.revoke_api_key(key_id)

        if modified > 0:
            # Log in audit trail
            await self.audit_repo.create_audit_log(
                event_type=EventType.API_KEY_REVOKED,
                entity_id=key_id,
                entity_type="ApiKey",
                entity_version=None,
                actor_id=revoked_by,
                actor_type="admin",
                action=f"Revoked API key for agent {key_record.agent_id}",
                metadata={
                    "agent_id": key_record.agent_id,
                    "agent_type": key_record.agent_type,
                    "reason": reason
                }
            )
            return True

        return False

    async def list_agent_keys(
        self,
        agent_id: str,
        include_revoked: bool = False
    ) -> list[ApiKey]:
        """
        List all API keys for an agent.

        Args:
            agent_id: Agent identifier
            include_revoked: Include revoked keys

        Returns:
            List of API keys
        """
        return await self.auth_repo.get_all_keys_by_agent(
            agent_id=agent_id,
            include_revoked=include_revoked
        )

    async def cleanup_expired_keys(self) -> int:
        """
        Deactivate all expired API keys.

        Returns:
            Number of keys deactivated
        """
        count = await self.auth_repo.cleanup_expired_keys()

        if count > 0:
            # Log in audit trail
            await self.audit_repo.create_audit_log(
                event_type=EventType.SYSTEM_HEALTH_CHECK_FAILED,
                entity_id="api_keys",
                entity_type="System",
                entity_version=None,
                actor_id="system",
                actor_type="system",
                action=f"Deactivated {count} expired API keys",
                metadata={"count": count}
            )

        return count




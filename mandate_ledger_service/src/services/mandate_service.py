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
Mandate service for business logic.

Handles mandate lifecycle, state transitions, and coordination.
"""

import asyncio
from typing import Optional
from uuid import uuid4
from datetime import datetime, timezone

from src.repositories import MandateRepository, AuditRepository
from src.models.mandate import MandateLedgerEntry, MandateCurrentState
from src.models.enums import MandateType, MandateStatus, EventType
from src.core.errors import (
    MandateNotFoundError,
    VersionConflictError,
    InvalidMandateDataError
)
from src.core.state_machine import (
    validate_transition,
    get_initial_status,
    is_terminal_status
)
from src.core.monitoring import track_mandate_operation


class MandateService:
    """
    Service for mandate business logic.

    Provides high-level operations that orchestrate repositories
    and enforce business rules.
    """

    def __init__(
        self,
        mandate_repo: Optional[MandateRepository] = None,
        audit_repo: Optional[AuditRepository] = None
    ):
        """
        Initialize the mandate service.

        Args:
            mandate_repo: Mandate repository (creates new if None)
            audit_repo: Audit repository (creates new if None)
        """
        self.mandate_repo = mandate_repo or MandateRepository()
        self.audit_repo = audit_repo or AuditRepository()

    # ==================== Create Operations ====================

    async def create_mandate(
        self,
        entity_type: MandateType,
        mandate_data: dict,
        created_by_agent: str,
        agent_type: str,
        transaction_id: Optional[str] = None,
        metadata: Optional[dict] = None,
        initial_signatures: Optional[list] = None,
        initial_status: Optional[MandateStatus] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> MandateLedgerEntry:
        """
        Create a new mandate.

        This creates both the ledger entry and current state record,
        and logs the operation in the audit trail.

        Args:
            entity_type: Type of mandate (INTENT, CART, PAYMENT)
            mandate_data: The AP2 mandate data
            created_by_agent: Agent creating the mandate
            agent_type: Type of agent (e.g., 'shopping-agent')
            transaction_id: Optional transaction ID
            metadata: Optional metadata
            initial_signatures: Optional list of signatures (for pre-signed mandates)
            initial_status: Optional status override (e.g., 'signed' for pre-signed mandates)

        Returns:
            Created ledger entry

        Raises:
            InvalidMandateDataError: If mandate data is invalid
        """
        # Generate IDs
        entity_id = f"{entity_type.value}_{uuid4()}"
        transaction_id = transaction_id or f"txn_{uuid4()}"

        # Determine status
        if initial_status:
            # Explicit status override
            status = initial_status
        elif initial_signatures:
            # If signatures provided, set to signed
            status = MandateStatus.SIGNED
        else:
            # Default behavior - get initial status for this mandate type
            status = get_initial_status(entity_type)

        try:
            # Create ledger entry with signatures
            ledger_entry = await self.mandate_repo.create_ledger_entry(
                entity_id=entity_id,
                entity_type=entity_type,
                mandate_data=mandate_data,
                status=status,
                created_by_agent=created_by_agent,
                created_by_agent_type=agent_type,
                transaction_id=transaction_id,
                metadata=metadata,
                signatures=initial_signatures or [],  # Include initial signatures if provided
                user_id=user_id,
                session_id=session_id
            )

            # NOTE: No longer creating current_state - it's queried from ledger

            # Log in audit trail
            action_text = f"Created {entity_type.value} mandate"
            if initial_signatures:
                action_text += " (pre-signed)"

            await self.audit_repo.create_audit_log(
                event_type=EventType.MANDATE_CREATED,
                entity_id=entity_id,
                entity_type=entity_type.value,
                entity_version=1,
                actor_id=created_by_agent,
                actor_type=agent_type,
                action=action_text,
                metadata=metadata or {},
                transaction_id=transaction_id
            )

            # Track metrics
            track_mandate_operation(
                operation="create",
                mandate_type=entity_type.value,
                success=True
            )

            return ledger_entry

        except Exception as e:
            # Track failure
            track_mandate_operation(
                operation="create",
                mandate_type=entity_type.value,
                success=False
            )
            raise

    # ==================== Create Version Operations ====================

    async def create_mandate_version(
        self,
        entity_id: str,
        mandate_data: dict,
        new_status: MandateStatus,
        updated_by_agent: str,
        agent_type: str,
        transaction_id: Optional[str] = None,
        metadata: Optional[dict] = None,
        signatures: Optional[list] = None,
        max_retries: int = 3,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> MandateLedgerEntry:
        """
        Create a new version of a mandate with optimistic locking retry logic.

        This APPENDS a new immutable version to the ledger while updating
        the current state cache for fast queries. The ledger remains immutable -
        old versions are never modified.

        This handles version conflicts by retrying with the latest version.

        Args:
            entity_id: Mandate identifier
            mandate_data: Updated mandate data
            new_status: New status
            updated_by_agent: Agent making the update
            agent_type: Type of agent
            transaction_id: Optional transaction ID
            metadata: Optional metadata
            signatures: Optional list of signature dicts
            max_retries: Maximum retry attempts for version conflicts

        Returns:
            New ledger entry

        Raises:
            MandateNotFoundError: If mandate doesn't exist
            InvalidStateTransitionError: If status transition is invalid
            VersionConflictError: If max retries exceeded
        """
        transaction_id = transaction_id or f"txn_{uuid4()}"

        for attempt in range(max_retries):
            try:
                # Get current state
                current = await self.mandate_repo.get_current_state(entity_id)
                if not current:
                    raise MandateNotFoundError(entity_id)

                # Validate state transition
                validate_transition(
                    mandate_type=MandateType(current.entity_type),
                    current_status=MandateStatus(current.status),
                    new_status=new_status,
                    entity_id=entity_id
                )

                # Create new ledger entry
                new_entry = await self.mandate_repo.append_ledger_entry(
                    entity_id=entity_id,
                    mandate_data=mandate_data,
                    status=new_status,
                    created_by_agent=updated_by_agent,
                    created_by_agent_type=agent_type,
                    transaction_id=transaction_id,
                    parent_version=current.current_version,
                    parent_version_hash=current.current_version_hash,
                    metadata=metadata,
                    signatures=signatures or [],
                    user_id=user_id,
                    session_id=session_id
                )

                # NOTE: No longer updating current_state - it's queried from ledger

                # Log in audit trail
                await self.audit_repo.create_audit_log(
                    event_type=EventType.MANDATE_UPDATED,
                    entity_id=entity_id,
                    entity_type=current.entity_type,
                    entity_version=new_entry.version,
                    actor_id=updated_by_agent,
                    actor_type=agent_type,
                    action=f"Updated mandate to status {new_status.value}",
                    changes={
                        "old_status": current.status,
                        "new_status": new_status.value,
                        "old_version": current.current_version,
                        "new_version": new_entry.version
                    },
                    metadata=metadata or {},
                    transaction_id=transaction_id
                )

                # Track metrics
                track_mandate_operation(
                    operation="update",
                    mandate_type=current.entity_type,
                    success=True
                )

                return new_entry

            except VersionConflictError as e:
                # Retry on version conflict
                if attempt < max_retries - 1:
                    await asyncio.sleep(0.1 * (2 ** attempt))  # Exponential backoff
                    continue
                else:
                    # Max retries exceeded
                    track_mandate_operation(
                        operation="update",
                        mandate_type=current.entity_type if current else "unknown",
                        success=False
                    )
                    raise

            except Exception as e:
                # Track other failures
                track_mandate_operation(
                    operation="update",
                    mandate_type=current.entity_type if current else "unknown",
                    success=False
                )
                raise

    # ==================== Sign Operations ====================

    async def sign_mandate(
        self,
        entity_id: str,
        signed_by_agent: str,
        agent_type: str,
        transaction_id: Optional[str] = None,
        signature_data: Optional[dict] = None
    ) -> MandateLedgerEntry:
        """
        Sign a mandate (transition to SIGNED status).

        Args:
            entity_id: Mandate identifier
            signed_by_agent: Agent signing the mandate
            agent_type: Type of agent
            transaction_id: Optional transaction ID
            signature_data: Optional signature metadata (must include 'signature' field)

        Returns:
            New ledger entry with SIGNED status and new signature
        """
        # Get current state to preserve mandate_data
        current = await self.mandate_repo.get_current_state(entity_id)
        if not current:
            raise MandateNotFoundError(entity_id)

        # Build signature entry
        now = datetime.now(timezone.utc)
        signature_entry = {
            "signature": signature_data.get("signature", "") if signature_data else "",
            "signer_id": signed_by_agent,
            "signer_type": agent_type,
            "algorithm": signature_data.get("algorithm", "EdDSA") if signature_data else "EdDSA",
            "signed_at": now.isoformat(),  # Convert to ISO string for JSON serialization
            "metadata": signature_data.get("metadata", {}) if signature_data else {}
        }

        # Append to existing signatures
        existing_signatures = getattr(current, 'signatures', [])
        # Convert Pydantic models to dicts if needed
        existing_sigs_dicts = []
        for sig in existing_signatures:
            if hasattr(sig, 'model_dump'):
                existing_sigs_dicts.append(sig.model_dump())
            elif isinstance(sig, dict):
                existing_sigs_dicts.append(sig)

        new_signatures = existing_sigs_dicts + [signature_entry]

        # Prepare metadata
        metadata = signature_data or {}
        metadata["signed_at"] = now.isoformat()

        # Convert mandate_data to dict if it's a Pydantic model
        mandate_data_dict = current.mandate_data
        if hasattr(mandate_data_dict, 'model_dump'):
            mandate_data_dict = mandate_data_dict.model_dump()

        return await self.create_mandate_version(
            entity_id=entity_id,
            mandate_data=mandate_data_dict,
            new_status=MandateStatus.SIGNED,
            updated_by_agent=signed_by_agent,
            agent_type=agent_type,
            transaction_id=transaction_id,
            metadata=metadata,
            signatures=new_signatures  # ← Pass signatures
        )

    # ==================== Cancel Operations ====================

    async def cancel_mandate(
        self,
        entity_id: str,
        cancelled_by_agent: str,
        agent_type: str,
        reason: Optional[str] = None,
        transaction_id: Optional[str] = None
    ) -> MandateLedgerEntry:
        """
        Cancel a mandate (transition to CANCELLED status).

        Args:
            entity_id: Mandate identifier
            cancelled_by_agent: Agent cancelling the mandate
            agent_type: Type of agent
            reason: Optional cancellation reason
            transaction_id: Optional transaction ID

        Returns:
            New ledger entry with CANCELLED status
        """
        transaction_id = transaction_id or f"txn_{uuid4()}"

        return await self.mandate_repo.cancel_mandate(
            entity_id=entity_id,
            cancelled_by_agent=cancelled_by_agent,
            transaction_id=transaction_id,
            reason=reason
        )

    # ==================== Query Operations ====================

    async def get_mandate(
        self,
        entity_id: str,
        version: Optional[int] = None
    ) -> MandateLedgerEntry | MandateCurrentState:
        """
        Get a mandate by ID.

        Args:
            entity_id: Mandate identifier
            version: Optional specific version (gets latest if None)

        Returns:
            Ledger entry (if version specified) or current state (if not)

        Raises:
            MandateNotFoundError: If mandate doesn't exist
        """
        if version is not None:
            # Get specific version
            entry = await self.mandate_repo.get_ledger_entry(entity_id, version)
            if not entry:
                raise MandateNotFoundError(entity_id)
            return entry
        else:
            # Get latest version
            current = await self.mandate_repo.get_current_state(entity_id)
            if not current:
                raise MandateNotFoundError(entity_id)
            return current

    async def get_mandate_history(
        self,
        entity_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> list[MandateLedgerEntry]:
        """
        Get full version history for a mandate.

        Args:
            entity_id: Mandate identifier
            limit: Maximum versions to return
            offset: Number of versions to skip

        Returns:
            List of ledger entries (newest first)
        """
        history = await self.mandate_repo.get_ledger_history(
            entity_id=entity_id,
            limit=limit,
            offset=offset
        )

        if not history:
            raise MandateNotFoundError(entity_id)

        return history

    async def get_mandates_by_transaction(
        self,
        transaction_id: str
    ) -> list[MandateLedgerEntry]:
        """
        Get all mandates for a transaction.

        Returns the latest version of each mandate (Intent, Cart, Payment)
        in chronological order.

        Args:
            transaction_id: Transaction identifier

        Returns:
            List of mandate ledger entries (latest version of each)
        """
        return await self.mandate_repo.get_mandates_by_transaction(transaction_id)


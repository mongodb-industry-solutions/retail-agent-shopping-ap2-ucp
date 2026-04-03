"""
Client for interacting with the Mandate Ledger Service.

This client provides a simple interface for agents to store and retrieve
mandates from the ledger service with full audit trail support.
"""

import httpx
import os
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class MandateLedgerClient:
    """
    Client for Mandate Ledger Service API.

    Handles authentication, request formatting, and error handling
    for all ledger operations.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        agent_id: Optional[str] = None,
        agent_type: Optional[str] = None,
        timeout: float = 30.0
    ):
        """
        Initialize the ledger client.

        Args:
            base_url: Ledger service URL (default: from MANDATE_LEDGER_SERVICE_URL env)
            api_key: API key (default: from MANDATE_LEDGER_API_KEY env)
            agent_id: Agent identifier (default: from AGENT_ID env)
            agent_type: Agent type (default: from AGENT_TYPE env)
            timeout: Request timeout in seconds

        Raises:
            ValueError: If API key is not provided
        """
        self.base_url = base_url or os.getenv("MANDATE_LEDGER_SERVICE_URL", "http://localhost:8000")
        self.api_key = api_key or os.getenv("MANDATE_LEDGER_API_KEY")
        self.agent_id = agent_id or os.getenv("AGENT_ID", "unknown")
        self.agent_type = agent_type or os.getenv("AGENT_TYPE", "unknown")
        self.timeout = timeout

        if not self.api_key:
            raise ValueError(
                "API key required. Set MANDATE_LEDGER_API_KEY environment variable "
                "or pass api_key parameter."
            )

        logger.info(
            f"MandateLedgerClient initialized: {self.agent_id} ({self.agent_type}) -> {self.base_url}"
        )

    def _get_headers(self, idempotency_key: Optional[str] = None) -> Dict[str, str]:
        """Get headers for API requests."""
        logger.debug(f"Getting headers with idempotency_key={idempotency_key}")
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        if idempotency_key:
            headers["X-Idempotency-Key"] = idempotency_key
        return headers

    async def create_mandate(
        self,
        mandate_type: str,
        mandate_data: dict,
        transaction_id: Optional[str] = None,
        idempotency_key: Optional[str] = None,
        metadata: Optional[dict] = None,
        initial_signatures: Optional[list] = None,
        initial_status: Optional[str] = None,
    ) -> dict:
        """
        Create a new mandate in the ledger.

        Args:
            mandate_type: Type of mandate (INTENT, CART, or PAYMENT)
            mandate_data: Mandate data (should be dict from .model_dump())
            transaction_id: Optional transaction identifier for grouping
            idempotency_key: Optional key to prevent duplicate creates
            metadata: Optional metadata for audit trail
            initial_signatures: Optional list of signatures (for pre-signed mandates)
            initial_status: Optional status override (e.g., 'signed' for pre-signed mandates)
            user_id: Optional user identifier for tracking
            session_id: Optional session identifier for tracking

        Returns:
            Created mandate ledger entry with entity_id and version

        Raises:
            httpx.HTTPStatusError: If request fails
        """
        logger.info(f"Creating {mandate_type} mandate (txn: {transaction_id})")
        logger.info(f"SESSION_DEBUG: metadata={metadata}")

        payload = {
            "mandate_type": mandate_type,
            "mandate_data": mandate_data,
            "transaction_id": transaction_id,
            "metadata": metadata or {}
        }

        # Add initial signatures if provided
        if initial_signatures:
            payload["initial_signatures"] = initial_signatures
            logger.info(f"Including {len(initial_signatures)} initial signature(s)")

        # Add initial status if provided
        if initial_status:
            payload["initial_status"] = initial_status
            logger.info(f"Setting initial status: {initial_status}")

        logger.info(f"MANDATE_LEDGER_DEBUG: Full create_mandate payload: {payload}")

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/api/v1/mandates",
                headers=self._get_headers(idempotency_key),
                json=payload
            )
            logger.info(f"MANDATE_LEDGER_DEBUG: create_mandate response status: {response.status_code}")
            response.raise_for_status()
            result = response.json()
            logger.info(f"MANDATE_LEDGER_DEBUG: create_mandate response: {result}")

            logger.info(
                f"Created {mandate_type} mandate: entity_id={result['entity_id']}, "
                f"version={result['version']}, status={result['status']}"
            )
            return result

    async def get_mandate(
        self,
        entity_id: str,
        version: Optional[int] = None
    ) -> dict:
        """
        Get a mandate by ID.

        Args:
            entity_id: Mandate entity ID
            version: Optional specific version (default: latest)

        Returns:
            Mandate data with metadata

        Raises:
            httpx.HTTPStatusError: If mandate not found or request fails
        """
        url = f"{self.base_url}/api/v1/mandates/{entity_id}"
        if version:
            url += f"?version={version}"

        logger.info(f"Getting mandate: {entity_id} (version: {version or 'latest'})")

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, headers=self._get_headers())
            response.raise_for_status()
            return response.json()

    async def update_mandate(
        self,
        entity_id: str,
        mandate_data: dict,
        new_status: str,
        idempotency_key: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> dict:
        """
        Update a mandate (creates new immutable version).

        Args:
            entity_id: Mandate entity ID
            mandate_data: Updated mandate data
            new_status: New status for the mandate
            idempotency_key: Optional key to prevent duplicate updates
            metadata: Optional metadata for audit trail

        Returns:
            New mandate version with updated data

        Raises:
            httpx.HTTPStatusError: If update fails (e.g., invalid transition, version conflict)
        """
        logger.info(f"Updating mandate {entity_id} to status {new_status}")

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.put(
                f"{self.base_url}/api/v1/mandates/{entity_id}",
                headers=self._get_headers(idempotency_key),
                json={
                    "mandate_data": mandate_data,
                    "new_status": new_status,
                    "metadata": metadata or {}
                }
            )
            response.raise_for_status()
            result = response.json()

            logger.info(f"Updated mandate {entity_id}: new version={result['version']}")
            return result

    async def sign_mandate(
        self,
        entity_id: str,
        transaction_id: Optional[str] = None,
        signature_data: Optional[dict] = None
    ) -> dict:
        """
        Sign a mandate (transition to SIGNED status).

        Args:
            entity_id: Mandate entity ID
            transaction_id: Optional transaction identifier
            signature_data: Optional signature metadata (e.g., JWT, timestamp)

        Returns:
            Signed mandate version

        Raises:
            httpx.HTTPStatusError: If signing fails (e.g., invalid state)
        """
        logger.info(f"Signing mandate {entity_id}")

        sign_payload = {
            "transaction_id": transaction_id,
            "signature_data": signature_data or {}
        }
        logger.info(f"MANDATE_LEDGER_DEBUG: Full sign_mandate payload: {sign_payload}")

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/api/v1/mandates/{entity_id}/sign",
                headers=self._get_headers(),
                json=sign_payload
            )
            logger.info(f"MANDATE_LEDGER_DEBUG: sign_mandate response status: {response.status_code}")
            response.raise_for_status()
            result = response.json()
            logger.info(f"MANDATE_LEDGER_DEBUG: sign_mandate response: {result}")

            logger.info(f"Signed mandate {entity_id}: version={result['version']}")
            return result

    async def get_mandate_history(self, entity_id: str) -> List[dict]:
        """
        Get full version history for a mandate.

        Args:
            entity_id: Mandate entity ID

        Returns:
            List of all mandate versions (oldest to newest)

        Raises:
            httpx.HTTPStatusError: If request fails
        """
        logger.info(f"Getting mandate history: {entity_id}")

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/api/v1/mandates/{entity_id}/history",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()

    async def search_mandates(
        self,
        filters: dict,
        limit: int = 50,
        offset: int = 0,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> dict:
        """
        Search for mandates.

        Args:
            filters: Search filters (e.g., {"mandate_type": "CART", "status": "signed"})
            limit: Maximum results to return
            offset: Pagination offset
            sort_by: Field to sort by
            sort_order: Sort order (asc or desc)

        Returns:
            Search results with items and pagination info

        Raises:
            httpx.HTTPStatusError: If request fails
        """
        logger.info(f"Searching mandates with filters: {filters}, limit: {limit}, offset: {offset}")

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/api/v1/mandates/search",
                headers=self._get_headers(),
                json={
                    "filters": filters,
                    "limit": limit,
                    "offset": offset,
                    "sort_by": sort_by,
                    "sort_order": sort_order
                }
            )
            response.raise_for_status()
            return response.json()

    async def get_audit_trail(self, entity_id: str) -> List[dict]:
        """
        Get complete audit trail for a mandate.

        Args:
            entity_id: Mandate entity ID

        Returns:
            List of all audit log entries for this mandate

        Raises:
            httpx.HTTPStatusError: If request fails
        """
        logger.info(f"Getting audit trail: {entity_id}")

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/api/v1/audit/entities/{entity_id}/trail",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()

    async def create_payment(
        self,
        transaction_id: str,
        intent_mandate_id: str,
        cart_mandate_id: str,
        payment_mandate_id: str,
        amount: float,
        currency: str,
        status: str,
        merchant_agent: str,
        payment_processor_agent: str,
        payment_method_type: Optional[str] = None,
        metadata: Optional[dict] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> dict:
        """
        Create a payment summary record in the payments collection.

        This creates an ultra-lean record linking Intent, Cart, and Payment mandates
        with their signatures for fast lookup.

        Args:
            transaction_id: Transaction/session ID
            intent_mandate_id: IntentMandate entity ID from ledger
            cart_mandate_id: CartMandate entity ID from ledger
            payment_mandate_id: PaymentMandate entity ID from ledger
            amount: Payment amount
            currency: Currency code (e.g., "USD")
            status: Payment status (SUCCESS, FAILED, PENDING)
            merchant_agent: Merchant agent ID
            payment_processor_agent: Payment processor agent ID
            payment_method_type: Payment method (e.g., "CARD")
            metadata: Optional additional metadata

        Returns:
            Payment record data

        Raises:
            httpx.HTTPStatusError: If request fails
        """
        logger.info(f"Creating payment record: {transaction_id}")

        payload = {
            "transaction_id": transaction_id,
            "intent_mandate_id": intent_mandate_id,
            "cart_mandate_id": cart_mandate_id,
            "payment_mandate_id": payment_mandate_id,
            "amount": amount,
            "currency": currency,
            "status": status,
            "merchant_agent": merchant_agent,
            "payment_processor_agent": payment_processor_agent,
        }

        if payment_method_type:
            payload["payment_method_type"] = payment_method_type
        
        # Build metadata with user_id and session_id
        if metadata or user_id or session_id:
            final_metadata = metadata or {}
            if user_id:
                final_metadata["user_id"] = user_id
            if session_id:
                final_metadata["session_id"] = session_id
            payload["metadata"] = final_metadata

        logger.info(f"MANDATE_LEDGER_DEBUG: Full create_payment payload: {payload}")

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/api/v1/payments",
                json=payload,
                headers=self._get_headers()
            )
            logger.info(f"MANDATE_LEDGER_DEBUG: create_payment response status: {response.status_code}")
            response.raise_for_status()
            result = response.json()
            logger.info(f"MANDATE_LEDGER_DEBUG: create_payment response: {result}")
            return result

    async def health_check(self) -> dict:
        """
        Check if the ledger service is healthy.

        Returns:
            Health status information

        Raises:
            httpx.HTTPStatusError: If service is unhealthy
        """
        logger.info(f"Health check for mandate ledger service at {self.base_url}")
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{self.base_url}/api/v1/health")
            response.raise_for_status()
            return response.json()


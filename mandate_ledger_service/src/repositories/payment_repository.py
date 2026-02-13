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
Payment Repository
Database operations for payment records
"""

from typing import Optional, List
from datetime import datetime

from src.repositories.base_repository import BaseRepository
from src.db.mongodb import MongoDB
from src.models.payment import PaymentRecord


class PaymentRepository:
    """Repository for payment record operations"""

    def __init__(self):
        """Initialize the payment repository"""
        self.repo = BaseRepository(MongoDB.payments)

    async def create_payment(self, payment_data: dict) -> PaymentRecord:
        """
        Create a new payment record.

        Args:
            payment_data: Payment data dictionary

        Returns:
            Created payment record
        """
        await self.repo.insert_one(payment_data)
        return PaymentRecord(**payment_data)

    async def get_by_payment_id(self, payment_id: str) -> Optional[PaymentRecord]:
        """
        Get payment by payment_id.

        Args:
            payment_id: Payment identifier

        Returns:
            Payment record or None
        """
        doc = await self.repo.find_one({"payment_id": payment_id})
        if doc:
            doc.pop("_id", None)
            return PaymentRecord(**doc)
        return None

    async def get_by_transaction_id(self, transaction_id: str) -> List[PaymentRecord]:
        """
        Get all payments for a transaction (session).

        Useful when a user retries payment - multiple payment_ids for same transaction_id.

        Args:
            transaction_id: Transaction/session identifier

        Returns:
            List of payment records
        """
        docs = await self.repo.find_many({"transaction_id": transaction_id})
        return [PaymentRecord(**{**doc, "_id": None} if "_id" in doc else doc) for doc in docs]

    async def search_payments(
        self,
        status: Optional[str] = None,
        merchant_agent: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[PaymentRecord], int]:
        """
        Search payments with filters.

        Args:
            status: Filter by payment status
            merchant_agent: Filter by merchant agent
            start_date: Filter by start date
            end_date: Filter by end date
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Tuple of (payment records, total count)
        """
        query = {}

        if status:
            query["status"] = status
        if merchant_agent:
            query["merchant_agent"] = merchant_agent
        if start_date or end_date:
            query["processed_at"] = {}
            if start_date:
                query["processed_at"]["$gte"] = start_date
            if end_date:
                query["processed_at"]["$lte"] = end_date

        docs = await self.repo.find_many(query, skip=skip, limit=limit)
        total = await self.repo.count_documents(query)

        payments = []
        for doc in docs:
            doc.pop("_id", None)
            payments.append(PaymentRecord(**doc))

        return payments, total


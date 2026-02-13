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
Base repository class.

Provides common database operations that can be inherited by specific repositories.
"""

from typing import Optional, Any, TypeVar, Generic
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.errors import PyMongoError

from src.core.errors import DatabaseError, DatabaseOperationError
from src.core.monitoring import track_db_operation
import time

T = TypeVar('T')


class BaseRepository(Generic[T]):
    """
    Base repository with common database operations.

    This class provides reusable database methods that can be inherited
    by specific repository implementations.
    """

    def __init__(self, collection: AsyncIOMotorCollection):
        """
        Initialize the repository.

        Args:
            collection: MongoDB collection to operate on
        """
        self.collection = collection
        self.collection_name = collection.name

    async def _execute_with_tracking(
        self,
        operation: str,
        func,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute a database operation with metric tracking.

        Args:
            operation: Operation name (insert, find, update, delete)
            func: Async function to execute
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func

        Returns:
            Result of the operation

        Raises:
            DatabaseOperationError: If operation fails
        """
        start_time = time.time()
        success = False

        try:
            result = await func(*args, **kwargs)
            success = True
            return result

        except PyMongoError as e:
            raise DatabaseOperationError(
                operation=f"{operation} on {self.collection_name}",
                reason=str(e)
            )

        finally:
            duration = time.time() - start_time
            track_db_operation(
                collection=self.collection_name,
                operation=operation,
                success=success,
                duration=duration
            )

    async def find_one(
        self,
        filter_dict: dict,
        projection: Optional[dict] = None
    ) -> Optional[dict]:
        """
        Find a single document.

        Args:
            filter_dict: Query filter
            projection: Fields to include/exclude

        Returns:
            Document dict or None if not found
        """
        return await self._execute_with_tracking(
            "find_one",
            self.collection.find_one,
            filter_dict,
            projection
        )

    async def find_many(
        self,
        filter_dict: dict,
        projection: Optional[dict] = None,
        sort: Optional[list] = None,
        limit: Optional[int] = None,
        skip: Optional[int] = None
    ) -> list[dict]:
        """
        Find multiple documents.

        Args:
            filter_dict: Query filter
            projection: Fields to include/exclude
            sort: Sort specification [(field, direction), ...]
            limit: Maximum number of documents
            skip: Number of documents to skip

        Returns:
            List of document dicts
        """
        async def _find():
            cursor = self.collection.find(filter_dict, projection)

            if sort:
                cursor = cursor.sort(sort)
            if skip:
                cursor = cursor.skip(skip)
            if limit:
                cursor = cursor.limit(limit)

            return await cursor.to_list(length=limit)

        return await self._execute_with_tracking("find", _find)

    async def count_documents(self, filter_dict: dict) -> int:
        """
        Count documents matching filter.

        Args:
            filter_dict: Query filter

        Returns:
            Count of matching documents
        """
        return await self._execute_with_tracking(
            "count",
            self.collection.count_documents,
            filter_dict
        )

    async def insert_one(self, document: dict) -> str:
        """
        Insert a single document.

        Args:
            document: Document to insert

        Returns:
            Inserted document ID (as string)
        """
        result = await self._execute_with_tracking(
            "insert",
            self.collection.insert_one,
            document
        )
        return str(result.inserted_id)

    async def insert_many(self, documents: list[dict]) -> list[str]:
        """
        Insert multiple documents.

        Args:
            documents: List of documents to insert

        Returns:
            List of inserted document IDs (as strings)
        """
        result = await self._execute_with_tracking(
            "insert",
            self.collection.insert_many,
            documents
        )
        return [str(id) for id in result.inserted_ids]

    async def update_one(
        self,
        filter_dict: dict,
        update: dict,
        upsert: bool = False
    ) -> int:
        """
        Update a single document.

        Args:
            filter_dict: Query filter
            update: Update operations
            upsert: Create if not exists

        Returns:
            Number of documents modified
        """
        result = await self._execute_with_tracking(
            "update",
            self.collection.update_one,
            filter_dict,
            update,
            upsert=upsert
        )
        return result.modified_count

    async def update_many(
        self,
        filter_dict: dict,
        update: dict
    ) -> int:
        """
        Update multiple documents.

        Args:
            filter_dict: Query filter
            update: Update operations

        Returns:
            Number of documents modified
        """
        result = await self._execute_with_tracking(
            "update",
            self.collection.update_many,
            filter_dict,
            update
        )
        return result.modified_count

    async def delete_one(self, filter_dict: dict) -> int:
        """
        Delete a single document.

        Args:
            filter_dict: Query filter

        Returns:
            Number of documents deleted
        """
        result = await self._execute_with_tracking(
            "delete",
            self.collection.delete_one,
            filter_dict
        )
        return result.deleted_count

    async def delete_many(self, filter_dict: dict) -> int:
        """
        Delete multiple documents.

        Args:
            filter_dict: Query filter

        Returns:
            Number of documents deleted
        """
        result = await self._execute_with_tracking(
            "delete",
            self.collection.delete_many,
            filter_dict
        )
        return result.deleted_count

    async def aggregate(self, pipeline: list[dict]) -> list[dict]:
        """
        Execute an aggregation pipeline.

        Args:
            pipeline: Aggregation pipeline stages

        Returns:
            List of result documents
        """
        async def _aggregate():
            cursor = self.collection.aggregate(pipeline)
            return await cursor.to_list(length=None)

        return await self._execute_with_tracking("aggregate", _aggregate)





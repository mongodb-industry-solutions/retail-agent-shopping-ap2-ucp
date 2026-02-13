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
MongoDB Change Stream Manager

Handles background listeners for real-time data processing.
Watches for database changes and triggers corresponding actions.
"""

from motor.motor_asyncio import AsyncIOMotorCollection
from typing import Callable, List, Dict, Any
import asyncio
import logging

logger = logging.getLogger(__name__)


class ChangeStreamListener:
    """Single change stream listener configuration"""

    def __init__(
        self,
        collection: AsyncIOMotorCollection,
        pipeline: List[Dict[str, Any]],
        handler: Callable,
        name: str
    ):
        self.collection = collection
        self.pipeline = pipeline
        self.handler = handler
        self.name = name
        self.task = None


class ChangeStreamManager:
    """Manages all MongoDB change stream listeners"""

    def __init__(self):
        self.listeners: List[ChangeStreamListener] = []
        self.running = False

    def register_listener(
        self,
        collection: AsyncIOMotorCollection,
        pipeline: List[Dict[str, Any]],
        handler: Callable,
        name: str
    ):
        """
        Register a change stream listener.

        Args:
            collection: MongoDB collection to watch
            pipeline: Aggregation pipeline to filter events
            handler: Async function to handle events
            name: Descriptive name for this listener
        """
        listener = ChangeStreamListener(collection, pipeline, handler, name)
        self.listeners.append(listener)
        logger.info(f"Registered change stream listener: {name}")

    async def start_all(self):
        """Start all registered listeners"""
        if self.running:
            logger.warning("Change streams already running")
            return

        self.running = True
        logger.info(f"Starting {len(self.listeners)} change stream listeners...")

        for listener in self.listeners:
            listener.task = asyncio.create_task(
                self._run_listener(listener),
                name=f"change_stream_{listener.name}"
            )

        logger.info("✅ All change stream listeners started")

    async def _run_listener(self, listener: ChangeStreamListener):
        """
        Run a single change stream listener with reconnection logic.

        Args:
            listener: Listener configuration
        """
        while self.running:
            try:
                async with listener.collection.watch(
                    listener.pipeline,
                    full_document="updateLookup"
                ) as stream:
                    logger.info(f"✅ Change stream '{listener.name}' started")

                    async for change in stream:
                        try:
                            await listener.handler(change)
                        except Exception as e:
                            logger.error(
                                f"Error in change stream handler '{listener.name}': {e}",
                                exc_info=True
                            )
                            # Continue processing other changes

            except Exception as e:
                logger.error(
                    f"Change stream '{listener.name}' connection error: {e}",
                    exc_info=True
                )
                if self.running:
                    logger.info(f"Reconnecting '{listener.name}' in 5 seconds...")
                    await asyncio.sleep(5)

    async def stop_all(self):
        """Stop all listeners"""
        logger.info("Stopping all change stream listeners...")
        self.running = False

        for listener in self.listeners:
            if listener.task and not listener.task.done():
                listener.task.cancel()
                try:
                    await listener.task
                except asyncio.CancelledError:
                    pass

        logger.info("✅ All change stream listeners stopped")


# Global singleton instance
change_stream_manager = ChangeStreamManager()



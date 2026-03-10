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

"""GenAI Client Manager for proper lifecycle management.

This module provides a singleton client manager to prevent the creation
of multiple GenAI clients and avoid cleanup issues.
"""

import logging
from typing import Optional
from google import genai

logger = logging.getLogger(__name__)


class GenAIClientManager:
    """Singleton manager for GenAI clients to prevent lifecycle issues."""
    
    _instance: Optional['GenAIClientManager'] = None
    _client: Optional[genai.Client] = None
    
    def __new__(cls) -> 'GenAIClientManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_client(self) -> genai.Client:
        """Get or create the shared GenAI client instance."""
        if self._client is None:
            logger.info("Creating shared GenAI client instance")
            self._client = genai.Client()
        return self._client
    
    async def cleanup(self) -> None:
        """Properly cleanup the GenAI client if it exists."""
        if self._client is not None:
            try:
                logger.info("Cleaning up GenAI client")
                # Check if the client has the aclose method and the required attributes
                if hasattr(self._client, 'aclose'):
                    # Only attempt to close if the client has the expected attributes
                    if hasattr(self._client, '_async_httpx_client'):
                        await self._client.aclose()
                    else:
                        logger.warning("GenAI client missing _async_httpx_client attribute, skipping aclose()")
                self._client = None
                logger.info("GenAI client cleaned up successfully")
            except Exception as e:
                logger.error(f"Error during GenAI client cleanup: {e}")
                # Set to None anyway to prevent further issues
                self._client = None


# Global instance for easy access
_client_manager = GenAIClientManager()


def get_genai_client() -> genai.Client:
    """Get the shared GenAI client instance."""
    return _client_manager.get_client()


async def cleanup_genai_client() -> None:
    """Cleanup the shared GenAI client."""
    await _client_manager.cleanup()
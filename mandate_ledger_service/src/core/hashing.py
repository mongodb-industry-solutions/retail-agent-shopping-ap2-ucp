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
Hashing utilities for the Mandate Ledger Service.

Provides SHA-256 for mandate version hashing and bcrypt for API key hashing.
"""

import hashlib
import json
from typing import Any, Union
import bcrypt

from pydantic import BaseModel


def compute_sha256(data: Union[str, dict, BaseModel]) -> str:
    """
    Compute SHA-256 hash of data.

    Used for:
    - Parent version hashing (chain integrity)
    - Current version hashing (verification)

    Args:
        data: String, dict, or Pydantic model to hash

    Returns:
        Hex string of SHA-256 hash

    Example:
        >>> compute_sha256({"entity_id": "mandate_123", "version": 1})
        'a3c4e5...'
    """
    # Convert to canonical JSON string
    if isinstance(data, BaseModel):
        json_str = data.model_dump_json(exclude_none=False, sort_keys=True)
    elif isinstance(data, dict):
        json_str = json.dumps(data, sort_keys=True, ensure_ascii=True)
    elif isinstance(data, str):
        json_str = data
    else:
        raise TypeError(f"Unsupported data type for hashing: {type(data)}")

    # Compute SHA-256
    hash_obj = hashlib.sha256(json_str.encode('utf-8'))
    return hash_obj.hexdigest()


def compute_mandate_hash(mandate_entry: dict) -> str:
    """
    Compute hash for a mandate ledger entry.

    This is a specialized version of compute_sha256 that excludes
    the hash fields themselves to avoid circular dependencies.

    Args:
        mandate_entry: Mandate ledger entry dict

    Returns:
        SHA-256 hash hex string

    Example:
        >>> entry = {
        ...     "entity_id": "mandate_123",
        ...     "version": 1,
        ...     "mandate_data": {...},
        ...     "parent_version_hash": "abc...",  # Excluded from hash
        ...     "current_version_hash": "def..."  # Excluded from hash
        ... }
        >>> compute_mandate_hash(entry)
        'e7f8a9...'
    """
    # Create a copy and exclude hash fields
    hashable_entry = {
        k: v for k, v in mandate_entry.items()
        if k not in ['parent_version_hash', 'current_version_hash', '_id']
    }

    return compute_sha256(hashable_entry)


def hash_api_key(api_key: str) -> str:
    """
    Hash an API key using bcrypt.

    Args:
        api_key: Plaintext API key

    Returns:
        Bcrypt hash string

    Example:
        >>> hash_api_key("mlsk_1234567890abcdef")
        '$2b$12$...'
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(api_key.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_api_key(api_key: str, hashed_key: str) -> bool:
    """
    Verify an API key against its hash.

    Args:
        api_key: Plaintext API key to verify
        hashed_key: Bcrypt hash to check against

    Returns:
        True if the key matches, False otherwise

    Example:
        >>> hashed = hash_api_key("mlsk_1234567890abcdef")
        >>> verify_api_key("mlsk_1234567890abcdef", hashed)
        True
        >>> verify_api_key("wrong_key", hashed)
        False
    """
    try:
        return bcrypt.checkpw(
            api_key.encode('utf-8'),
            hashed_key.encode('utf-8')
        )
    except Exception:
        return False


def generate_api_key_prefix(api_key: str, length: int = 8) -> str:
    """
    Extract the first N characters of an API key for identification.

    This prefix is stored unhashed for user-friendly key identification.

    Args:
        api_key: Full API key
        length: Number of characters to include in prefix

    Returns:
        First N characters of the key

    Example:
        >>> generate_api_key_prefix("mlsk_1234567890abcdef", 8)
        'mlsk_123'
    """
    return api_key[:length]


def verify_chain_integrity(
    parent_entry: dict,
    child_entry: dict
) -> bool:
    """
    Verify the chain integrity between two mandate versions.

    Checks that:
    1. Child's parent_version matches parent's version
    2. Child's parent_version_hash matches parent's current_version_hash

    Args:
        parent_entry: Parent mandate ledger entry
        child_entry: Child mandate ledger entry

    Returns:
        True if chain is valid, False otherwise

    Example:
        >>> parent = {
        ...     "entity_id": "mandate_123",
        ...     "version": 1,
        ...     "current_version_hash": "abc123..."
        ... }
        >>> child = {
        ...     "entity_id": "mandate_123",
        ...     "version": 2,
        ...     "parent_version": 1,
        ...     "parent_version_hash": "abc123..."
        ... }
        >>> verify_chain_integrity(parent, child)
        True
    """
    # Check version continuity
    if child_entry.get("parent_version") != parent_entry.get("version"):
        return False

    # Check hash linkage
    if child_entry.get("parent_version_hash") != parent_entry.get("current_version_hash"):
        return False

    return True


def compute_ledger_entry_hash(
    entity_id: str,
    version: int,
    mandate_data: Any,
    status: str,
    created_at: str,
    created_by_agent: str,
    transaction_id: str
) -> str:
    """
    Compute hash for core mandate ledger fields.

    This creates a reproducible hash for version integrity checking.

    Args:
        entity_id: Mandate entity ID
        version: Version number
        mandate_data: The AP2 mandate data
        status: Mandate status
        created_at: Creation timestamp (ISO format)
        created_by_agent: Agent that created this version
        transaction_id: Transaction ID

    Returns:
        SHA-256 hash hex string
    """
    # Build canonical representation
    hashable_data = {
        "entity_id": entity_id,
        "version": version,
        "mandate_data": mandate_data if isinstance(mandate_data, dict)
                       else mandate_data.model_dump() if isinstance(mandate_data, BaseModel)
                       else str(mandate_data),
        "status": status,
        "created_at": created_at,
        "created_by_agent": created_by_agent,
        "transaction_id": transaction_id
    }

    return compute_sha256(hashable_data)





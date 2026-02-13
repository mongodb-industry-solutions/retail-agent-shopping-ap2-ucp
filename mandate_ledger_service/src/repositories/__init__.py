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
Repository layer for database operations.

Implements the Repository pattern to abstract MongoDB operations
from business logic.
"""

from src.repositories.mandate_repository import MandateRepository
from src.repositories.audit_repository import AuditRepository
from src.repositories.auth_repository import AuthRepository
from src.repositories.idempotency_repository import IdempotencyRepository
from src.repositories.rate_limit_repository import RateLimitRepository
from src.repositories.consistency_repository import ConsistencyRepository

__all__ = [
    "MandateRepository",
    "AuditRepository",
    "AuthRepository",
    "IdempotencyRepository",
    "RateLimitRepository",
    "ConsistencyRepository",
]


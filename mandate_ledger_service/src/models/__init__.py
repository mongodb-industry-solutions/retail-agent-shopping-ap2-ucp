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
Pydantic models for the Mandate Ledger Service.

All data models, enums, and validation logic.
"""

# Enums
from src.models.enums import (
    MandateType,
    MandateStatus,
    EventType,
    ConsistencyIssueType,
    ApiKeyStatus,
)

# Mandate models
from src.models.mandate import (
    MandateLedgerEntry,
    MandateCurrentState,
    MandateCreateRequest,
    MandateUpdateRequest,
    MandateSignRequest,
    MandateResponse,
    MandateHistoryResponse,
    MandateSearchRequest,
)

# Audit models
from src.models.audit import (
    AuditLogEntry,
    AuditLogSearchRequest,
    AuditLogResponse,
    EntityAuditTrailResponse,
)

# Auth models
from src.models.auth import (
    ApiKey,
    ApiKeyCreateRequest,
    ApiKeyCreateResponse,
    ApiKeyListResponse,
    AuthenticatedAgent,
)

# Admin models
from src.models.admin import (
    ConsistencyCheckResult,
    ConsistencyIssue,
    ConsistencyRepairRequest,
    ConsistencyRepairResponse,
    HealthCheckResponse,
    StorageStatsResponse,
    IdempotencyRecord,
    RateLimitRecord,
)

# Common models (Day 4)
from src.models.common import (
    PaginationParams,
    PaginatedResponse,
    ErrorDetail,
    ErrorResponse,
    ErrorInfo,
    SuccessResponse,
    HealthStatus,
    SortOrder,
)

__all__ = [
    # Enums
    "MandateType",
    "MandateStatus",
    "EventType",
    "ConsistencyIssueType",
    "ApiKeyStatus",
    # Mandate models
    "MandateLedgerEntry",
    "MandateCurrentState",
    "MandateCreateRequest",
    "MandateUpdateRequest",
    "MandateSignRequest",
    "MandateResponse",
    "MandateHistoryResponse",
    "MandateSearchRequest",
    # Audit models
    "AuditLogEntry",
    "AuditLogSearchRequest",
    "AuditLogResponse",
    "EntityAuditTrailResponse",
    # Auth models
    "ApiKey",
    "ApiKeyCreateRequest",
    "ApiKeyCreateResponse",
    "ApiKeyListResponse",
    "AuthenticatedAgent",
    # Admin models
    "ConsistencyCheckResult",
    "ConsistencyIssue",
    "ConsistencyRepairRequest",
    "ConsistencyRepairResponse",
    "HealthCheckResponse",
    "StorageStatsResponse",
    "IdempotencyRecord",
    "RateLimitRecord",
    # Common models
    "PaginationParams",
    "PaginatedResponse",
    "ErrorDetail",
    "ErrorResponse",
    "ErrorInfo",
    "SuccessResponse",
    "HealthStatus",
    "SortOrder",
]


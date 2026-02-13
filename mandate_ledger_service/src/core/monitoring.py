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
Monitoring and metrics utilities.

Provides Prometheus metrics for observability.
"""

from prometheus_client import Counter, Histogram, Gauge, Info
from typing import Optional
import time
from functools import wraps


# ==================== Request Metrics ====================

request_count = Counter(
    'mandate_ledger_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

request_duration = Histogram(
    'mandate_ledger_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

# ==================== Mandate Metrics ====================

mandates_total = Gauge(
    'mandate_ledger_mandates_total',
    'Total number of mandates',
    ['mandate_type', 'status']
)

mandate_operations = Counter(
    'mandate_ledger_operations_total',
    'Total mandate operations',
    ['operation', 'mandate_type', 'success']
)

mandate_versions = Histogram(
    'mandate_ledger_versions',
    'Number of versions per mandate',
    buckets=(1, 2, 3, 5, 10, 20, 50)
)

# ==================== Database Metrics ====================

db_operations = Counter(
    'mandate_ledger_db_operations_total',
    'Total database operations',
    ['collection', 'operation', 'success']
)

db_operation_duration = Histogram(
    'mandate_ledger_db_operation_duration_seconds',
    'Database operation duration',
    ['collection', 'operation']
)

db_connection_pool = Gauge(
    'mandate_ledger_db_connection_pool_size',
    'Current database connection pool size'
)

# ==================== Auth Metrics ====================

auth_attempts = Counter(
    'mandate_ledger_auth_attempts_total',
    'Total authentication attempts',
    ['result']  # success, invalid_key, expired, revoked
)

api_keys_active = Gauge(
    'mandate_ledger_api_keys_active',
    'Number of active API keys'
)

# ==================== Error Metrics ====================

errors_total = Counter(
    'mandate_ledger_errors_total',
    'Total errors',
    ['error_type', 'operation']
)

# ==================== Service Info ====================

service_info = Info(
    'mandate_ledger_service',
    'Service information'
)

service_uptime = Gauge(
    'mandate_ledger_uptime_seconds',
    'Service uptime in seconds'
)

# ==================== Helper Functions ====================

def track_request(method: str, endpoint: str, status_code: int):
    """
    Track an HTTP request.

    Args:
        method: HTTP method (GET, POST, etc.)
        endpoint: API endpoint path
        status_code: HTTP status code
    """
    request_count.labels(
        method=method,
        endpoint=endpoint,
        status_code=status_code
    ).inc()


def track_mandate_operation(
    operation: str,
    mandate_type: str,
    success: bool
):
    """
    Track a mandate operation.

    Args:
        operation: Operation type (create, update, sign, etc.)
        mandate_type: Mandate type (IntentMandate, CartMandate, etc.)
        success: Whether operation succeeded
    """
    mandate_operations.labels(
        operation=operation,
        mandate_type=mandate_type,
        success=str(success).lower()
    ).inc()


def track_db_operation(
    collection: str,
    operation: str,
    success: bool,
    duration: Optional[float] = None
):
    """
    Track a database operation.

    Args:
        collection: MongoDB collection name
        operation: Operation type (insert, find, update, delete)
        success: Whether operation succeeded
        duration: Operation duration in seconds
    """
    db_operations.labels(
        collection=collection,
        operation=operation,
        success=str(success).lower()
    ).inc()

    if duration is not None:
        db_operation_duration.labels(
            collection=collection,
            operation=operation
        ).observe(duration)


def track_auth_attempt(result: str):
    """
    Track an authentication attempt.

    Args:
        result: Result of attempt (success, invalid_key, expired, revoked)
    """
    auth_attempts.labels(result=result).inc()


def track_error(error_type: str, operation: str):
    """
    Track an error occurrence.

    Args:
        error_type: Type of error (e.g., 'VersionConflictError')
        operation: Operation that failed
    """
    errors_total.labels(
        error_type=error_type,
        operation=operation
    ).inc()


def timer(operation: str, collection: Optional[str] = None):
    """
    Decorator to time operations and track metrics.

    Args:
        operation: Name of the operation
        collection: Optional collection name for DB operations

    Example:
        >>> @timer(operation="create_mandate", collection="mandate_ledger")
        ... async def create_mandate(data):
        ...     # ... implementation ...
        ...     pass
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            success = False
            try:
                result = await func(*args, **kwargs)
                success = True
                return result
            finally:
                duration = time.time() - start_time
                if collection:
                    track_db_operation(collection, operation, success, duration)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            success = False
            try:
                result = func(*args, **kwargs)
                success = True
                return result
            finally:
                duration = time.time() - start_time
                if collection:
                    track_db_operation(collection, operation, success, duration)

        # Return appropriate wrapper based on function type
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def update_service_info(
    version: str,
    environment: str,
    database: str
):
    """
    Update service information metrics.

    Args:
        version: Service version
        environment: Environment (development, staging, production)
        database: Database name
    """
    service_info.info({
        'version': version,
        'environment': environment,
        'database': database
    })


def update_uptime(uptime_seconds: float):
    """
    Update service uptime metric.

    Args:
        uptime_seconds: Service uptime in seconds
    """
    service_uptime.set(uptime_seconds)





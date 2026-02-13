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
FastAPI dependencies for authentication, rate limiting, and idempotency.
"""

from typing import Optional, Annotated
from fastapi import Header, HTTPException, Request, status, Depends

from src.services.auth_service import AuthService
from src.repositories import IdempotencyRepository, RateLimitRepository
from src.models.auth import AuthenticatedAgent
from src.models.admin import IdempotencyRecord
from src.core.errors import (
    InvalidApiKeyError,
    ApiKeyExpiredError,
    ApiKeyRevokedError,
    RateLimitExceededError
)
from src.config import settings


async def get_authenticated_agent(
    authorization: Optional[str] = Header(None),
    x_api_key: Optional[str] = Header(None)
) -> AuthenticatedAgent:
    """
    Dependency to authenticate an agent via API key.

    Supports three authentication methods:
    1. Bearer token in Authorization header
    2. API key in X-API-Key header
    3. Bootstrap admin key (if enabled, for initial setup)

    Args:
        authorization: Authorization header value (e.g., "Bearer xxx")
        x_api_key: API key from X-API-Key header

    Returns:
        AuthenticatedAgent with agent info and permissions

    Raises:
        HTTPException: 401 if authentication fails
    """
    # Extract API key from either source
    api_key = None

    # Parse Authorization header (format: "Bearer xxx")
    if authorization and authorization.startswith("Bearer "):
        api_key = authorization[7:]  # Remove "Bearer " prefix
    elif x_api_key:
        api_key = x_api_key
    print(f"🔍 DEBUG Bootstrap Check:")
    print(f"  ENABLE_BOOTSTRAP_AUTH = {settings.ENABLE_BOOTSTRAP_AUTH} (type: {type(settings.ENABLE_BOOTSTRAP_AUTH)})")
    print(f"  BOOTSTRAP_ADMIN_KEY = {settings.BOOTSTRAP_ADMIN_KEY[:20] if settings.BOOTSTRAP_ADMIN_KEY else 'EMPTY'}...")
    print(f"  Received api_key = {api_key[:20] if api_key else 'NONE'}...")
    print(f"  Keys match? {api_key == settings.BOOTSTRAP_ADMIN_KEY}")

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Provide API key via Authorization header or X-API-Key header.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Check for bootstrap key first (if enabled)
    # This solves the chicken-egg problem: need API key to create API keys
    if settings.ENABLE_BOOTSTRAP_AUTH and api_key == settings.BOOTSTRAP_ADMIN_KEY:
        print("✅ Bootstrap authentication GRANTED")
        # Bootstrap mode: Grant temporary admin access
        # This bypasses database lookup for initial setup
        return AuthenticatedAgent(
            agent_id="bootstrap-admin",
            agent_type="admin",
            agent_name="Bootstrap Admin",
            key_id="bootstrap",
            permissions=["admin", "mandate:read", "mandate:write", "audit:read", "auth:manage"],
            rate_limit_per_minute=settings.DEFAULT_RATE_LIMIT_PER_MINUTE
        )
    else:
        print("Bootstrap authentication REJECTED")
    # Normal authentication (database lookup)
    auth_service = AuthService()

    try:
        authenticated_agent = await auth_service.authenticate(api_key)
        return authenticated_agent
    except InvalidApiKeyError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid API key: {e.message}",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except ApiKeyExpiredError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"API key expired: {e.message}",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except ApiKeyRevokedError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"API key revoked: {e.message}",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication error: {str(e)}"
        )


async def check_rate_limit(
    agent: AuthenticatedAgent = Depends(get_authenticated_agent),
    request: Request = None
) -> None:
    """
    Dependency to check rate limits for an agent.

    Args:
        agent: Authenticated agent (from get_authenticated_agent)
        request: FastAPI request object

    Raises:
        HTTPException: 429 if rate limit exceeded
    """
    rate_limit_repo = RateLimitRepository()

    try:
        current_count, window_start = await rate_limit_repo.check_and_increment(
            agent_id=agent.agent_id,
            limit_per_minute=settings.DEFAULT_RATE_LIMIT_PER_MINUTE,
            window_seconds=60
        )

        # Add rate limit info to request state for response headers
        request.state.rate_limit_count = current_count
        request.state.rate_limit_limit = settings.DEFAULT_RATE_LIMIT_PER_MINUTE
        request.state.rate_limit_remaining = settings.DEFAULT_RATE_LIMIT_PER_MINUTE - current_count

    except RateLimitExceededError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded: {e.message}",
            headers={
                "X-RateLimit-Limit": str(e.limit),
                "X-RateLimit-Reset": e.reset_at,
                "Retry-After": "60"
            }
        )
    except Exception as e:
        # Don't fail the request on rate limit errors, just log
        # This prevents rate limit DB issues from breaking the API
        import logging
        logging.error(f"Rate limit check failed: {e}")


async def check_idempotency(
    agent: Annotated[AuthenticatedAgent, "get_authenticated_agent"],
    request: Request,
    x_idempotency_key: Optional[str] = Header(None)
) -> Optional[IdempotencyRecord]:
    """
    Dependency to check idempotency for write operations.

    If an idempotency key is provided and a matching record exists,
    returns the cached record. Otherwise returns None.

    Args:
        agent: Authenticated agent (from get_authenticated_agent)
        request: FastAPI request object
        x_idempotency_key: Idempotency key from X-Idempotency-Key header

    Returns:
        IdempotencyRecord if duplicate request, None otherwise
    """
    if not x_idempotency_key:
        return None

    idempotency_repo = IdempotencyRepository()

    try:
        existing = await idempotency_repo.check_idempotency_key(
            idempotency_key=x_idempotency_key,
            agent_id=agent.agent_id
        )

        if existing:
            # Store in request state for endpoint to use
            request.state.idempotency_record = existing
            return existing

        # Store idempotency key in request state for endpoint to save result
        request.state.idempotency_key = x_idempotency_key
        return None

    except Exception as e:
        # Don't fail the request on idempotency check errors
        import logging
        logging.error(f"Idempotency check failed: {e}")
        return None


async def require_scope(
    agent: Annotated[AuthenticatedAgent, "get_authenticated_agent"],
    required_scopes: list[str]
) -> None:
    """
    Dependency to require specific scopes for an endpoint.

    Args:
        agent: Authenticated agent
        required_scopes: List of required scopes

    Raises:
        HTTPException: 403 if agent lacks required scopes
    """
    missing_scopes = [scope for scope in required_scopes if scope not in agent.permissions]

    if missing_scopes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Insufficient permissions. Missing scopes: {', '.join(missing_scopes)}"
        )


# Common dependencies for write endpoints
WriteEndpointDeps = Annotated[
    tuple[AuthenticatedAgent, Optional[IdempotencyRecord]],
    "get_authenticated_agent + check_rate_limit + check_idempotency"
]

# Common dependencies for read endpoints
ReadEndpointDeps = Annotated[
    AuthenticatedAgent,
    "get_authenticated_agent + check_rate_limit"
]




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
FastAPI application entry point.

Main application setup, lifecycle hooks, and middleware configuration.
"""

import logging
import time
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

from src.config import settings
from src.db.mongodb import connect_to_mongo, close_mongo_connection
from src.db.indexes import create_all_indexes
from src.core.errors import MandateLedgerError
from src.core.monitoring import (
    update_service_info,
    update_uptime,
    track_request,
    track_error
)
from src.core.change_streams import change_stream_manager
from src.listeners.payment_listener import register_payment_listeners

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Track service start time
SERVICE_START_TIME = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Handles startup and shutdown tasks:
    - Connect to MongoDB
    - Create indexes
    - Initialize metrics
    - Cleanup on shutdown
    """
    # Startup
    logger.info(f"Starting {settings.SERVICE_NAME}...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Database: {settings.MONGODB_DATABASE}")

    try:
        # Connect to MongoDB
        await connect_to_mongo()

        # Create indexes
        await create_all_indexes()

        # Register change stream listeners
        # register_payment_listeners()  # Temporarily disabled - requires MongoDB replica set

        # Start change streams in background
        # asyncio.create_task(change_stream_manager.start_all())  # Temporarily disabled
        # logger.info("Change stream listeners starting in background")

        # Initialize service metrics
        update_service_info(
            version="0.1.0",  # TODO: Get from package metadata
            environment=settings.ENVIRONMENT,
            database=settings.MONGODB_DATABASE
        )

        logger.info(f"{settings.SERVICE_NAME} started successfully")

    except Exception as e:
        logger.error(f"Failed to start service: {e}")
        raise

    yield

    # Shutdown
    logger.info(f"Shutting down {settings.SERVICE_NAME}...")

    # Stop change streams
    # await change_stream_manager.stop_all()  # Temporarily disabled

    # Close MongoDB connection
    await close_mongo_connection()
    logger.info("Shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Mandate Ledger Service",
    description="Immutable ledger for Agent Payments Protocol (AP2) mandates",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)


# ==================== Middleware ====================

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """
    Middleware to track request metrics.

    Records request count, duration, and updates uptime.
    """
    start_time = time.time()

    # Update uptime
    uptime = time.time() - SERVICE_START_TIME
    update_uptime(uptime)

    # Process request
    try:
        response = await call_next(request)

        # Track metrics
        duration = time.time() - start_time
        track_request(
            method=request.method,
            endpoint=request.url.path,
            status_code=response.status_code
        )

        # Add custom headers
        response.headers["X-Request-Duration"] = f"{duration:.3f}"
        response.headers["X-Service-Version"] = "0.1.0"

        return response

    except Exception as e:
        # Track error
        track_error(
            error_type=type(e).__name__,
            operation=f"{request.method} {request.url.path}"
        )
        raise


# ==================== Error Handlers ====================

@app.exception_handler(MandateLedgerError)
async def mandate_ledger_error_handler(request: Request, exc: MandateLedgerError):
    """
    Handle all MandateLedgerError exceptions.

    Returns consistent error response format.
    """
    logger.warning(
        f"MandateLedgerError: {exc.error_code} - {exc.message}",
        extra={"details": exc.details}
    )

    # Map error types to HTTP status codes
    status_code_map = {
        "MANDATE_NOT_FOUND": status.HTTP_404_NOT_FOUND,
        "VERSION_CONFLICT": status.HTTP_409_CONFLICT,
        "INVALID_MANDATE_DATA": status.HTTP_400_BAD_REQUEST,
        "INVALID_STATE_TRANSITION": status.HTTP_400_BAD_REQUEST,
        "INVALID_API_KEY": status.HTTP_401_UNAUTHORIZED,
        "API_KEY_EXPIRED": status.HTTP_401_UNAUTHORIZED,
        "API_KEY_REVOKED": status.HTTP_401_UNAUTHORIZED,
        "INSUFFICIENT_PERMISSIONS": status.HTTP_403_FORBIDDEN,
        "RATE_LIMIT_EXCEEDED": status.HTTP_429_TOO_MANY_REQUESTS,
        "CHAIN_INTEGRITY_ERROR": status.HTTP_500_INTERNAL_SERVER_ERROR,
    }

    status_code = status_code_map.get(exc.error_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "message": exc.message,
                "code": exc.error_code,
                "details": exc.details
            }
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle unexpected exceptions.

    Logs full error and returns generic error response.
    """
    logger.error(
        f"Unexpected error: {type(exc).__name__} - {str(exc)}",
        exc_info=True
    )

    track_error(
        error_type=type(exc).__name__,
        operation=f"{request.method} {request.url.path}"
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "message": "An unexpected error occurred",
                "code": "INTERNAL_SERVER_ERROR",
                "details": {
                    "type": type(exc).__name__
                } if settings.is_development else {}
            }
        }
    )


# ==================== Health & Metrics Endpoints ====================

@app.get("/health", tags=["Health"])
async def health_check():
    """
    Basic health check endpoint.

    Returns:
        200 OK if service is running
    """
    return {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "environment": settings.ENVIRONMENT
    }


@app.get("/api/v1/health", tags=["Health"])
async def detailed_health_check():
    """
    Detailed health check with component status.

    Returns:
        Health status of service and components
    """
    from src.db.mongodb import MongoDB

    # Check database connection
    db_status = "healthy"
    try:
        if MongoDB.client:
            await MongoDB.client.admin.command('ping')
        else:
            db_status = "unhealthy"
    except Exception:
        db_status = "unhealthy"

    overall_status = "healthy" if db_status == "healthy" else "degraded"
    uptime = time.time() - SERVICE_START_TIME

    return {
        "status": overall_status,
        "timestamp": time.time(),
        "version": "0.1.0",
        "uptime_seconds": uptime,
        "database": {
            "status": db_status,
            "name": settings.MONGODB_DATABASE
        },
        "environment": settings.ENVIRONMENT
    }


@app.get("/api/v1/metrics", tags=["Monitoring"])
async def metrics():
    """
    Prometheus metrics endpoint.

    Returns:
        Prometheus-formatted metrics
    """
    if not settings.ENABLE_METRICS:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "Metrics not enabled"}
        )

    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with service information.

    Returns:
        Service metadata and available endpoints
    """
    return {
        "service": settings.SERVICE_NAME,
        "version": "0.1.0",
        "environment": settings.ENVIRONMENT,
        "documentation": "/docs",
        "health": "/api/v1/health",
        "metrics": "/api/v1/metrics" if settings.ENABLE_METRICS else None
    }


# ==================== API Routes ====================

# Import routers
from src.api.routes import mandates, audit, admin, auth, payments

# Include routers
app.include_router(mandates.router)
app.include_router(audit.router)
app.include_router(admin.router)
app.include_router(auth.router)
app.include_router(payments.router)


"""
MongoDB connection management.

Handles the lifecycle of MongoDB connections:
- Startup: connect_to_mongo()
- Runtime: get_database()
- Shutdown: close_mongo_connection()
"""

import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from src.config import settings

# SSL certificate support for macOS (fixes Python.org installer issues)
try:
    import certifi
    TLS_CA_FILE = certifi.where()
except ImportError:
    TLS_CA_FILE = None

logger = logging.getLogger(__name__)


class MongoDB:
    """
    Singleton class to manage MongoDB client and database.

    Usage:
        # At startup
        await connect_to_mongo()

        # During runtime
        db = get_database()
        collection = db["my_collection"]

        # Or use collection accessors
        mandate_ledger = MongoDB.mandate_ledger

        # At shutdown
        await close_mongo_connection()
    """

    client: AsyncIOMotorClient | None = None
    database: AsyncIOMotorDatabase | None = None

    # Collection accessors as class attributes (will be set after connection)
    mandate_ledger = None
    # NOTE: mandates_current_state removed - current state queried from ledger
    payments = None  # Payment records (auto-created by change streams)
    api_keys = None
    audit_logs = None
    idempotency_records = None
    consistency_checks = None
    rate_limits = None


async def connect_to_mongo() -> None:
    """
    Connect to MongoDB Atlas.

    This should be called once at application startup.
    It creates a connection pool and tests the connection.

    Raises:
        Exception: If connection fails
    """
    try:
        logger.info(f"Connecting to MongoDB: {settings.MONGODB_DATABASE}")
        
        # Build client options with connection pooling
        client_options = {
            "maxPoolSize": settings.MONGODB_MAX_POOL_SIZE,
            "minPoolSize": settings.MONGODB_MIN_POOL_SIZE,
            "maxIdleTimeMS": 45000,  # Close idle connections after 45 seconds
            "serverSelectionTimeoutMS": 5000,  # Timeout for server selection
            "connectTimeoutMS": 10000,  # Timeout for initial connection
            "socketTimeoutMS": 20000,  # Timeout for socket operations
        }

        # Add certifi CA file if available (fixes macOS SSL certificate issues)
        if TLS_CA_FILE:
            client_options["tlsCAFile"] = TLS_CA_FILE
            logger.debug(f"Using certifi CA file for TLS: {TLS_CA_FILE}")


        # Create MongoDB client with connection pooling
        MongoDB.client = AsyncIOMotorClient(
            settings.MONGODB_URI,
            **client_options
        )

        # Get database reference
        MongoDB.database = MongoDB.client[settings.MONGODB_DATABASE]

        # Set up collection references
        MongoDB.mandate_ledger = MongoDB.database["mandate_ledger"]
        # NOTE: mandates_current_state removed - current state queried from ledger
        MongoDB.payments = MongoDB.database["payments"]
        MongoDB.api_keys = MongoDB.database["api_keys"]
        MongoDB.audit_logs = MongoDB.database["audit_log"]  # Note: singular in DB
        MongoDB.idempotency_records = MongoDB.database["idempotency_records"]
        MongoDB.consistency_checks = MongoDB.database["consistency_checks"]
        MongoDB.rate_limits = MongoDB.database["rate_limits"]

        # NOTE: Index creation for mandate_ledger moved to src/db/indexes.py
        # The create_all_indexes() function handles all indexes at startup

        # Create indexes for payments collection
        try:
            await MongoDB.payments.create_index("payment_id", unique=True)
            await MongoDB.payments.create_index("transaction_id")
            await MongoDB.payments.create_index("merchant_agent")
            await MongoDB.payments.create_index("processed_at")
            await MongoDB.payments.create_index([("status", 1), ("processed_at", -1)])
            logger.info("Created indexes on payments collection")
        except Exception as e:
            logger.warning(f"Could not create payment indexes (may already exist): {e}")

        # Test the connection with a ping
        await MongoDB.client.admin.command('ping')

        logger.info("Successfully connected to MongoDB")
        logger.info(f"   Database: {settings.MONGODB_DATABASE}")
        logger.info(f"   Environment: {settings.ENVIRONMENT}")

    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise


async def close_mongo_connection() -> None:
    """
    Close MongoDB connection.

    This should be called once at application shutdown
    to gracefully close all connections in the pool.
    """
    if MongoDB.client is not None:
        logger.info("Closing MongoDB connection...")
        MongoDB.client.close()
        MongoDB.client = None
        MongoDB.database = None
        # Clear collection references
        MongoDB.mandate_ledger = None
        # NOTE: mandates_current_state removed
        MongoDB.payments = None
        MongoDB.api_keys = None
        MongoDB.audit_logs = None
        MongoDB.idempotency_records = None
        MongoDB.consistency_checks = None
        MongoDB.rate_limits = None
        logger.info("MongoDB connection closed")


def get_database() -> AsyncIOMotorDatabase:
    """
    Get the MongoDB database reference.

    This should be called during request handling to access collections.

    Returns:
        AsyncIOMotorDatabase: The database instance

    Raises:
        RuntimeError: If database is not connected
    """
    if MongoDB.database is None:
        raise RuntimeError(
            "MongoDB is not connected. "
            "Call connect_to_mongo() at startup first."
        )
    return MongoDB.database


def get_client() -> AsyncIOMotorClient:
    """
    Get the MongoDB client reference.

    This is mainly used for transaction sessions.

    Returns:
        AsyncIOMotorClient: The client instance

    Raises:
        RuntimeError: If client is not connected
    """
    if MongoDB.client is None:
        raise RuntimeError(
            "MongoDB is not connected. "
            "Call connect_to_mongo() at startup first."
        )
    return MongoDB.client

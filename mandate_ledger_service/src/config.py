"""
Configuration management using Pydantic Settings.

Loads configuration from environment variables (.env file).
All settings are validated at startup.
"""

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings are loaded from .env file or environment variables.
    Validation happens automatically via Pydantic.
    """


    MONGODB_URI: str = Field(
        ...,
        description="MongoDB connection string (mongodb+srv://...)"
    )

    MONGODB_DATABASE: str = Field(
        default="mandate_ledger",
        description="MongoDB database name"
    )

    MONGODB_MAX_POOL_SIZE: int = Field(
        default=50,
        description="Maximum number of connections in the MongoDB connection pool"
    )

    MONGODB_MIN_POOL_SIZE: int = Field(
        default=10,
        description="Minimum number of connections to maintain in the pool"
    )

    SERVICE_NAME: str = Field(
        default="mandate-ledger-service",
        description="Service name for logging and monitoring"
    )

    ENVIRONMENT: str = Field(
        default="development",
        description="Environment: development, staging, or production"
    )

    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL"
    )

    API_KEY_HASH_ALGORITHM: str = Field(
        default="bcrypt",
        description="Algorithm for hashing API keys"
    )

    ALLOWED_CORS_ORIGINS: str = Field(
        default="*",
        description="Comma-separated list of allowed CORS origins, or * for all"
    )

    DEFAULT_RATE_LIMIT_PER_MINUTE: int = Field(
        default=60,
        description="Default rate limit: requests per minute per agent"
    )

    ENABLE_METRICS: bool = Field(
        default=True,
        description="Enable Prometheus metrics endpoint"
    )

    # Bootstrap Authentication (for initial API key creation)
    BOOTSTRAP_ADMIN_KEY: str = Field(
        default="",
        description="Master key for initial API key creation (development only)"
    )

    ENABLE_BOOTSTRAP_AUTH: bool = Field(
        default=False,
        description="Enable bootstrap authentication (disable in production after setup)"
    )

    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment is one of the allowed values."""
        allowed = ["development", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"ENVIRONMENT must be one of {allowed}")
        return v

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is valid."""
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in allowed:
            raise ValueError(f"LOG_LEVEL must be one of {allowed}")
        return v_upper

    @field_validator("API_KEY_HASH_ALGORITHM")
    @classmethod
    def validate_hash_algorithm(cls, v: str) -> str:
        """Validate hash algorithm is supported."""
        allowed = ["bcrypt"]
        if v not in allowed:
            raise ValueError(f"API_KEY_HASH_ALGORITHM must be one of {allowed}")
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # Ignore extra fields in .env
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        if self.ALLOWED_CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.ALLOWED_CORS_ORIGINS.split(",")]

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT == "production"

# This will be loaded once at startup
# If .env is missing or invalid, this will raise an error immediately
settings = Settings()


"""Application configuration settings for different environments."""
import os
from datetime import timedelta
from pathlib import Path

# Base directory of the backend package
BASE_DIR = Path(__file__).resolve().parent.parent


class BaseConfig:
    """Base configuration shared across environments."""
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "dev-secret-key-mad2-tma-v2-production-grade-32bytes"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Ensure instance directory exists
    INSTANCE_DIR = BASE_DIR / "instance"
    INSTANCE_DIR.mkdir(parents=True, exist_ok=True)

    # JWT Settings (Ensure default key >= 32 bytes for RFC 7518 compliance)
    JWT_SECRET_KEY = os.environ.get(
        "JWT_SECRET_KEY",
        "dev-jwt-secret-key-mad2-tma-v2-super-secure-32bytes"
    )
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        hours=int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRES_HOURS", 2))
    )
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"

    # CORS settings (restricted to local frontend)
    CORS_ORIGINS = os.environ.get(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")


class DevelopmentConfig(BaseConfig):
    """Configuration for local development."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{(BASE_DIR / 'instance' / 'tma.db').resolve().as_posix()}"
    )


class TestingConfig(BaseConfig):
    """Configuration for automated test execution."""
    TESTING = True
    DEBUG = False
    # Use isolated in-memory SQLite database for testing
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    JWT_SECRET_KEY = "test-jwt-secret-key-mad2-tma-v2-32bytes-secure!"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)


class ProductionConfig(BaseConfig):
    """Configuration for production deployment."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{(BASE_DIR / 'instance' / 'tma.db').resolve().as_posix()}"
    )
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}

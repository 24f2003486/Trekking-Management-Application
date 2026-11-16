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

    # Celery & Redis Settings
    REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", REDIS_URL)
    CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", REDIS_URL)
    CELERY_TIMEZONE = "UTC"
    REMINDER_WINDOW_DAYS = int(os.environ.get("REMINDER_WINDOW_DAYS", 3))

    # Private directories for exports and reports
    EXPORTS_DIR = INSTANCE_DIR / "exports"
    REPORTS_DIR = INSTANCE_DIR / "reports"
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)


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
    # Celery test configuration
    CELERY_TASK_ALWAYS_EAGER = True
    CELERY_TASK_EAGER_PROPAGATES = True
    CELERY_BROKER_URL = "memory://"
    CELERY_RESULT_BACKEND = "cache+memory://"



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

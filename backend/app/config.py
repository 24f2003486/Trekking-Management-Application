"""Application configuration settings for different environments."""
import os
from pathlib import Path

# Base directory of the backend package
BASE_DIR = Path(__file__).resolve().parent.parent


class BaseConfig:
    """Base configuration shared across environments."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-mad2-tma-v2")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Ensure instance directory exists
    INSTANCE_DIR = BASE_DIR / "instance"
    INSTANCE_DIR.mkdir(parents=True, exist_ok=True)


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


class ProductionConfig(BaseConfig):
    """Configuration for production deployment."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{(BASE_DIR / 'instance' / 'tma.db').resolve().as_posix()}"
    )


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}

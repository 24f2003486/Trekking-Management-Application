"""Flask application factory and database initialization."""
import os
import sqlite3
import click
from flask import Flask
from sqlalchemy import event
from sqlalchemy.engine import Engine
from backend.app.config import config
from backend.app.extensions import db


# Enable SQLite foreign key enforcement for all SQLite connections
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Enable foreign key constraints for SQLite connections."""
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()


def create_app(config_name: str = None) -> Flask:
    """Application factory for Trekking Management Application V2."""
    if config_name is None:
        config_name = os.environ.get("FLASK_CONFIG", "development")

    app = Flask(__name__, instance_relative_config=True)
    
    # Load configuration
    cfg = config.get(config_name, config["default"])
    app.config.from_object(cfg)
    
    # Ensure instance directory exists
    os.makedirs(app.instance_path, exist_ok=True)
    
    # Initialize extensions
    db.init_app(app)
    
    # Import models within app context so SQLAlchemy is aware of all models
    with app.app_context():
        from backend.app.models import User, Trek, Booking, StaffProfile  # noqa: F401
    
    # CLI command for programmatic database initialization
    @app.cli.command("init-db")
    def init_db_command():
        """Initialize and create all database tables programmatically."""
        db.create_all()
        click.echo("Database initialized successfully. All tables created.")

    return app


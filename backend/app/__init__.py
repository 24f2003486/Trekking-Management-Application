"""Flask application factory, extensions initialization, and route registration."""
import os
import sqlite3
import click
from flask import Flask
from sqlalchemy import event
from sqlalchemy.engine import Engine
from backend.app.config import config
from backend.app.extensions import db, jwt, cors
from backend.app.utils.responses import error_response


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
    jwt.init_app(app)
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": app.config.get("CORS_ORIGINS", "*")}},
        supports_credentials=True
    )
    
    # Import models within app context so SQLAlchemy is aware of all models
    with app.app_context():
        from backend.app.models import (  # noqa: F401
            User,
            Trek,
            Booking,
            StaffProfile,
            TokenBlocklist
        )
    
    # Configure JWT token blocklist verification (SQLite backed)
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
        from backend.app.models.token_blocklist import TokenBlocklist
        jti = jwt_payload.get("jti")
        token = db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar()
        return token is not None

    # Standardized JWT error responses
    @jwt.unauthorized_loader
    def custom_unauthorized_response(error_message):
        return error_response(
            f"Authentication required: {error_message}",
            status_code=401
        )

    @jwt.invalid_token_loader
    def custom_invalid_token_response(error_message):
        return error_response(
            f"Invalid authentication token: {error_message}",
            status_code=401
        )

    @jwt.expired_token_loader
    def custom_expired_token_response(jwt_header, jwt_payload):
        return error_response(
            "Authentication token has expired. Please log in again.",
            status_code=401
        )

    @jwt.revoked_token_loader
    def custom_revoked_token_response(jwt_header, jwt_payload):
        return error_response(
            "Authentication token has been revoked. Please log in again.",
            status_code=401
        )

    # Register blueprints
    from backend.app.routes import (
        auth_bp,
        admin_bp,
        admin_treks_bp,
        admin_staff_bp,
        admin_users_bp,
        admin_bookings_bp,
        admin_reports_bp,
        staff_bp,
        trekker_bp,
    )
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(admin_treks_bp)
    app.register_blueprint(admin_staff_bp)
    app.register_blueprint(admin_users_bp)
    app.register_blueprint(admin_bookings_bp)
    app.register_blueprint(admin_reports_bp)
    app.register_blueprint(staff_bp)
    app.register_blueprint(trekker_bp)

    # CLI command for programmatic database initialization
    @app.cli.command("init-db")
    def init_db_command():
        """Initialize and create all database tables programmatically."""
        db.create_all()
        # Safe schema migration for operational_progress if table pre-existed
        with db.engine.connect() as conn:
            from sqlalchemy import inspect, text
            inspector = inspect(conn)
            if "treks" in inspector.get_table_names():
                cols = [c["name"] for c in inspector.get_columns("treks")]
                if "operational_progress" not in cols:
                    conn.execute(text("ALTER TABLE treks ADD COLUMN operational_progress VARCHAR(20) NOT NULL DEFAULT 'Not Started'"))
                    conn.commit()
        click.echo("Database initialized successfully. All tables created.")

    return app

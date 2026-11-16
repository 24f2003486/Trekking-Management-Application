"""Programmatic Admin account provisioning script."""
import os
import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app import create_app
from backend.app.extensions import db
from backend.app.models import User


def create_admin(app=None, config_name: str = None):
    """Create initial Admin account if one does not already exist."""
    admin_password = os.environ.get("ADMIN_INITIAL_PASSWORD")
    if not admin_password:
        print(
            "ERROR: The 'ADMIN_INITIAL_PASSWORD' environment variable is not set.\n"
            "Please set this variable before running the script.\n"
            "Example (PowerShell): $env:ADMIN_INITIAL_PASSWORD=\"YourSecurePassword123!\"",
            file=sys.stderr
        )
        sys.exit(1)

    if app is None:
        if config_name is None:
            config_name = os.environ.get("FLASK_CONFIG", "development")
        app = create_app(config_name)
    
    with app.app_context():
        # Ensure database tables exist
        db.create_all()
        
        reserved_email = "admin@trekkingapp.local"
        user_with_reserved_email = User.query.filter_by(email=reserved_email).first()
        
        # Distinguish between an existing Admin and an email conflict with a non-admin
        if user_with_reserved_email:
            if user_with_reserved_email.role == "Admin":
                print(
                    f"Notice: Admin account already exists (ID: {user_with_reserved_email.id}, "
                    f"Email: {user_with_reserved_email.email}). Duplicate creation prevented."
                )
                return
            else:
                print(
                    f"Conflict Error: A user with the reserved Admin email '{reserved_email}' already exists, "
                    f"but has role '{user_with_reserved_email.role}' (ID: {user_with_reserved_email.id}). "
                    "Cannot provision Admin account with this email. Please resolve the email conflict.",
                    file=sys.stderr
                )
                sys.exit(1)

        # Check if an Admin account already exists under a different email address
        existing_admin = User.query.filter_by(role="Admin").first()
        if existing_admin:
            print(
                f"Notice: An Admin account already exists in the system (ID: {existing_admin.id}, "
                f"Email: {existing_admin.email}). Duplicate creation prevented."
            )
            return

        # Provision new Admin account
        admin = User(
            full_name="System Administrator",
            email=reserved_email,
            role="Admin",
            status="Active"
        )
        admin.set_password(admin_password)
        
        db.session.add(admin)
        db.session.commit()
        
        print(
            f"Success: Admin account created successfully.\n"
            f"  Full Name: {admin.full_name}\n"
            f"  Email: {admin.email}\n"
            f"  Role: {admin.role}\n"
            f"  Status: {admin.status}"
        )


if __name__ == "__main__":
    create_admin()

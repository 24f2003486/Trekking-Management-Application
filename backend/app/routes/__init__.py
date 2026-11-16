"""Routes package for Trekking Management Application V2."""
from backend.app.routes.auth import auth_bp
from backend.app.routes.admin import admin_bp
from backend.app.routes.staff import staff_bp
from backend.app.routes.trekker import trekker_bp

__all__ = ["auth_bp", "admin_bp", "staff_bp", "trekker_bp"]


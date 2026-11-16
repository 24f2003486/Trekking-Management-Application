"""Routes package for Trekking Management Application V2."""
from backend.app.routes.auth import auth_bp
from backend.app.routes.admin import admin_bp
from backend.app.routes.admin_treks import admin_treks_bp
from backend.app.routes.admin_staff import admin_staff_bp
from backend.app.routes.admin_users import admin_users_bp
from backend.app.routes.admin_bookings import admin_bookings_bp
from backend.app.routes.admin_reports import admin_reports_bp
from backend.app.routes.staff import staff_bp
from backend.app.routes.trekker import trekker_bp
from backend.app.routes.notifications import notifications_bp

__all__ = [
    "auth_bp",
    "admin_bp",
    "admin_treks_bp",
    "admin_staff_bp",
    "admin_users_bp",
    "admin_bookings_bp",
    "admin_reports_bp",
    "staff_bp",
    "trekker_bp",
    "notifications_bp",
]

"""Admin overview dashboard route."""
from flask import Blueprint, g
from backend.app.models.user import User
from backend.app.models.trek import Trek
from backend.app.models.booking import Booking
from backend.app.utils.decorators import role_required
from backend.app.utils.responses import success_response

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


@admin_bp.route("/dashboard", methods=["GET"])
@role_required("Admin")
def admin_dashboard():
    """
    Admin dashboard overview returning actual database statistics.
    """
    total_treks = Trek.query.count()
    total_users = User.query.count()
    total_staff = User.query.filter_by(role="Trek Staff").count()
    total_trekkers = User.query.filter_by(role="Trekker").count()
    total_admins = User.query.filter_by(role="Admin").count()
    total_bookings = Booking.query.count()

    open_treks = Trek.query.filter_by(status="Open").count()
    completed_treks = Trek.query.filter_by(status="Completed").count()
    pending_treks = Trek.query.filter_by(status="Pending").count()

    active_users = User.query.filter_by(status="Active").count()
    inactive_users = User.query.filter_by(status="Inactive").count()
    blacklisted_users = User.query.filter_by(status="Blacklisted").count()

    stats = {
        "role": "Admin",
        "admin_name": g.current_user.full_name,
        "total_treks": total_treks,
        "total_users": total_users,
        "total_staff": total_staff,
        "total_trekkers": total_trekkers,
        "total_admins": total_admins,
        "total_bookings": total_bookings,
        "open_treks": open_treks,
        "completed_treks": completed_treks,
        "pending_treks": pending_treks,
        "active_users": active_users,
        "inactive_users": inactive_users,
        "blacklisted_users": blacklisted_users,
    }

    return success_response(
        "Admin dashboard statistics retrieved successfully",
        data=stats
    )

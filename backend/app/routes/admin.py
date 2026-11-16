"""Admin role-protected routes."""
from flask import Blueprint, g
from backend.app.utils.decorators import role_required
from backend.app.utils.responses import success_response

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


@admin_bp.route("/dashboard", methods=["GET"])
@role_required("Admin")
def admin_dashboard():
    """Admin dashboard placeholder endpoint."""
    user = g.current_user
    return success_response(
        "Admin dashboard access granted",
        data={
            "role": "Admin",
            "admin_name": user.full_name,
            "message": "Welcome to the Administrator portal. All admin controls will be available in future milestones."
        }
    )


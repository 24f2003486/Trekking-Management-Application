"""Trek Staff role-protected routes."""
from flask import Blueprint, g
from backend.app.utils.decorators import role_required
from backend.app.utils.responses import success_response

staff_bp = Blueprint("staff", __name__, url_prefix="/api/staff")


@staff_bp.route("/dashboard", methods=["GET"])
@role_required("Trek Staff")
def staff_dashboard():
    """Trek Staff dashboard placeholder endpoint."""
    user = g.current_user
    return success_response(
        "Trek Staff dashboard access granted",
        data={
            "role": "Trek Staff",
            "staff_name": user.full_name,
            "specialization": user.staff_profile.specialization if user.staff_profile else None,
            "message": "Welcome to the Trek Staff portal. Assigned expeditions will be available in future milestones."
        }
    )


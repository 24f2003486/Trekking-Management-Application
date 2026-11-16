"""Trekker role-protected routes."""
from flask import Blueprint, g
from backend.app.utils.decorators import role_required
from backend.app.utils.responses import success_response

trekker_bp = Blueprint("trekker", __name__, url_prefix="/api/trekker")


@trekker_bp.route("/dashboard", methods=["GET"])
@role_required("Trekker")
def trekker_dashboard():
    """Trekker dashboard placeholder endpoint."""
    user = g.current_user
    return success_response(
        "Trekker dashboard access granted",
        data={
            "role": "Trekker",
            "trekker_name": user.full_name,
            "message": "Welcome to your Trekker portal. Browse treks and bookings will be available in future milestones."
        }
    )


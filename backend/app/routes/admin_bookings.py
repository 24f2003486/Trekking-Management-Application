"""Admin booking management and historical record inspection routes."""
from flask import Blueprint, request
from sqlalchemy import or_
from backend.app.extensions import db
from backend.app.models.booking import Booking
from backend.app.models.user import User
from backend.app.models.trek import Trek
from backend.app.utils.decorators import role_required
from backend.app.utils.responses import success_response, error_response

admin_bookings_bp = Blueprint("admin_bookings", __name__, url_prefix="/api/admin/bookings")


@admin_bookings_bp.route("", methods=["GET"])
@role_required("Admin")
def list_bookings():
    """List bookings with search, status filtering, and pagination."""
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 10, type=int), 100)
    search = request.args.get("search", "").strip()
    status = request.args.get("status", "").strip()

    query = Booking.query.join(User, Booking.user_id == User.id).join(Trek, Booking.trek_id == Trek.id)

    if search:
        search_filter = or_(
            User.full_name.ilike(f"%{search}%"),
            User.email.ilike(f"%{search}%"),
            Trek.trek_name.ilike(f"%{search}%")
        )
        if search.isdigit():
            search_filter = or_(search_filter, Booking.id == int(search))
        query = query.filter(search_filter)

    if status:
        query = query.filter(Booking.booking_status == status)

    query = query.order_by(Booking.booking_date.desc())
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    return success_response(
        "Bookings retrieved successfully",
        data={
            "bookings": [b.to_dict() for b in paginated.items],
            "pagination": {
                "page": paginated.page,
                "per_page": paginated.per_page,
                "total": paginated.total,
                "total_items": paginated.total,
                "pages": paginated.pages,
                "total_pages": paginated.pages,
                "has_prev": paginated.has_prev,
                "has_next": paginated.has_next,
            }
        }
    )


@admin_bookings_bp.route("/<int:booking_id>", methods=["GET"])
@role_required("Admin")
def get_booking(booking_id):
    """Retrieve details of a single booking."""
    booking = db.session.get(Booking, booking_id)
    if not booking:
        return error_response(f"Booking with ID {booking_id} not found.", status_code=404)
    b_dict = booking.to_dict()
    return success_response("Booking details retrieved successfully", data={"booking": b_dict, **b_dict})

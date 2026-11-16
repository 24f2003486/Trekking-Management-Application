"""Trekker role-protected routes and booking management."""
from datetime import datetime, date
import re
from flask import Blueprint, request, g
from sqlalchemy import or_, desc, asc
from sqlalchemy.exc import IntegrityError
from backend.app.extensions import db
from backend.app.models.user import User
from backend.app.models.trek import Trek
from backend.app.models.booking import Booking
from backend.app.utils.decorators import role_required
from backend.app.utils.responses import success_response, error_response

trekker_bp = Blueprint("trekker", __name__, url_prefix="/api/trekker")


def serialize_trekker_trek(trek, current_user_id=None):
    """Serialize trek details for trekker views with capacity calculations."""
    d = trek.to_dict()
    active_count = Booking.query.filter_by(trek_id=trek.id, booking_status="Booked").count()
    total_slots = trek.available_slots
    remaining_slots = max(0, total_slots - active_count)
    d["total_slots"] = total_slots
    d["booked_slots"] = active_count
    d["remaining_slots"] = remaining_slots
    d["is_full"] = remaining_slots <= 0
    d["is_open"] = trek.status == "Open"
    d["is_bookable"] = trek.status == "Open" and trek.operational_progress != "Completed" and remaining_slots > 0

    if current_user_id:
        has_active = Booking.query.filter_by(
            user_id=current_user_id,
            trek_id=trek.id,
            booking_status="Booked"
        ).first() is not None
        d["has_active_booking"] = has_active
        d["can_book"] = d["is_bookable"] and not has_active
    else:
        d["has_active_booking"] = False
        d["can_book"] = d["is_bookable"]

    return d


def serialize_trekker_booking(booking):
    """Serialize booking details for trekker history views."""
    trek = booking.trek
    return {
        "id": booking.id,
        "booking_id": booking.id,
        "booking_date": booking.booking_date.isoformat() if booking.booking_date else None,
        "booking_status": booking.booking_status,
        "status": booking.booking_status,
        "payment_status": booking.payment_status or "Pending",
        "created_at": booking.created_at.isoformat() if booking.created_at else None,
        "trek_id": booking.trek_id,
        "trek": {
            "id": trek.id,
            "name": trek.trek_name,
            "trek_name": trek.trek_name,
            "location": trek.location,
            "difficulty": trek.difficulty,
            "duration_days": trek.duration_days,
            "start_date": trek.start_date.isoformat() if trek.start_date else None,
            "end_date": trek.end_date.isoformat() if trek.end_date else None,
            "status": trek.status,
            "operational_progress": trek.operational_progress,
            "progress": trek.operational_progress,
            "assigned_staff_name": trek.assigned_staff.full_name if trek.assigned_staff else None
        } if trek else None,
        "trek_name": trek.trek_name if trek else None,
        "trek_location": trek.location if trek else None,
        "trek_difficulty": trek.difficulty if trek else None,
        "trek_duration_days": trek.duration_days if trek else None,
        "trek_start_date": trek.start_date.isoformat() if trek and trek.start_date else None,
        "trek_end_date": trek.end_date.isoformat() if trek and trek.end_date else None,
        "trek_status": trek.status if trek else None,
        "trek_operational_progress": trek.operational_progress if trek else None
    }


# =============================================================================
# 1. Trekker Dashboard
# =============================================================================
@trekker_bp.route("/dashboard", methods=["GET"])
@role_required("Trekker")
def trekker_dashboard():
    """Trekker dashboard metrics, upcoming expeditions, and recent bookings."""
    user = g.current_user

    # Booking counts strictly for current trekker
    base_query = Booking.query.filter_by(user_id=user.id)
    total_bookings = base_query.count()
    active_bookings = base_query.filter_by(booking_status="Booked").count()
    cancelled_bookings = base_query.filter_by(booking_status="Cancelled").count()
    completed_bookings = base_query.filter_by(booking_status="Completed").count()

    # Upcoming booked expeditions (Active reservations)
    upcoming_bookings = (
        base_query.filter_by(booking_status="Booked")
        .join(Trek, Booking.trek_id == Trek.id)
        .order_by(Trek.start_date.asc())
        .limit(5)
        .all()
    )

    # Recent booking activity
    recent_bookings = (
        base_query.order_by(Booking.booking_date.desc())
        .limit(5)
        .all()
    )

    return success_response(
        "Trekker dashboard access granted",
        data={
            "role": "Trekker",
            "trekker_name": user.full_name,
            "email": user.email,
            "contact_number": user.contact_number,
            "status": user.status,
            "total_bookings": total_bookings,
            "active_bookings": active_bookings,
            "cancelled_bookings": cancelled_bookings,
            "completed_bookings": completed_bookings,
            "metrics": {
                "total_bookings": total_bookings,
                "active_bookings": active_bookings,
                "cancelled_bookings": cancelled_bookings,
                "completed_bookings": completed_bookings,
            },
            "upcoming_treks": [serialize_trekker_booking(b) for b in upcoming_bookings],
            "recent_bookings": [serialize_trekker_booking(b) for b in recent_bookings],
        }
    )


# =============================================================================
# 2. Profile Management
# =============================================================================
@trekker_bp.route("/profile", methods=["GET"])
@role_required("Trekker")
def get_profile():
    """Retrieve authenticated Trekker's profile."""
    user = g.current_user
    return success_response("Profile retrieved successfully", data=user.to_dict())


@trekker_bp.route("/profile", methods=["PUT"])
@role_required("Trekker")
def update_profile():
    """Update authenticated Trekker's permitted profile fields."""
    user = g.current_user
    payload = request.get_json(silent=True) or {}

    # Strict protection: do not allow role or status mutation
    if "role" in payload and payload["role"] != user.role:
        return error_response("Role modification is strictly prohibited.", status_code=400)
    if "status" in payload and payload["status"] != user.status:
        return error_response("Status modification is strictly prohibited.", status_code=400)

    # Full name validation
    full_name = payload.get("full_name")
    if full_name is not None:
        full_name = full_name.strip()
        if not full_name:
            return error_response("Full name cannot be empty.", status_code=400)
        if len(full_name) < 2 or len(full_name) > 100:
            return error_response("Full name must be between 2 and 100 characters.", status_code=400)
        user.full_name = full_name

    # Contact number validation
    if "contact_number" in payload or "phone_number" in payload:
        raw_contact = payload.get("contact_number") or payload.get("phone_number") or ""
        contact = raw_contact.strip()
        if contact:
            # Validate format (digits, spaces, optional leading plus, hyphen)
            if not re.match(r"^\+?[0-9\s\-]{7,20}$", contact):
                return error_response(
                    "Invalid contact number format. Use standard telephone format (e.g., +91 9876543210).",
                    status_code=400
                )
            user.contact_number = contact
        else:
            user.contact_number = None

    # Email update support with uniqueness enforcement
    if "email" in payload:
        email = payload.get("email", "").strip().lower()
        if email and email != user.email:
            if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
                return error_response("Invalid email format.", status_code=400)
            existing = User.query.filter(User.email == email, User.id != user.id).first()
            if existing:
                return error_response("An account with this email address already exists.", status_code=409)
            user.email = email

    db.session.commit()
    return success_response("Profile updated successfully.", data=user.to_dict())


# =============================================================================
# 3. Browse Available Treks
# =============================================================================
@trekker_bp.route("/treks", methods=["GET"])
@role_required("Trekker")
def list_available_treks():
    """Browse treks available for booking with search, filters, and pagination."""
    user = g.current_user
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 10, type=int), 50)
    search = request.args.get("search", "").strip()
    difficulty = request.args.get("difficulty", "").strip()
    location = request.args.get("location", "").strip()
    duration = request.args.get("duration", type=int)
    min_duration = request.args.get("min_duration", type=int)
    max_duration = request.args.get("max_duration", type=int)
    sort_by = request.args.get("sort_by", "start_date").strip()
    sort_order = request.args.get("sort_order", "asc").strip().lower()

    # Only treks that are Open for bookings and not completed
    query = Trek.query.filter(
        Trek.status == "Open",
        Trek.operational_progress != "Completed"
    )

    if search:
        search_filter = or_(
            Trek.trek_name.ilike(f"%{search}%"),
            Trek.location.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)

    if difficulty:
        query = query.filter(Trek.difficulty == difficulty)

    if location:
        query = query.filter(Trek.location.ilike(f"%{location}%"))

    if duration:
        query = query.filter(Trek.duration_days == duration)

    if min_duration is not None:
        query = query.filter(Trek.duration_days >= min_duration)

    if max_duration is not None:
        query = query.filter(Trek.duration_days <= max_duration)

    sort_column = getattr(Trek, sort_by, Trek.start_date)
    order_func = desc if sort_order == "desc" else asc
    query = query.order_by(order_func(sort_column))

    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    return success_response(
        "Available treks retrieved successfully",
        data={
            "treks": [serialize_trekker_trek(trek, current_user_id=user.id) for trek in paginated.items],
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


# =============================================================================
# 4. Trek Details
# =============================================================================
@trekker_bp.route("/treks/<int:trek_id>", methods=["GET"])
@role_required("Trekker")
def get_trek_details(trek_id):
    """Retrieve detailed information and booking eligibility for a specific trek."""
    user = g.current_user
    trek = db.session.get(Trek, trek_id)
    if not trek:
        return error_response(f"Trek with ID {trek_id} not found.", status_code=404)

    data = serialize_trekker_trek(trek, current_user_id=user.id)
    return success_response("Trek details retrieved successfully", data={"trek": data, **data})


# =============================================================================
# 5. Book a Trek
# =============================================================================
@trekker_bp.route("/bookings", methods=["POST"])
@role_required("Trekker")
def book_trek():
    """Book a trek slot for the authenticated Trekker with atomic concurrency protection."""
    user = g.current_user
    payload = request.get_json(silent=True) or {}

    raw_trek_id = payload.get("trek_id")
    if raw_trek_id is None:
        return error_response("trek_id is required.", status_code=400)

    try:
        trek_id = int(raw_trek_id)
    except (ValueError, TypeError):
        return error_response("trek_id must be a valid integer.", status_code=400)

    # 1. Trek exists check
    trek = db.session.get(Trek, trek_id)
    if not trek:
        return error_response(f"Trek with ID {trek_id} not found.", status_code=404)

    # 2. Trek must not be completed
    if trek.status == "Completed" or trek.operational_progress == "Completed":
        return error_response(
            f"Cannot book trek '{trek.trek_name}' because it has already concluded.",
            status_code=400
        )

    # 3. Booking status must be Open
    if trek.status != "Open":
        return error_response(
            f"Trek '{trek.trek_name}' is not open for bookings (status is '{trek.status}').",
            status_code=400
        )

    # 4. Check for duplicate active reservation by current user
    existing_active = Booking.query.filter_by(
        user_id=user.id,
        trek_id=trek.id,
        booking_status="Booked"
    ).first()
    if existing_active:
        return error_response(
            f"You already have an active reservation for '{trek.trek_name}' (Booking #{existing_active.id}). "
            "Duplicate active bookings are not permitted.",
            status_code=409
        )

    # 5. Capacity check (active bookings vs available_slots)
    active_count = Booking.query.filter_by(
        trek_id=trek.id,
        booking_status="Booked"
    ).count()
    if active_count >= trek.available_slots:
        return error_response(
            f"Trek '{trek.trek_name}' is fully booked ({active_count}/{trek.available_slots} slots taken). "
            "No capacity remains.",
            status_code=409
        )

    # 6. Atomic creation with partial unique index enforcement
    booking = Booking(
        user_id=user.id,
        trek_id=trek.id,
        booking_date=datetime.utcnow(),
        booking_status="Booked",
        payment_status="Pending"
    )
    db.session.add(booking)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return error_response(
            "A booking reservation conflict occurred (duplicate active booking or capacity limit reached).",
            status_code=409
        )
    except Exception as e:
        db.session.rollback()
        return error_response(f"Booking creation failed: {str(e)}", status_code=500)

    serialized = serialize_trekker_booking(booking)
    return success_response(
        f"Expedition slot successfully reserved for '{trek.trek_name}'!",
        data={"booking": serialized, **serialized},
        status_code=201
    )


# =============================================================================
# 6. Booking History
# =============================================================================
@trekker_bp.route("/bookings", methods=["GET"])
@role_required("Trekker")
def list_my_bookings():
    """Retrieve authenticated Trekker's booking history with filters and pagination."""
    user = g.current_user
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 10, type=int), 50)
    status_filter = request.args.get("status", "").strip()

    # STRICT ISOLATION: Only bookings belonging to current_user
    query = Booking.query.filter(Booking.user_id == user.id)

    if status_filter and status_filter.lower() != "all":
        query = query.filter(Booking.booking_status == status_filter)

    query = query.order_by(Booking.booking_date.desc())
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    return success_response(
        "Booking history retrieved successfully",
        data={
            "bookings": [serialize_trekker_booking(b) for b in paginated.items],
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


# =============================================================================
# 7. Individual Booking Details
# =============================================================================
@trekker_bp.route("/bookings/<int:booking_id>", methods=["GET"])
@role_required("Trekker")
def get_booking_details(booking_id):
    """Retrieve details for a single booking strictly owned by the authenticated Trekker."""
    user = g.current_user
    booking = db.session.get(Booking, booking_id)
    if not booking:
        return error_response(f"Booking with ID {booking_id} not found.", status_code=404)

    # STRICT ISOLATION: User can only view their own booking
    if booking.user_id != user.id:
        return error_response("You are not authorized to view this booking.", status_code=403)

    serialized = serialize_trekker_booking(booking)
    return success_response(
        "Booking details retrieved successfully",
        data={"booking": serialized, **serialized}
    )

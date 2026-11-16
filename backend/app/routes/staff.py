"""Trek Staff role-protected routes and operations."""
from flask import Blueprint, request, g
from sqlalchemy import or_, desc, asc
from backend.app.extensions import db
from backend.app.models.trek import Trek
from backend.app.models.booking import Booking
from backend.app.models.user import User
from backend.app.utils.decorators import role_required
from backend.app.utils.responses import success_response, error_response

staff_bp = Blueprint("staff", __name__, url_prefix="/api/staff")


def serialize_staff_trek(trek):
    """Serialize a trek with participant/booking metrics for staff view."""
    d = trek.to_dict()
    active_count = Booking.query.filter_by(trek_id=trek.id, booking_status="Booked").count()
    cancelled_count = Booking.query.filter_by(trek_id=trek.id, booking_status="Cancelled").count()
    d["active_bookings_count"] = active_count
    d["booked_slots"] = active_count
    d["active_participants_count"] = active_count
    d["cancelled_bookings_count"] = cancelled_count
    d["remaining_slots"] = max(0, trek.available_slots - active_count)
    return d


@staff_bp.route("/dashboard", methods=["GET"])
@role_required("Trek Staff")
def staff_dashboard():
    """Trek Staff dashboard metrics and assigned trek overview."""
    user = g.current_user

    # Base query for treks assigned to this staff member
    treks_query = Trek.query.filter(Trek.assigned_staff_id == user.id)
    total_assigned_treks = treks_query.count()
    open_treks = treks_query.filter(Trek.status == "Open").count()
    closed_treks = treks_query.filter(Trek.status == "Closed").count()

    # Progress counts
    not_started_treks = treks_query.filter(Trek.operational_progress == "Not Started").count()
    started_treks = treks_query.filter(Trek.operational_progress == "Started").count()
    ongoing_treks = treks_query.filter(
        or_(Trek.operational_progress == "Ongoing", Trek.status == "Ongoing")
    ).count()
    completed_treks = treks_query.filter(
        or_(Trek.operational_progress == "Completed", Trek.status == "Completed")
    ).count()

    # Total active participants across all assigned treks
    active_participants = (
        db.session.query(db.func.count(Booking.id))
        .join(Trek, Booking.trek_id == Trek.id)
        .filter(Trek.assigned_staff_id == user.id, Booking.booking_status == "Booked")
        .scalar()
        or 0
    )

    # Assigned treks (ordered by start_date asc)
    assigned_treks = (
        treks_query.order_by(Trek.start_date.asc())
        .limit(10)
        .all()
    )

    specialization = user.staff_profile.specialization if user.staff_profile else None
    experience_years = user.staff_profile.experience_years if user.staff_profile else 0

    return success_response(
        "Trek Staff dashboard access granted",
        data={
            "role": "Trek Staff",
            "staff_name": user.full_name,
            "email": user.email,
            "specialization": specialization,
            "experience_years": experience_years,
            "total_assigned_treks": total_assigned_treks,
            "open_treks": open_treks,
            "closed_treks": closed_treks,
            "ongoing_treks": ongoing_treks,
            "completed_treks": completed_treks,
            "not_started_treks": not_started_treks,
            "started_treks": started_treks,
            "total_participants": active_participants,
            "active_participants": active_participants,
            "metrics": {
                "total_assigned_treks": total_assigned_treks,
                "open_treks": open_treks,
                "closed_treks": closed_treks,
                "ongoing_treks": ongoing_treks,
                "completed_treks": completed_treks,
                "not_started_treks": not_started_treks,
                "started_treks": started_treks,
                "total_participants": active_participants,
                "active_participants": active_participants,
            },
            "assigned_treks": [serialize_staff_trek(t) for t in assigned_treks],
            "treks": [serialize_staff_trek(t) for t in assigned_treks],
        }
    )


@staff_bp.route("/treks", methods=["GET"])
@role_required("Trek Staff")
def list_assigned_treks():
    """List treks assigned to the authenticated staff member with filters and pagination."""
    user = g.current_user
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 10, type=int), 100)
    search = request.args.get("search", "").strip()
    status = request.args.get("status", "").strip()
    progress = (
        request.args.get("progress", "")
        or request.args.get("operational_progress", "")
    ).strip()
    difficulty = request.args.get("difficulty", "").strip()
    sort_by = request.args.get("sort_by", "start_date").strip()
    sort_order = request.args.get("sort_order", "asc").strip().lower()

    # STRICT ISOLATION: Only treks assigned to current_user
    query = Trek.query.filter(Trek.assigned_staff_id == user.id)

    if search:
        search_filter = or_(
            Trek.trek_name.ilike(f"%{search}%"),
            Trek.location.ilike(f"%{search}%")
        )
        if search.isdigit():
            search_filter = or_(search_filter, Trek.id == int(search))
        query = query.filter(search_filter)

    if status:
        query = query.filter(Trek.status == status)

    if progress:
        query = query.filter(Trek.operational_progress == progress)

    if difficulty:
        query = query.filter(Trek.difficulty == difficulty)

    sort_column = getattr(Trek, sort_by, Trek.start_date)
    order_func = desc if sort_order == "desc" else asc
    query = query.order_by(order_func(sort_column))

    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    return success_response(
        "Assigned treks retrieved successfully",
        data={
            "treks": [serialize_staff_trek(trek) for trek in paginated.items],
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


@staff_bp.route("/treks/<int:trek_id>", methods=["GET"])
@role_required("Trek Staff")
def get_assigned_trek(trek_id):
    """Retrieve details of an assigned trek."""
    user = g.current_user
    trek = db.session.get(Trek, trek_id)
    if not trek:
        return error_response(f"Trek with ID {trek_id} not found.", status_code=404)

    # STRICT ISOLATION: Must be assigned to this staff member
    if trek.assigned_staff_id != user.id:
        return error_response("You are not authorized to access this trek.", status_code=403)

    data = serialize_staff_trek(trek)
    return success_response("Trek details retrieved successfully", data={"trek": data, **data})


@staff_bp.route("/treks/<int:trek_id>/slots", methods=["PATCH"])
@role_required("Trek Staff")
def update_trek_slots(trek_id):
    """Update available slot capacity for an assigned trek."""
    user = g.current_user
    trek = db.session.get(Trek, trek_id)
    if not trek:
        return error_response(f"Trek with ID {trek_id} not found.", status_code=404)

    if trek.assigned_staff_id != user.id:
        return error_response("You are not authorized to access this trek.", status_code=403)

    payload = request.get_json(silent=True) or {}
    slots_val = None
    for key in ("available_slots", "slots", "total_slots", "max_participants"):
        if key in payload:
            slots_val = payload[key]
            break

    if slots_val is None:
        return error_response("available_slots field is required.", status_code=400)

    try:
        new_slots = int(slots_val)
    except (ValueError, TypeError):
        return error_response("Available slots must be a valid integer.", status_code=400)

    if new_slots < 0:
        return error_response("Available slots cannot be negative.", status_code=400)

    # Capacity guard: cannot reduce below active bookings count
    active_count = Booking.query.filter_by(trek_id=trek.id, booking_status="Booked").count()
    if new_slots < active_count:
        return error_response(
            f"Cannot reduce available slots to {new_slots}. There are already {active_count} active bookings for this trek.",
            status_code=400
        )

    trek.available_slots = new_slots
    db.session.commit()

    serialized = serialize_staff_trek(trek)
    return success_response(
        f"Available slots for trek '{trek.trek_name}' updated to {new_slots}.",
        data={"trek": serialized, **serialized}
    )


@staff_bp.route("/treks/<int:trek_id>/status", methods=["PATCH"])
@role_required("Trek Staff")
def update_trek_status(trek_id):
    """Toggle booking status (Open/Closed) for an assigned trek."""
    user = g.current_user
    trek = db.session.get(Trek, trek_id)
    if not trek:
        return error_response(f"Trek with ID {trek_id} not found.", status_code=404)

    if trek.assigned_staff_id != user.id:
        return error_response("You are not authorized to access this trek.", status_code=403)

    payload = request.get_json(silent=True) or {}
    new_status = (payload.get("status") or "").strip()

    if not new_status:
        return error_response("status field is required.", status_code=400)

    # Allowed booking statuses for staff: Open or Closed
    if new_status not in {"Open", "Closed"}:
        return error_response(
            "Staff members may only update booking status to 'Open' or 'Closed'. Administrative statuses ('Pending', 'Approved') cannot be set by staff.",
            status_code=400
        )

    # Cannot modify completed treks
    if trek.status == "Completed" or trek.operational_progress == "Completed":
        return error_response("Cannot modify booking status for a completed trek.", status_code=400)

    trek.status = new_status
    db.session.commit()

    serialized = serialize_staff_trek(trek)
    return success_response(
        f"Trek booking status updated to '{new_status}'.",
        data={"trek": serialized, **serialized}
    )


@staff_bp.route("/treks/<int:trek_id>/progress", methods=["PATCH"])
@role_required("Trek Staff")
def update_trek_progress(trek_id):
    """Update operational progress lifecycle for an assigned trek."""
    user = g.current_user
    trek = db.session.get(Trek, trek_id)
    if not trek:
        return error_response(f"Trek with ID {trek_id} not found.", status_code=404)

    if trek.assigned_staff_id != user.id:
        return error_response("You are not authorized to access this trek.", status_code=403)

    payload = request.get_json(silent=True) or {}
    new_progress = (
        payload.get("operational_progress")
        or payload.get("progress")
        or ""
    ).strip()

    if not new_progress:
        return error_response("operational_progress field is required.", status_code=400)

    if new_progress not in Trek.ALLOWED_PROGRESS_STAGES:
        return error_response(
            f"Invalid operational progress: '{new_progress}'. Allowed stages: {', '.join(sorted(Trek.ALLOWED_PROGRESS_STAGES))}",
            status_code=400
        )

    current_progress = trek.operational_progress
    if current_progress != new_progress:
        allowed_transitions = Trek.ALLOWED_PROGRESS_TRANSITIONS.get(current_progress, set())
        if new_progress not in allowed_transitions:
            trans_msg = (
                f"Allowed transitions from '{current_progress}': {', '.join(sorted(allowed_transitions))}"
                if allowed_transitions
                else "No transitions allowed from terminal stage."
            )
            return error_response(
                f"Invalid progress transition from '{current_progress}' to '{new_progress}'. {trans_msg}",
                status_code=400
            )

    trek.operational_progress = new_progress

    # When trek is Completed, automatically close booking status and transition active bookings
    if new_progress == "Completed":
        if trek.status in ("Open", "Pending", "Approved"):
            trek.status = "Closed"
        active_bookings = Booking.query.filter_by(
            trek_id=trek.id,
            booking_status="Booked"
        ).all()
        for b in active_bookings:
            b.booking_status = "Completed"

    db.session.commit()

    serialized = serialize_staff_trek(trek)
    return success_response(
        f"Trek operational progress updated to '{new_progress}'.",
        data={"trek": serialized, **serialized}
    )


@staff_bp.route("/treks/<int:trek_id>/participants", methods=["GET"])
@role_required("Trek Staff")
def get_trek_participants(trek_id):
    """Retrieve participant roster for an assigned trek."""
    user = g.current_user
    trek = db.session.get(Trek, trek_id)
    if not trek:
        return error_response(f"Trek with ID {trek_id} not found.", status_code=404)

    if trek.assigned_staff_id != user.id:
        return error_response("You are not authorized to access this trek.", status_code=403)

    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 20, type=int), 100)
    status_filter = request.args.get("status", "").strip()
    search = request.args.get("search", "").strip()

    base_query = Booking.query.filter(Booking.trek_id == trek.id)

    total_count = base_query.count()
    active_count = base_query.filter(Booking.booking_status == "Booked").count()
    cancelled_count = base_query.filter(Booking.booking_status == "Cancelled").count()
    completed_count = base_query.filter(Booking.booking_status == "Completed").count()

    query = base_query
    if status_filter and status_filter.lower() != "all":
        query = query.filter(Booking.booking_status == status_filter)

    if search:
        query = query.join(User, Booking.user_id == User.id).filter(
            or_(
                User.full_name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                User.contact_number.ilike(f"%{search}%")
            )
        )

    query = query.order_by(Booking.booking_date.desc())
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    participant_list = []
    for b in paginated.items:
        participant_user = b.user
        participant_list.append({
            "booking_id": b.id,
            "id": b.id,
            "booking_status": b.booking_status,
            "status": b.booking_status,
            "payment_status": b.payment_status,
            "booking_date": b.booking_date.isoformat() if b.booking_date else None,
            "user_id": b.user_id,
            "participant": {
                "id": participant_user.id if participant_user else None,
                "full_name": participant_user.full_name if participant_user else "Unknown User",
                "email": participant_user.email if participant_user else "",
                "contact_number": participant_user.contact_number if participant_user else None,
            },
            "user": {
                "id": participant_user.id if participant_user else None,
                "full_name": participant_user.full_name if participant_user else "Unknown User",
                "email": participant_user.email if participant_user else "",
                "contact_number": participant_user.contact_number if participant_user else None,
            }
        })

    return success_response(
        "Participant roster retrieved successfully",
        data={
            "trek": serialize_staff_trek(trek),
            "participants": participant_list,
            "summary": {
                "total": total_count,
                "active": active_count,
                "cancelled": cancelled_count,
                "completed": completed_count,
            },
            "total_participants": total_count,
            "active_count": active_count,
            "cancelled_count": cancelled_count,
            "completed_count": completed_count,
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

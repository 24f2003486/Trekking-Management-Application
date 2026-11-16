"""Admin trek management routes."""
from datetime import date
from flask import Blueprint, request
from sqlalchemy import or_, desc, asc
from backend.app.extensions import db
from backend.app.models.trek import Trek
from backend.app.models.user import User
from backend.app.utils.decorators import role_required
from backend.app.utils.responses import success_response, error_response

admin_treks_bp = Blueprint("admin_treks", __name__, url_prefix="/api/admin/treks")


@admin_treks_bp.route("", methods=["GET"])
@role_required("Admin")
def list_treks():
    """List all treks with pagination, search, filter, and sorting."""
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 10, type=int), 100)
    search = request.args.get("search", "").strip()
    difficulty = request.args.get("difficulty", "").strip()
    status = request.args.get("status", "").strip()
    location = request.args.get("location", "").strip()
    sort_by = request.args.get("sort_by", "created_at").strip()
    sort_order = request.args.get("sort_order", "desc").strip().lower()

    query = Trek.query

    # Search filter
    if search:
        search_filter = or_(
            Trek.trek_name.ilike(f"%{search}%"),
            Trek.location.ilike(f"%{search}%")
        )
        if search.isdigit():
            search_filter = or_(search_filter, Trek.id == int(search))
        query = query.filter(search_filter)

    # Specific attribute filters
    if difficulty:
        query = query.filter(Trek.difficulty == difficulty)
    if status:
        query = query.filter(Trek.status == status)
    if location:
        query = query.filter(Trek.location.ilike(f"%{location}%"))

    # Sorting
    sort_column = getattr(Trek, sort_by, Trek.created_at)
    order_func = asc if sort_order == "asc" else desc
    query = query.order_by(order_func(sort_column))

    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    return success_response(
        "Treks retrieved successfully",
        data={
            "treks": [trek.to_dict() for trek in paginated.items],
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


@admin_treks_bp.route("/<int:trek_id>", methods=["GET"])
@role_required("Admin")
def get_trek(trek_id):
    """Retrieve details of a single trek."""
    trek = db.session.get(Trek, trek_id)
    if not trek:
        return error_response(f"Trek with ID {trek_id} not found.", status_code=404)
    trek_dict = trek.to_dict()
    return success_response("Trek details retrieved successfully", data={"trek": trek_dict, **trek_dict})


@admin_treks_bp.route("", methods=["POST"])
@role_required("Admin")
def create_trek():
    """Create a new trek route."""
    data = request.get_json(silent=True) or {}
    
    trek_name = (data.get("trek_name") or data.get("name") or "").strip()
    location = data.get("location", "").strip()
    description = data.get("description", "").strip() if data.get("description") else None
    difficulty = data.get("difficulty", "").strip()
    if difficulty.capitalize() == "Difficult":
        difficulty = "Hard"
    duration_days = data.get("duration_days")
    available_slots = data.get("available_slots") if "available_slots" in data else data.get("max_participants")
    start_date_str = data.get("start_date")
    end_date_str = data.get("end_date")
    assigned_staff_id = data.get("assigned_staff_id")
    status = data.get("status", "Pending").strip()

    # Field validations
    errors = {}
    if not trek_name:
        errors["trek_name"] = "Trek name is required."
    if not location:
        errors["location"] = "Location is required."
    if not difficulty or difficulty not in Trek.ALLOWED_DIFFICULTIES:
        errors["difficulty"] = f"Difficulty must be one of: {', '.join(sorted(Trek.ALLOWED_DIFFICULTIES))}."
    
    try:
        duration_days = int(duration_days)
        if duration_days <= 0:
            errors["duration_days"] = "Duration in days must be greater than zero."
    except (TypeError, ValueError):
        errors["duration_days"] = "Duration in days must be a valid positive integer."

    try:
        available_slots = int(available_slots)
        if available_slots < 0:
            errors["available_slots"] = "Available slots cannot be negative."
    except (TypeError, ValueError):
        errors["available_slots"] = "Available slots must be a non-negative integer."

    # Parse and validate dates
    start_date = None
    end_date = None
    try:
        if not start_date_str:
            errors["start_date"] = "Start date is required."
        else:
            start_date = date.fromisoformat(str(start_date_str))
    except ValueError:
        errors["start_date"] = "Start date must be in YYYY-MM-DD format."

    try:
        if not end_date_str:
            errors["end_date"] = "End date is required."
        else:
            end_date = date.fromisoformat(str(end_date_str))
    except ValueError:
        errors["end_date"] = "End date must be in YYYY-MM-DD format."

    if start_date and end_date and end_date < start_date:
        errors["end_date"] = "End date cannot precede start date."

    if status not in Trek.ALLOWED_STATUSES:
        errors["status"] = f"Status must be one of: {', '.join(sorted(Trek.ALLOWED_STATUSES))}."

    # Validate staff assignment if provided
    staff_user = None
    if assigned_staff_id is not None and assigned_staff_id != "":
        try:
            assigned_staff_id = int(assigned_staff_id)
            staff_user = db.session.get(User, assigned_staff_id)
            if not staff_user:
                errors["assigned_staff_id"] = f"Staff user with ID {assigned_staff_id} does not exist."
            elif staff_user.role != "Trek Staff":
                errors["assigned_staff_id"] = f"User '{staff_user.full_name}' is not a Trek Staff (Role: {staff_user.role})."
            elif staff_user.status != "Active":
                errors["assigned_staff_id"] = f"Staff user '{staff_user.full_name}' is not Active (Status: {staff_user.status})."
        except (TypeError, ValueError):
            errors["assigned_staff_id"] = "Assigned staff ID must be an integer."
    else:
        assigned_staff_id = None

    if errors:
        return error_response("Validation failed.", errors=errors, status_code=400)

    try:
        new_trek = Trek(
            trek_name=trek_name,
            location=location,
            description=description,
            difficulty=difficulty,
            duration_days=duration_days,
            available_slots=available_slots,
            start_date=start_date,
            end_date=end_date,
            assigned_staff_id=assigned_staff_id,
            status=status
        )
        db.session.add(new_trek)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return error_response(f"Failed to create trek: {str(e)}", status_code=400)

    new_trek_dict = new_trek.to_dict()
    return success_response(
        "Trek created successfully",
        data={"trek": new_trek_dict, **new_trek_dict},
        status_code=201
    )


@admin_treks_bp.route("/<int:trek_id>", methods=["PUT"])
@role_required("Admin")
def update_trek(trek_id):
    """Update details of an existing trek."""
    trek = db.session.get(Trek, trek_id)
    if not trek:
        return error_response(f"Trek with ID {trek_id} not found.", status_code=404)

    data = request.get_json(silent=True) or {}
    errors = {}

    if "trek_name" in data or "name" in data:
        name = (data.get("trek_name") or data.get("name") or "").strip()
        if not name:
            errors["trek_name"] = "Trek name cannot be empty."
        else:
            trek.trek_name = name

    if "location" in data:
        loc = data["location"].strip()
        if not loc:
            errors["location"] = "Location cannot be empty."
        else:
            trek.location = loc

    if "description" in data:
        trek.description = data["description"].strip() if data["description"] else None

    if "difficulty" in data:
        diff = data["difficulty"].strip()
        if diff.capitalize() == "Difficult":
            diff = "Hard"
        if diff not in Trek.ALLOWED_DIFFICULTIES:
            errors["difficulty"] = f"Difficulty must be one of: {', '.join(sorted(Trek.ALLOWED_DIFFICULTIES))}."
        else:
            trek.difficulty = diff

    if "duration_days" in data:
        try:
            dur = int(data["duration_days"])
            if dur <= 0:
                errors["duration_days"] = "Duration must be greater than zero."
            else:
                trek.duration_days = dur
        except (TypeError, ValueError):
            errors["duration_days"] = "Duration must be a positive integer."

    if "available_slots" in data:
        try:
            slots = int(data["available_slots"])
            if slots < 0:
                errors["available_slots"] = "Available slots cannot be negative."
            else:
                trek.available_slots = slots
        except (TypeError, ValueError):
            errors["available_slots"] = "Available slots must be a non-negative integer."

    if "status" in data:
        stat = data["status"].strip()
        if stat not in Trek.ALLOWED_STATUSES:
            errors["status"] = f"Status must be one of: {', '.join(sorted(Trek.ALLOWED_STATUSES))}."
        else:
            trek.status = stat

    # Handle dates
    new_start_date = trek.start_date
    new_end_date = trek.end_date
    if "start_date" in data:
        try:
            new_start_date = date.fromisoformat(str(data["start_date"]))
        except ValueError:
            errors["start_date"] = "Start date must be in YYYY-MM-DD format."

    if "end_date" in data:
        try:
            new_end_date = date.fromisoformat(str(data["end_date"]))
        except ValueError:
            errors["end_date"] = "End date must be in YYYY-MM-DD format."

    if new_start_date and new_end_date and new_end_date < new_start_date:
        errors["end_date"] = "End date cannot precede start date."
    elif "start_date" in data or "end_date" in data:
        trek.set_dates(new_start_date, new_end_date)

    # Handle staff assignment
    if "assigned_staff_id" in data:
        staff_id = data["assigned_staff_id"]
        if staff_id is None or staff_id == "":
            trek.assigned_staff_id = None
        else:
            try:
                staff_id = int(staff_id)
                staff_user = db.session.get(User, staff_id)
                if not staff_user:
                    errors["assigned_staff_id"] = f"Staff user with ID {staff_id} does not exist."
                elif staff_user.role != "Trek Staff":
                    errors["assigned_staff_id"] = f"User '{staff_user.full_name}' is not a Trek Staff."
                elif staff_user.status != "Active":
                    errors["assigned_staff_id"] = f"Staff user '{staff_user.full_name}' is not Active."
                else:
                    trek.assigned_staff_id = staff_id
            except (TypeError, ValueError):
                errors["assigned_staff_id"] = "Assigned staff ID must be an integer."

    if errors:
        return error_response("Validation failed.", errors=errors, status_code=400)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return error_response(f"Failed to update trek: {str(e)}", status_code=400)

    trek_dict = trek.to_dict()
    return success_response(
        "Trek updated successfully",
        data={"trek": trek_dict, **trek_dict}
    )


@admin_treks_bp.route("/<int:trek_id>", methods=["DELETE"])
@role_required("Admin")
def delete_trek(trek_id):
    """
    Safely delete a trek.
    Strictly prevents deletion if historical booking records exist to preserve audit history.
    """
    trek = db.session.get(Trek, trek_id)
    if not trek:
        return error_response(f"Trek with ID {trek_id} not found.", status_code=404)

    bookings_count = trek.bookings.count()
    if bookings_count > 0:
        return error_response(
            f"Cannot delete trek '{trek.trek_name}' because it has {bookings_count} existing booking record(s). "
            "To remove this trek from public availability while preserving booking history, update its status to 'Closed' or 'Completed'.",
            status_code=400
        )

    try:
        db.session.delete(trek)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return error_response(f"Failed to delete trek: {str(e)}", status_code=500)

    return success_response(f"Trek '{trek.trek_name}' deleted successfully.")


@admin_treks_bp.route("/<int:trek_id>/assign-staff", methods=["PUT"])
@role_required("Admin")
def assign_staff_to_trek(trek_id):
    """Assign or reassign an active Trek Staff member to a trek."""
    trek = db.session.get(Trek, trek_id)
    if not trek:
        return error_response(f"Trek with ID {trek_id} not found.", status_code=404)

    data = request.get_json(silent=True) or {}
    staff_id = data.get("staff_id") if "staff_id" in data else data.get("assigned_staff_id")

    if staff_id is None or staff_id == "":
        trek.assigned_staff_id = None
        db.session.commit()
        trek_dict = trek.to_dict()
        return success_response(
            "Staff assignment removed successfully",
            data={"trek": trek_dict, **trek_dict}
        )

    try:
        staff_id = int(staff_id)
    except (TypeError, ValueError):
        return error_response("Staff ID must be an integer.", status_code=400)

    staff_user = db.session.get(User, staff_id)
    if not staff_user:
        return error_response(f"Staff account with ID {staff_id} does not exist.", status_code=404)

    if staff_user.role != "Trek Staff":
        return error_response(
            f"User '{staff_user.full_name}' cannot be assigned as trek staff because their role is '{staff_user.role}'.",
            status_code=400
        )

    if staff_user.status != "Active":
        return error_response(
            f"Staff user '{staff_user.full_name}' cannot be assigned because their account status is '{staff_user.status}'.",
            status_code=400
        )

    trek.assigned_staff_id = staff_id
    db.session.commit()

    trek_dict = trek.to_dict()
    return success_response(
        f"Staff '{staff_user.full_name}' assigned to trek '{trek.trek_name}' successfully",
        data={"trek": trek_dict, **trek_dict}
    )

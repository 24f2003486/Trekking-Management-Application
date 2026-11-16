"""Admin trek staff management routes."""
import re
from flask import Blueprint, request
from sqlalchemy import or_
from backend.app.extensions import db
from backend.app.models.user import User
from backend.app.models.staff_profile import StaffProfile
from backend.app.utils.decorators import role_required
from backend.app.utils.responses import success_response, error_response

admin_staff_bp = Blueprint("admin_staff", __name__, url_prefix="/api/admin/staff")
EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")


@admin_staff_bp.route("", methods=["GET"])
@role_required("Admin")
def list_staff():
    """List Trek Staff accounts with pagination, search, and status filter."""
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 10, type=int), 100)
    search = request.args.get("search", "").strip()
    status = request.args.get("status", "").strip()

    query = User.query.filter_by(role="Trek Staff")

    if search:
        search_filter = or_(
            User.full_name.ilike(f"%{search}%"),
            User.email.ilike(f"%{search}%")
        )
        if search.isdigit():
            search_filter = or_(search_filter, User.id == int(search))
        query = query.filter(search_filter)

    if status:
        query = query.filter(User.status == status)

    query = query.order_by(User.id.desc())
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    return success_response(
        "Staff accounts retrieved successfully",
        data={
            "staff": [user.to_dict() for user in paginated.items],
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


@admin_staff_bp.route("/available", methods=["GET"])
@role_required("Admin")
def list_available_staff():
    """List active Trek Staff members for dropdown selection in trek forms."""
    staff_members = User.query.filter_by(role="Trek Staff", status="Active").order_by(User.full_name.asc()).all()
    return success_response(
        "Available staff retrieved successfully",
        data={"staff": [s.to_dict() for s in staff_members]}
    )


@admin_staff_bp.route("/<int:staff_id>", methods=["GET"])
@role_required("Admin")
def get_staff_member(staff_id):
    """Retrieve details of a single staff member."""
    staff = db.session.get(User, staff_id)
    if not staff or staff.role != "Trek Staff":
        return error_response(f"Staff account with ID {staff_id} not found.", status_code=404)
    
    data = staff.to_dict()
    data["assigned_treks"] = [t.to_dict() for t in staff.assigned_treks]
    return success_response("Staff member retrieved successfully", data={"staff": data})


@admin_staff_bp.route("", methods=["POST"])
@role_required("Admin")
def create_staff_member():
    """
    Create a new Trek Staff account and associated StaffProfile in an atomic transaction.
    """
    data = request.get_json(silent=True) or {}
    
    full_name = data.get("full_name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    contact_number = data.get("contact_number", "").strip() if data.get("contact_number") else None
    specialization = data.get("specialization", "").strip() if data.get("specialization") else None
    experience_years = data.get("experience_years", 0)
    emergency_contact = data.get("emergency_contact", "").strip() if data.get("emergency_contact") else None

    errors = {}
    if not full_name:
        errors["full_name"] = "Full name is required."
    if not email:
        errors["email"] = "Email address is required."
    elif not EMAIL_REGEX.match(email):
        errors["email"] = "Invalid email format."
    elif User.query.filter_by(email=email).first():
        return error_response("An account with this email address already exists.", status_code=409)

    if not password:
        errors["password"] = "Initial password is required."
    elif len(password) < 8:
        errors["password"] = "Initial password must be at least 8 characters."

    try:
        experience_years = int(experience_years)
        if experience_years < 0:
            errors["experience_years"] = "Experience years cannot be negative."
    except (TypeError, ValueError):
        errors["experience_years"] = "Experience years must be a valid integer."

    if errors:
        return error_response("Validation failed.", errors=errors, status_code=400)

    try:
        # Atomic creation of user and profile
        user = User(
            full_name=full_name,
            email=email,
            role="Trek Staff",
            status="Active",
            contact_number=contact_number
        )
        user.set_password(password)
        db.session.add(user)
        db.session.flush()  # Populates user.id

        profile = StaffProfile(
            user_id=user.id,
            specialization=specialization,
            experience_years=experience_years,
            emergency_contact=emergency_contact
        )
        db.session.add(profile)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return error_response(f"Failed to create staff account: {str(e)}", status_code=400)

    staff_dict = user.to_dict()
    return success_response(
        "Trek Staff account created successfully",
        data={"staff": staff_dict, **staff_dict},
        status_code=201
    )


@admin_staff_bp.route("/<int:staff_id>", methods=["PUT"])
@role_required("Admin")
def update_staff_member(staff_id):
    """Update profile and details of an existing Trek Staff member."""
    staff = db.session.get(User, staff_id)
    if not staff or staff.role != "Trek Staff":
        return error_response(f"Staff account with ID {staff_id} not found.", status_code=404)

    data = request.get_json(silent=True) or {}
    errors = {}

    if "full_name" in data:
        name = data["full_name"].strip()
        if not name:
            errors["full_name"] = "Full name cannot be empty."
        else:
            staff.full_name = name

    if "contact_number" in data:
        staff.contact_number = data["contact_number"].strip() if data["contact_number"] else None

    # Update profile fields
    profile = staff.staff_profile
    if not profile:
        profile = StaffProfile(user_id=staff.id)
        db.session.add(profile)

    if "specialization" in data:
        profile.specialization = data["specialization"].strip() if data["specialization"] else None

    if "emergency_contact" in data:
        profile.emergency_contact = data["emergency_contact"].strip() if data["emergency_contact"] else None

    if "experience_years" in data:
        try:
            exp = int(data["experience_years"])
            if exp < 0:
                errors["experience_years"] = "Experience years cannot be negative."
            else:
                profile.experience_years = exp
        except (TypeError, ValueError):
            errors["experience_years"] = "Experience years must be a valid integer."

    if errors:
        return error_response("Validation failed.", errors=errors, status_code=400)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return error_response(f"Failed to update staff member: {str(e)}", status_code=400)

    staff_dict = staff.to_dict()
    return success_response(
        "Staff member details updated successfully",
        data={"staff": staff_dict, **staff_dict}
    )


@admin_staff_bp.route("/<int:staff_id>/status", methods=["PATCH"])
@role_required("Admin")
def update_staff_status(staff_id):
    """Update account status of a staff member (Active, Inactive, Blacklisted)."""
    staff = db.session.get(User, staff_id)
    if not staff or staff.role != "Trek Staff":
        return error_response(f"Staff account with ID {staff_id} not found.", status_code=404)

    data = request.get_json(silent=True) or {}
    new_status = data.get("status", "").strip()

    if new_status not in User.ALLOWED_STATUSES:
        return error_response(
            f"Invalid status '{new_status}'. Allowed values: {', '.join(sorted(User.ALLOWED_STATUSES))}.",
            status_code=400
        )

    staff.status = new_status
    db.session.commit()

    staff_dict = staff.to_dict()
    return success_response(
        f"Staff status updated to '{new_status}' successfully",
        data={"staff": staff_dict, **staff_dict}
    )

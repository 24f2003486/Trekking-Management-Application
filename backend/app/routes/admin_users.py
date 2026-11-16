"""Admin trekker user management routes."""
from flask import Blueprint, request
from sqlalchemy import or_
from backend.app.extensions import db
from backend.app.models.user import User
from backend.app.utils.decorators import role_required
from backend.app.utils.responses import success_response, error_response

admin_users_bp = Blueprint("admin_users", __name__, url_prefix="/api/admin/users")


@admin_users_bp.route("", methods=["GET"])
@role_required("Admin")
def list_trekkers():
    """List registered Trekker accounts with pagination, search, and status filter."""
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 10, type=int), 100)
    search = request.args.get("search", "").strip()
    status = request.args.get("status", "").strip()

    query = User.query.filter_by(role="Trekker")

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
        "Trekker users retrieved successfully",
        data={
            "users": [user.to_dict() for user in paginated.items],
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


@admin_users_bp.route("/<int:user_id>", methods=["GET"])
@role_required("Admin")
def get_trekker(user_id):
    """Retrieve details of a single Trekker user."""
    user = db.session.get(User, user_id)
    if not user or user.role != "Trekker":
        return error_response(f"Trekker user with ID {user_id} not found.", status_code=404)
    return success_response("User details retrieved successfully", data={"user": user.to_dict()})


@admin_users_bp.route("/<int:user_id>", methods=["PUT"])
@role_required("Admin")
def update_trekker(user_id):
    """
    Update permitted profile details of a Trekker (name, contact number).
    Strictly forbids role changes or modifications to Admin accounts.
    """
    user = db.session.get(User, user_id)
    if not user:
        return error_response(f"User with ID {user_id} not found.", status_code=404)

    if user.role == "Admin":
        return error_response(
            "Admin accounts cannot be modified through the Trekker user management API.",
            status_code=403
        )

    data = request.get_json(silent=True) or {}

    # Strict check: reject or prevent role changes
    if "role" in data and data["role"] != user.role:
        return error_response(
            "User role cannot be modified through this endpoint.",
            status_code=400
        )

    if "full_name" in data:
        name = data["full_name"].strip()
        if not name:
            return error_response("Full name cannot be empty.", status_code=400)
        user.full_name = name

    phone = data.get("phone_number") or data.get("contact_number")
    if phone is not None:
        user.contact_number = phone.strip() if phone else None

    db.session.commit()
    user_dict = user.to_dict()
    return success_response("User profile updated successfully", data={"user": user_dict, **user_dict})


@admin_users_bp.route("/<int:user_id>/status", methods=["PATCH"])
@role_required("Admin")
def update_user_status(user_id):
    """
    Activate, deactivate, or blacklist a Trekker user.
    Takes effect immediately for subsequent requests.
    """
    user = db.session.get(User, user_id)
    if not user:
        return error_response(f"User with ID {user_id} not found.", status_code=404)

    if user.role == "Admin":
        return error_response(
            "Cannot modify the account status of an Administrator account.",
            status_code=403
        )

    data = request.get_json(silent=True) or {}
    new_status = data.get("status", "").strip()

    if new_status not in User.ALLOWED_STATUSES:
        return error_response(
            f"Invalid status '{new_status}'. Allowed values: {', '.join(sorted(User.ALLOWED_STATUSES))}.",
            status_code=400
        )

    user.status = new_status
    db.session.commit()

    user_dict = user.to_dict()
    return success_response(
        f"User status updated to '{new_status}' successfully",
        data={"user": user_dict, **user_dict}
    )

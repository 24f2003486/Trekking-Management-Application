"""Authentication routes for registration, login, logout, and current user profile."""
import re
from flask import Blueprint, request, g
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt,
    get_jwt_identity,
)
from backend.app.extensions import db
from backend.app.models.user import User
from backend.app.models.token_blocklist import TokenBlocklist
from backend.app.utils.responses import success_response, error_response
from backend.app.utils.decorators import active_user_required

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Register a new Trekker user.
    Only Trekker self-registration is permitted.
    """
    data = request.get_json(silent=True) or {}
    
    full_name = data.get("full_name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    confirm_password = data.get("confirm_password", "")
    contact_number = data.get("contact_number", "").strip() if data.get("contact_number") else None

    # 1. Validation of required fields
    errors = {}
    if not full_name:
        errors["full_name"] = "Full name is required."
    if not email:
        errors["email"] = "Email address is required."
    elif not EMAIL_REGEX.match(email):
        errors["email"] = "Invalid email format."
    if not password:
        errors["password"] = "Password is required."
    elif len(password) < 8:
        errors["password"] = "Password must be at least 8 characters in length."
    if not confirm_password:
        errors["confirm_password"] = "Confirm password is required."
    elif password != confirm_password:
        errors["confirm_password"] = "Passwords do not match."

    # Prevent role escalation
    requested_role = data.get("role")
    if requested_role and requested_role != "Trekker":
        return error_response(
            "Self-registration is strictly restricted to the 'Trekker' role. "
            "Admin and Trek Staff accounts cannot be registered publicly.",
            status_code=403
        )

    if errors:
        return error_response("Validation failed.", errors=errors, status_code=400)

    # 2. Check email uniqueness
    if User.query.filter_by(email=email).first():
        return error_response(
            "An account with this email address already exists.",
            errors={"email": "Email address already registered."},
            status_code=409
        )

    # 3. Create Trekker user (role and status strictly enforced on backend)
    try:
        user = User(
            full_name=full_name,
            email=email,
            role="Trekker",
            status="Active",
            contact_number=contact_number
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return error_response(f"Registration failed: {str(e)}", status_code=500)

    return success_response(
        "Registration successful. Please log in with your credentials.",
        data=user.to_dict(),
        status_code=201
    )


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Authenticate user and generate a JWT access token.
    Supports Admin, Trek Staff, and Trekker roles.
    """
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return error_response(
            "Email and password are required.",
            errors={
                "email": "Email is required." if not email else None,
                "password": "Password is required." if not password else None,
            },
            status_code=400
        )

    # Generic invalid credentials message for security
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return error_response("Invalid email or password.", status_code=401)

    # Check account status
    if user.status == "Inactive":
        return error_response(
            "Account is inactive. Please contact the administrator.",
            status_code=403
        )
    if user.status == "Blacklisted":
        return error_response(
            "Account is blacklisted. Access denied.",
            status_code=403
        )
    if user.status != "Active":
        return error_response(
            f"Account access denied. Account status is '{user.status}'.",
            status_code=403
        )

    # For Trek Staff, verify associated StaffProfile exists
    if user.role == "Trek Staff" and user.staff_profile is None:
        return error_response(
            "Trek Staff account setup is incomplete. An associated Staff Profile is required.",
            status_code=403
        )

    # Generate JWT access token with user ID identity and role claim
    additional_claims = {
        "role": user.role,
        "email": user.email,
        "full_name": user.full_name
    }
    access_token = create_access_token(
        identity=str(user.id),
        additional_claims=additional_claims
    )

    return success_response(
        "Login successful",
        data={
            "access_token": access_token,
            "user": {
                "id": user.id,
                "full_name": user.full_name,
                "email": user.email,
                "role": user.role,
                "status": user.status
            }
        },
        status_code=200
    )


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
@active_user_required()
def get_current_user_profile():
    """Retrieve profile of the currently authenticated user."""
    user = g.current_user
    return success_response(
        "User profile retrieved successfully",
        data={"user": user.to_dict()},
        status_code=200
    )


@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    """
    Log out the current user by placing their JWT jti into the SQLite token blocklist.
    """
    jwt_payload = get_jwt()
    jti = jwt_payload["jti"]

    existing = TokenBlocklist.query.filter_by(jti=jti).first()
    if not existing:
        revoked_token = TokenBlocklist(jti=jti)
        db.session.add(revoked_token)
        db.session.commit()

    return success_response("Successfully logged out. Token has been revoked.")


"""Authentication and Role-Based Access Control (RBAC) decorators."""
from functools import wraps
from flask import g
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from backend.app.extensions import db
from backend.app.models.user import User
from backend.app.utils.responses import error_response


def role_required(*allowed_roles):
    """
    Decorator enforcing that the request contains a valid JWT,
    the user exists and is Active, and their role is in allowed_roles.
    Returns 401 for authentication errors, and 403 for authorization errors.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # 1. Verify JWT in request header
            verify_jwt_in_request()
            
            # 2. Extract identity
            identity = get_jwt_identity()
            try:
                user_id = int(identity)
            except (ValueError, TypeError):
                return error_response("Invalid authentication token.", status_code=401)

            # 3. Fetch user from database - never trust client claims
            user = db.session.get(User, user_id)
            if not user:
                return error_response("User account not found.", status_code=401)

            # 4. Enforce Active account status
            if user.status != "Active":
                return error_response(
                    f"Account access denied. Account status is '{user.status}'.",
                    status_code=403
                )

            # 5. Verify role matches permission
            if user.role not in allowed_roles:
                return error_response(
                    f"Forbidden: You do not have permission to access this resource. Required role(s): {', '.join(allowed_roles)}.",
                    status_code=403
                )

            # Attach current_user to flask request context for convenience
            g.current_user = user
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def active_user_required():
    """
    Decorator ensuring the authenticated user exists and is Active.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            identity = get_jwt_identity()
            try:
                user_id = int(identity)
            except (ValueError, TypeError):
                return error_response("Invalid authentication token.", status_code=401)

            user = db.session.get(User, user_id)
            if not user:
                return error_response("User account not found.", status_code=401)

            if user.status != "Active":
                return error_response(
                    f"Account access denied. Account status is '{user.status}'.",
                    status_code=403
                )

            g.current_user = user
            return fn(*args, **kwargs)
        return wrapper
    return decorator


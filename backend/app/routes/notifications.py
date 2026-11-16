"""Notifications routes for viewing and managing in-app user alerts."""
from flask import Blueprint, g
from backend.app.extensions import db
from backend.app.models.notification import Notification
from backend.app.utils.decorators import active_user_required
from backend.app.utils.responses import success_response, error_response

notifications_bp = Blueprint("notifications", __name__, url_prefix="/api/notifications")


@notifications_bp.route("", methods=["GET"])
@active_user_required()
def get_notifications():
    """Retrieve all notifications for the authenticated user, newest first."""
    user = g.current_user
    notifications = (
        Notification.query.filter_by(user_id=user.id)
        .order_by(Notification.created_at.desc())
        .limit(50)
        .all()
    )
    unread_count = (
        Notification.query.filter_by(user_id=user.id, is_read=False).count()
    )

    data = {
        "notifications": [n.to_dict() for n in notifications],
        "unread_count": unread_count,
        "total_count": len(notifications),
    }
    return success_response("Notifications retrieved successfully.", data=data)


@notifications_bp.route("/<int:notification_id>/read", methods=["PATCH", "POST"])
@active_user_required()
def mark_notification_read(notification_id: int):
    """Mark a notification as read, enforcing strict user ownership."""
    user = g.current_user
    notification = db.session.get(Notification, notification_id)
    if not notification:
        return error_response(f"Notification with ID {notification_id} not found.", status_code=404)

    # Strictly isolated: cannot mark another user's notification as read
    if notification.user_id != user.id:
        return error_response("You are not authorized to access this notification.", status_code=403)

    notification.is_read = True
    db.session.commit()

    return success_response(
        f"Notification #{notification_id} marked as read.",
        data={"notification": notification.to_dict()}
    )


@notifications_bp.route("/read-all", methods=["POST", "PATCH"])
@active_user_required()
def mark_all_notifications_read():
    """Mark all unread notifications as read for the authenticated user."""
    user = g.current_user
    updated = (
        Notification.query.filter_by(user_id=user.id, is_read=False)
        .update({"is_read": True})
    )
    db.session.commit()

    return success_response(
        f"Marked {updated} notification(s) as read.",
        data={"updated_count": updated}
    )

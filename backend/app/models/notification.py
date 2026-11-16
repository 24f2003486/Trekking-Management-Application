"""Notification model for user alerts, reminders and job completion."""
from datetime import datetime
from backend.app.extensions import db


class Notification(db.Model):
    """Stores in-app notifications for users."""
    
    __tablename__ = "notifications"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False, default="general")
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationship
    user = db.relationship("User", back_populates="notifications")
    
    def to_dict(self) -> dict:
        """Serialize notification to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "message": self.message,
            "category": self.category,
            "is_read": self.is_read,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

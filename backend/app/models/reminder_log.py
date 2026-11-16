"""ReminderLog model for tracking trek reminder delivery and preventing duplicates."""
from datetime import datetime
from sqlalchemy import Index
from backend.app.extensions import db


class ReminderLog(db.Model):
    """Tracks daily trek reminders sent to trekkers to guarantee idempotency."""
    
    __tablename__ = "reminder_logs"
    
    __table_args__ = (
        Index("uq_booking_reminder_date", "booking_id", "reminder_date", unique=True),
    )
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    booking_id = db.Column(
        db.Integer,
        db.ForeignKey("bookings.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    trek_id = db.Column(
        db.Integer,
        db.ForeignKey("treks.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    reminder_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="Sent")
    channel = db.Column(db.String(30), nullable=False, default="In-App")
    error_message = db.Column(db.Text, nullable=True)
    sent_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def to_dict(self) -> dict:
        """Serialize reminder log to dictionary."""
        return {
            "id": self.id,
            "booking_id": self.booking_id,
            "user_id": self.user_id,
            "trek_id": self.trek_id,
            "reminder_date": self.reminder_date.isoformat() if self.reminder_date else None,
            "status": self.status,
            "channel": self.channel,
            "error_message": self.error_message,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
        }

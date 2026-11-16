"""Booking model for Trekking Management Application V2."""
from datetime import datetime
from sqlalchemy.orm import validates, synonym
from sqlalchemy import Index, text
from backend.app.extensions import db


class Booking(db.Model):
    """Booking model recording trek reservations by users."""
    
    __tablename__ = "bookings"
    
    ALLOWED_BOOKING_STATUSES = {"Booked", "Cancelled", "Completed"}
    ALLOWED_PAYMENT_STATUSES = {"Pending", "Paid", "Failed", "Refunded"}
    ALLOWED_STATUS_TRANSITIONS = {
        "Booked": {"Cancelled", "Completed"},
        "Cancelled": set(),
        "Completed": set()
    }
    
    __table_args__ = (
        db.CheckConstraint(
            "booking_status IN ('Booked', 'Cancelled', 'Completed')",
            name="ck_bookings_status"
        ),
        # Partial unique index enforcing no duplicate active ('Booked') reservations
        # for the same user and trek in SQLite
        Index(
            "uq_active_user_trek_booking",
            "user_id",
            "trek_id",
            unique=True,
            sqlite_where=text("booking_status = 'Booked'")
        ),
    )
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False
    )
    trek_id = db.Column(
        db.Integer,
        db.ForeignKey("treks.id", ondelete="RESTRICT"),
        nullable=False
    )
    booking_date = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )
    booking_status = db.Column(
        db.String(20),
        nullable=False,
        default="Booked"
    )
    status = synonym("booking_status")
    payment_status = db.Column(
        db.String(20),
        nullable=True,
        default="Pending"
    )
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    # Relationships
    user = db.relationship("User", back_populates="bookings")
    trek = db.relationship("Trek", back_populates="bookings")
    
    @validates("booking_status")
    def validate_booking_status(self, key, value):
        """Validate booking status and enforce allowed state transitions."""
        if value not in self.ALLOWED_BOOKING_STATUSES:
            raise ValueError(
                f"Invalid booking status: {value}. Allowed values: {', '.join(sorted(self.ALLOWED_BOOKING_STATUSES))}"
            )
        current = getattr(self, "booking_status", None)
        if current is not None and current != value:
            allowed = self.ALLOWED_STATUS_TRANSITIONS.get(current, set())
            if value not in allowed:
                raise ValueError(
                    f"Invalid booking status transition from '{current}' to '{value}'. "
                    f"Completed and Cancelled booking records cannot be reverted or altered."
                )
        return value

    @validates("payment_status")
    def validate_payment_status(self, key, value):
        """Validate payment status if provided."""
        if value is not None and value not in self.ALLOWED_PAYMENT_STATUSES:
            raise ValueError(
                f"Invalid payment status: {value}. Allowed values: {', '.join(sorted(self.ALLOWED_PAYMENT_STATUSES))}"
            )
        return value

    def to_dict(self) -> dict:
        """Sanitized dictionary representation of Booking including trek completion metadata."""
        trek_obj = self.trek
        user_obj = self.user
        is_completed = (
            (trek_obj.status == "Completed" or trek_obj.operational_progress == "Completed")
            if trek_obj else False
        )
        return {
            "id": self.id,
            "booking_id": self.id,
            "user_id": self.user_id,
            "trek_id": self.trek_id,
            "user": {
                "id": user_obj.id,
                "full_name": user_obj.full_name,
                "email": user_obj.email,
                "contact_number": user_obj.contact_number,
                "phone_number": user_obj.contact_number,
            } if user_obj else None,
            "trek": {
                "id": trek_obj.id,
                "name": trek_obj.trek_name,
                "trek_name": trek_obj.trek_name,
                "location": trek_obj.location,
                "difficulty": trek_obj.difficulty,
                "duration_days": trek_obj.duration_days,
                "status": trek_obj.status,
                "operational_progress": trek_obj.operational_progress,
                "progress": trek_obj.operational_progress,
                "start_date": trek_obj.start_date.isoformat() if trek_obj.start_date else None,
                "end_date": trek_obj.end_date.isoformat() if trek_obj.end_date else None,
                "assigned_staff_id": trek_obj.assigned_staff_id,
                "assigned_staff_name": trek_obj.assigned_staff.full_name if trek_obj.assigned_staff else None,
                "is_completed": is_completed,
            } if trek_obj else None,
            "user_name": user_obj.full_name if user_obj else None,
            "user_email": user_obj.email if user_obj else None,
            "trek_name": trek_obj.trek_name if trek_obj else None,
            "trek_location": trek_obj.location if trek_obj else None,
            "trek_status": trek_obj.status if trek_obj else None,
            "trek_operational_progress": trek_obj.operational_progress if trek_obj else None,
            "trek_start_date": trek_obj.start_date.isoformat() if trek_obj and trek_obj.start_date else None,
            "trek_end_date": trek_obj.end_date.isoformat() if trek_obj and trek_obj.end_date else None,
            "is_trek_completed": is_completed,
            "booking_date": self.booking_date.isoformat() if self.booking_date else None,
            "booking_status": self.booking_status,
            "status": self.booking_status,
            "payment_status": self.payment_status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:
        return f"<Booking id={self.id} user_id={self.user_id} trek_id={self.trek_id} status='{self.booking_status}'>"


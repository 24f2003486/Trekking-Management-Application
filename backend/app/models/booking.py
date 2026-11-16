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
        """Validate booking status."""
        if value not in self.ALLOWED_BOOKING_STATUSES:
            raise ValueError(
                f"Invalid booking status: {value}. Allowed values: {', '.join(sorted(self.ALLOWED_BOOKING_STATUSES))}"
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
        """Sanitized dictionary representation of Booking."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "trek_id": self.trek_id,
            "user": {
                "id": self.user.id,
                "full_name": self.user.full_name,
                "email": self.user.email,
                "contact_number": self.user.contact_number,
                "phone_number": self.user.contact_number,
            } if self.user else None,
            "trek": {
                "id": self.trek.id,
                "name": self.trek.trek_name,
                "trek_name": self.trek.trek_name,
                "location": self.trek.location,
                "difficulty": self.trek.difficulty,
                "duration_days": self.trek.duration_days,
            } if self.trek else None,
            "user_name": self.user.full_name if self.user else None,
            "user_email": self.user.email if self.user else None,
            "trek_name": self.trek.trek_name if self.trek else None,
            "trek_location": self.trek.location if self.trek else None,
            "booking_date": self.booking_date.isoformat() if self.booking_date else None,
            "booking_status": self.booking_status,
            "status": self.booking_status,
            "payment_status": self.payment_status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:
        return f"<Booking id={self.id} user_id={self.user_id} trek_id={self.trek_id} status='{self.booking_status}'>"


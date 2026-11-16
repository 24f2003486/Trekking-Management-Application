"""Trek model for Trekking Management Application V2."""
from datetime import datetime, date
from sqlalchemy import event
from sqlalchemy.orm import validates, object_session, synonym
from backend.app.extensions import db


class Trek(db.Model):
    """Trek route and expedition model."""
    
    __tablename__ = "treks"
    
    ALLOWED_DIFFICULTIES = {"Easy", "Moderate", "Hard"}
    ALLOWED_STATUSES = {"Pending", "Approved", "Open", "Closed", "Completed"}
    
    __table_args__ = (
        db.CheckConstraint(
            "difficulty IN ('Easy', 'Moderate', 'Hard')",
            name="ck_treks_difficulty"
        ),
        db.CheckConstraint(
            "status IN ('Pending', 'Approved', 'Open', 'Closed', 'Completed')",
            name="ck_treks_status"
        ),
        db.CheckConstraint(
            "duration_days > 0",
            name="ck_treks_duration_positive"
        ),
        db.CheckConstraint(
            "available_slots >= 0",
            name="ck_treks_slots_non_negative"
        ),
        db.CheckConstraint(
            "end_date >= start_date",
            name="ck_treks_date_order"
        ),
    )
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    trek_name = db.Column(db.String(100), nullable=False)
    name = synonym("trek_name")
    location = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    difficulty = db.Column(db.String(20), nullable=False)
    duration_days = db.Column(db.Integer, nullable=False)
    available_slots = db.Column(db.Integer, nullable=False)
    assigned_staff_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    status = db.Column(db.String(20), nullable=False, default="Pending")
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    # Relationships
    # Assigned staff member (User with role 'Trek Staff')
    assigned_staff = db.relationship(
        "User",
        back_populates="assigned_treks",
        foreign_keys=[assigned_staff_id]
    )
    
    # One-to-Many with Booking
    bookings = db.relationship(
        "Booking",
        back_populates="trek",
        lazy="dynamic"
    )
    
    @validates("difficulty")
    def validate_difficulty(self, key, value):
        """Validate trek difficulty."""
        if value not in self.ALLOWED_DIFFICULTIES:
            raise ValueError(
                f"Invalid difficulty: {value}. Allowed values: {', '.join(sorted(self.ALLOWED_DIFFICULTIES))}"
            )
        return value

    @validates("status")
    def validate_status(self, key, value):
        """Validate trek status."""
        if value not in self.ALLOWED_STATUSES:
            raise ValueError(
                f"Invalid status: {value}. Allowed values: {', '.join(sorted(self.ALLOWED_STATUSES))}"
            )
        return value

    @validates("duration_days")
    def validate_duration_days(self, key, value):
        """Ensure duration is strictly positive."""
        if value is None or value <= 0:
            raise ValueError("Trek duration must be a positive integer greater than zero.")
        return value

    @validates("available_slots")
    def validate_available_slots(self, key, value):
        """Ensure available slots cannot be negative."""
        if value is None or value < 0:
            raise ValueError("Available slots cannot be negative.")
        return value

    @validates("assigned_staff")
    def validate_assigned_staff_attribute(self, key, staff):
        """Validate assigned staff role on direct relationship assignment."""
        if staff is not None and staff.role != "Trek Staff":
            raise ValueError(
                f"Assigned staff must have the 'Trek Staff' role. Assigned user has role: '{staff.role}'."
            )
        return staff

    def set_dates(self, start_date: date, end_date: date) -> None:
        """Set both dates simultaneously with validation."""
        if start_date and end_date and end_date < start_date:
            raise ValueError(f"End date ({end_date}) must not precede start date ({start_date}).")
        self.start_date = start_date
        self.end_date = end_date

    def validate_dates(self):
        """Validate that end date does not precede start date."""
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValueError(
                f"End date ({self.end_date}) must not precede start date ({self.start_date})."
            )

    def validate_assigned_staff(self, session=None):
        """Ensure assigned staff member has the 'Trek Staff' role."""
        staff = self.assigned_staff
        if staff is None and self.assigned_staff_id is not None:
            from backend.app.models.user import User
            if session is not None:
                staff = session.get(User, self.assigned_staff_id)
            else:
                staff = db.session.get(User, self.assigned_staff_id)
        if staff and staff.role != "Trek Staff":
            raise ValueError(
                f"Assigned staff must have the 'Trek Staff' role. Assigned user has role: '{staff.role}'."
            )

    def to_dict(self) -> dict:
        """Sanitized dictionary representation of Trek."""
        assigned_name = self.assigned_staff.full_name if self.assigned_staff else None
        return {
            "id": self.id,
            "name": self.trek_name,
            "trek_name": self.trek_name,
            "location": self.location,
            "description": self.description,
            "difficulty": self.difficulty,
            "duration_days": self.duration_days,
            "available_slots": self.available_slots,
            "assigned_staff_id": self.assigned_staff_id,
            "assigned_staff_name": assigned_name,
            "status": self.status,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "bookings_count": self.bookings.count() if hasattr(self, "bookings") and self.bookings else 0
        }

    def __repr__(self) -> str:
        return f"<Trek id={self.id} trek_name='{self.trek_name}' difficulty='{self.difficulty}' status='{self.status}'>"


@event.listens_for(Trek, "before_insert")
@event.listens_for(Trek, "before_update")
def validate_trek_entity(mapper, connection, target):
    """Ensure dates and assigned staff are valid before persisting."""
    session = object_session(target)
    target.validate_dates()
    target.validate_assigned_staff(session=session)

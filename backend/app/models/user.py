"""User model for Trekking Management Application V2."""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import event
from sqlalchemy.orm import validates, synonym
from backend.app.extensions import db


class User(db.Model):
    """User account model supporting Admin, Trek Staff, and Trekker roles."""
    
    __tablename__ = "users"
    
    ALLOWED_ROLES = {"Admin", "Trek Staff", "Trekker"}
    ALLOWED_STATUSES = {"Active", "Inactive", "Blacklisted"}
    
    __table_args__ = (
        db.CheckConstraint(
            "role IN ('Admin', 'Trek Staff', 'Trekker')",
            name="ck_users_role"
        ),
        db.CheckConstraint(
            "status IN ('Active', 'Inactive', 'Blacklisted')",
            name="ck_users_status"
        ),
    )
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    contact_number = db.Column(db.String(20), nullable=True)
    phone_number = synonym("contact_number")
    role = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="Active")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    # Relationships
    # One-to-One with StaffProfile (only for Trek Staff)
    staff_profile = db.relationship(
        "StaffProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )
    
    # One-to-Many with Trek (as assigned trek staff)
    assigned_treks = db.relationship(
        "Trek",
        back_populates="assigned_staff",
        foreign_keys="Trek.assigned_staff_id",
        lazy="dynamic"
    )
    
    # One-to-Many with Booking (do not cascade delete bookings to preserve history)
    bookings = db.relationship(
        "Booking",
        back_populates="user",
        lazy="dynamic"
    )
    
    def set_password(self, password: str) -> None:
        """Hash and store the given password."""
        if not password:
            raise ValueError("Password cannot be empty.")
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password: str) -> bool:
        """Verify the given password against the stored hash."""
        if not self.password_hash or not password:
            return False
        return check_password_hash(self.password_hash, password)
        
    @validates("role")
    def validate_role(self, key, value):
        """Ensure role is within the allowed set."""
        if value not in self.ALLOWED_ROLES:
            raise ValueError(
                f"Invalid role: {value}. Allowed roles: {', '.join(sorted(self.ALLOWED_ROLES))}"
            )
        return value

    @validates("status")
    def validate_status(self, key, value):
        """Ensure status is within the allowed set."""
        if value not in self.ALLOWED_STATUSES:
            raise ValueError(
                f"Invalid status: {value}. Allowed statuses: {', '.join(sorted(self.ALLOWED_STATUSES))}"
            )
        return value

    @validates("email")
    def validate_email(self, key, value):
        """Basic email format validation."""
        if not value or "@" not in value or "." not in value.split("@")[-1]:
            raise ValueError("Invalid email format.")
        return value.strip().lower()

    @property
    def is_admin(self) -> bool:
        return self.role == "Admin"

    @property
    def is_staff(self) -> bool:
        return self.role == "Trek Staff"

    @property
    def is_trekker(self) -> bool:
        return self.role == "Trekker"

    def to_dict(self) -> dict:
        """Sanitized dictionary representation of user (no password_hash)."""
        data = {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "role": self.role,
            "status": self.status,
            "contact_number": self.contact_number,
            "phone_number": self.contact_number,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if self.role == "Trek Staff":
            data["staff_profile"] = self.staff_profile.to_dict() if self.staff_profile else None
            data["specialization"] = self.staff_profile.specialization if self.staff_profile else None
            data["experience_years"] = self.staff_profile.experience_years if self.staff_profile else 0
            data["emergency_contact"] = self.staff_profile.emergency_contact if self.staff_profile else None
            data["assigned_treks_count"] = self.assigned_treks.count() if hasattr(self, "assigned_treks") and self.assigned_treks else 0
        elif self.role == "Trekker":
            data["bookings_count"] = self.bookings.count() if hasattr(self, "bookings") and self.bookings else 0
        return data

    def __repr__(self) -> str:
        return f"<User id={self.id} email='{self.email}' role='{self.role}' status='{self.status}'>"


@event.listens_for(User, "before_update")
def validate_user_role_transition(mapper, connection, target):
    """Ensure that non-Trek-Staff users cannot retain staff profiles or assigned treks."""
    from sqlalchemy.orm import object_session
    session = object_session(target)
    
    if target.role != "Trek Staff":
        from backend.app.models.staff_profile import StaffProfile
        from backend.app.models.trek import Trek
        
        # Check for existing staff profile
        profile = target.staff_profile
        if profile is None and session is not None and target.id is not None:
            profile = session.query(StaffProfile).filter_by(user_id=target.id).first()
            
        if profile is not None:
            raise ValueError(
                f"Cannot assign role '{target.role}' to user '{target.email}' "
                "while an associated StaffProfile exists. Delete or dissociate the staff profile first."
            )
            
        # Check for assigned treks
        assigned_count = 0
        if session is not None and target.id is not None:
            assigned_count = session.query(Trek).filter_by(assigned_staff_id=target.id).count()
        elif target.assigned_treks is not None:
            assigned_count = target.assigned_treks.count()
            
        if assigned_count > 0:
            raise ValueError(
                f"Cannot assign role '{target.role}' to user '{target.email}' "
                f"while assigned to {assigned_count} trek(s). Reassign or unassign all treks first."
            )

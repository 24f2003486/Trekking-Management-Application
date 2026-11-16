"""StaffProfile model for Trekking Management Application V2."""
from datetime import datetime
from sqlalchemy import event
from sqlalchemy.orm import validates, object_session
from backend.app.extensions import db


class StaffProfile(db.Model):
    """Staff profile for Trek Staff users."""
    
    __tablename__ = "staff_profiles"
    
    __table_args__ = (
        db.CheckConstraint(
            "experience_years >= 0",
            name="ck_staff_profiles_experience_years"
        ),
    )
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True
    )
    specialization = db.Column(db.String(100), nullable=True)
    experience_years = db.Column(db.Integer, nullable=False, default=0)
    emergency_contact = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    # One-to-One relationship with User
    user = db.relationship(
        "User",
        back_populates="staff_profile"
    )
    
    @validates("experience_years")
    def validate_experience_years(self, key, value):
        """Ensure experience years is non-negative."""
        if value is None or value < 0:
            raise ValueError("Experience years cannot be negative.")
        return value

    @validates("user")
    def validate_user_attribute(self, key, user):
        """Validate user role on direct relationship assignment."""
        if user is not None and user.role != "Trek Staff":
            raise ValueError(
                f"Staff profile can only belong to a user with role 'Trek Staff'. Provided user role: '{user.role}'."
            )
        return user

    def validate_user_role(self, session=None):
        """Ensure the associated user has the 'Trek Staff' role."""
        user = self.user
        if user is None and self.user_id is not None:
            from backend.app.models.user import User
            if session is not None:
                user = session.get(User, self.user_id)
            else:
                user = db.session.get(User, self.user_id)
        if user and user.role != "Trek Staff":
            raise ValueError(
                f"Staff profile can only belong to a user with role 'Trek Staff'. Provided user role: '{user.role}'."
            )

    def __repr__(self) -> str:
        return f"<StaffProfile id={self.id} user_id={self.user_id} experience_years={self.experience_years}>"


@event.listens_for(StaffProfile, "before_insert")
@event.listens_for(StaffProfile, "before_update")
def validate_staff_profile_user_role(mapper, connection, target):
    """Ensure associated user is a Trek Staff before persisting."""
    session = object_session(target)
    target.validate_user_role(session=session)

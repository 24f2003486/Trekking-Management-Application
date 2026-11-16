"""ExportJob model for tracking asynchronous CSV exports of trekker history."""
from datetime import datetime
from backend.app.extensions import db


class ExportJob(db.Model):
    """Tracks asynchronous CSV export requests and their status."""
    
    __tablename__ = "export_jobs"
    
    ALLOWED_STATUSES = {"Pending", "Processing", "Completed", "Failed"}
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    filename = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), nullable=False, default="Pending")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    
    # Relationship
    user = db.relationship("User", back_populates="export_jobs")
    
    def to_dict(self) -> dict:
        """Serialize export job to dictionary."""
        return {
            "id": self.id,
            "job_id": self.id,
            "user_id": self.user_id,
            "filename": self.filename,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error_message": self.error_message,
        }

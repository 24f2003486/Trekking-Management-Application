"""MonthlyReport model for tracking generated admin activity reports."""
from datetime import datetime
from backend.app.extensions import db


class MonthlyReport(db.Model):
    """Tracks generated monthly executive and operational activity reports."""
    
    __tablename__ = "monthly_reports"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    report_month = db.Column(db.String(7), nullable=False, index=True)  # Format: "YYYY-MM"
    filename = db.Column(db.String(255), nullable=False)
    file_format = db.Column(db.String(10), nullable=False, default="html")
    status = db.Column(db.String(20), nullable=False, default="Generated")  # Generated, Failed
    total_treks = db.Column(db.Integer, nullable=False, default=0)
    total_participants = db.Column(db.Integer, nullable=False, default=0)
    total_bookings = db.Column(db.Integer, nullable=False, default=0)
    popular_treks_summary = db.Column(db.Text, nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    generated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def to_dict(self) -> dict:
        """Serialize monthly report to dictionary."""
        return {
            "id": self.id,
            "report_month": self.report_month,
            "filename": self.filename,
            "file_format": self.file_format,
            "status": self.status,
            "total_treks": self.total_treks,
            "total_participants": self.total_participants,
            "total_bookings": self.total_bookings,
            "popular_treks_summary": self.popular_treks_summary,
            "error_message": self.error_message,
            "generated_at": self.generated_at.isoformat() if self.generated_at else None,
        }

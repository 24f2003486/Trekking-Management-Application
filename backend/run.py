"""Development application entry point for Trekking Management Application V2."""
import os
import sys
from pathlib import Path

# Ensure project root and backend directory are in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = Path(__file__).resolve().parent

for p in (PROJECT_ROOT, BACKEND_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from backend.app import create_app
from backend.app.extensions import db
from backend.app.models import (
    User,
    Trek,
    Booking,
    StaffProfile,
    TokenBlocklist,
    Notification,
    ReminderLog,
    MonthlyReport,
    ExportJob,
)

app = create_app(os.environ.get("FLASK_CONFIG", "development"))


@app.shell_context_processor
def make_shell_context():
    """Add database instance and models to flask shell context."""
    return {
        "db": db,
        "User": User,
        "Trek": Trek,
        "Booking": Booking,
        "StaffProfile": StaffProfile,
        "TokenBlocklist": TokenBlocklist,
        "Notification": Notification,
        "ReminderLog": ReminderLog,
        "MonthlyReport": MonthlyReport,
        "ExportJob": ExportJob,
    }


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)

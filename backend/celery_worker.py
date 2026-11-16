"""Celery worker and beat entry point for Trekking Management Application V2."""
import os
import sys
from pathlib import Path

# Add project root and backend to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = Path(__file__).resolve().parent

for p in (PROJECT_ROOT, BACKEND_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from backend.app import create_app
from backend.app.celery_app import celery_init_app

flask_app = create_app(os.environ.get("FLASK_CONFIG", "development"))
celery_app = celery_init_app(flask_app)

if __name__ == "__main__":
    celery_app.start()

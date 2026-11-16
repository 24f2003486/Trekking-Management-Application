"""Celery task for asynchronous CSV export of trekker booking history."""
import csv
import logging
from datetime import datetime
from celery import shared_task
from flask import current_app
from backend.app.extensions import db
from backend.app.models.export_job import ExportJob
from backend.app.models.booking import Booking
from backend.app.models.notification import Notification

logger = logging.getLogger(__name__)


@shared_task(bind=True, name="backend.app.tasks.exports.export_trekker_history_csv")
def export_trekker_history_csv(self, job_id: int) -> dict:
    """Export the authenticated user's complete trekking and booking history as CSV.
    
    Args:
        job_id: The ID of the ExportJob record.
        
    Returns:
        Dictionary summarizing job completion.
    """
    logger.info("Starting CSV export for ExportJob #%s", job_id)
    job = db.session.get(ExportJob, job_id)
    if not job:
        logger.error("ExportJob #%s does not exist", job_id)
        return {"status": "error", "message": f"ExportJob #{job_id} not found"}

    # 1. Update job status to Processing
    job.status = "Processing"
    db.session.commit()

    try:
        # 2. Query only the authenticated user's booking history
        bookings = Booking.query.filter_by(user_id=job.user_id).order_by(
            Booking.booking_date.desc()
        ).all()

        # 3. Target export file in private instance directory
        exports_dir = current_app.config["EXPORTS_DIR"]
        exports_dir.mkdir(parents=True, exist_ok=True)
        filename = f"trekker_history_user_{job.user_id}_job_{job.id}.csv"
        file_path = exports_dir / filename

        headers = [
            "Booking ID",
            "Trek Name",
            "Location",
            "Difficulty",
            "Duration (Days)",
            "Booking Date",
            "Booking Status",
            "Trek Status",
            "Start Date",
            "End Date",
        ]

        # 4. Generate CSV file with strict quoting and utf-8 encoding
        with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            for b in bookings:
                trek = b.trek
                writer.writerow([
                    b.id,
                    trek.trek_name if trek else "N/A",
                    trek.location if trek else "N/A",
                    trek.difficulty if trek else "N/A",
                    trek.duration_days if trek else "N/A",
                    b.booking_date.strftime("%Y-%m-%d %H:%M:%S") if b.booking_date else "",
                    b.booking_status,
                    trek.status if trek else "N/A",
                    trek.start_date.isoformat() if (trek and trek.start_date) else "",
                    trek.end_date.isoformat() if (trek and trek.end_date) else "",
                ])

        # 5. Mark job Completed and record completion time
        job.filename = filename
        job.status = "Completed"
        job.completed_at = datetime.utcnow()
        job.error_message = None

        # 6. Create in-app notification for the user
        notification = Notification(
            user_id=job.user_id,
            title="Trekking History Export Ready",
            message=f"Your trekking history CSV export (Job #{job.id}) has been generated and is ready for download.",
            category="export"
        )
        db.session.add(notification)
        db.session.commit()

        logger.info("ExportJob #%s completed successfully: %s rows exported to %s", job_id, len(bookings), filename)
        return {
            "status": "success",
            "job_id": job.id,
            "filename": filename,
            "records_exported": len(bookings),
        }

    except Exception as exc:
        db.session.rollback()
        logger.error("Failed processing ExportJob #%s: %s", job_id, exc)
        try:
            job = db.session.get(ExportJob, job_id)
            if job:
                job.status = "Failed"
                job.error_message = str(exc)[:250]
                job.completed_at = datetime.utcnow()
                # Create notification alerting user of failure
                fail_notif = Notification(
                    user_id=job.user_id,
                    title="Export Generation Failed",
                    message=f"We could not generate your trekking history export (Job #{job.id}). Please try again.",
                    category="export"
                )
                db.session.add(fail_notif)
                db.session.commit()
        except Exception as rec_err:
            db.session.rollback()
            logger.error("Could not record export failure status: %s", rec_err)
        raise exc

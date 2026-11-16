"""Celery task for daily upcoming trek reminders."""
import logging
from datetime import date, timedelta
from celery import shared_task
from flask import current_app
from backend.app.extensions import db
from backend.app.models.trek import Trek
from backend.app.models.booking import Booking
from backend.app.models.notification import Notification
from backend.app.models.reminder_log import ReminderLog

logger = logging.getLogger(__name__)


@shared_task(bind=True, name="backend.app.tasks.reminders.send_daily_trek_reminders")
def send_daily_trek_reminders(self, target_date: str = None, window_days: int = None) -> dict:
    """Send daily upcoming trek reminders to active trekkers with active bookings.
    
    Args:
        target_date: Optional ISO date string (YYYY-MM-DD). Defaults to today's date.
        window_days: Optional integer days window. Defaults to app config REMINDER_WINDOW_DAYS (3).
    
    Returns:
        Dictionary summarizing execution outcome (sent, skipped, failed counts).
    """
    if target_date:
        today = date.fromisoformat(target_date) if isinstance(target_date, str) else target_date
    else:
        today = date.today()

    if window_days is None:
        window_days = current_app.config.get("REMINDER_WINDOW_DAYS", 3)

    window_end = today + timedelta(days=window_days)
    logger.info("Running daily trek reminders for date %s, window up to %s", today, window_end)

    # 1. Query upcoming treks within the notification window that are not Cancelled or Completed
    upcoming_treks = Trek.query.filter(
        Trek.start_date >= today,
        Trek.start_date <= window_end,
        Trek.status.notin_(["Cancelled", "Completed"])
    ).all()

    sent_count = 0
    skipped_count = 0
    failed_count = 0

    for trek in upcoming_treks:
        # 2. Identify active Booked reservations (exclude Cancelled or Completed)
        active_bookings = Booking.query.filter(
            Booking.trek_id == trek.id,
            Booking.booking_status == "Booked"
        ).all()

        for booking in active_bookings:
            user = booking.user
            # 3. Identify associated active Trekker accounts
            if not user or user.status != "Active":
                logger.debug("Skipping booking %s: user inactive or missing", booking.id)
                skipped_count += 1
                continue

            # 5. Avoid duplicate reminders for the same booking and reminder date
            existing_log = ReminderLog.query.filter_by(
                booking_id=booking.id,
                reminder_date=today
            ).first()

            if existing_log and existing_log.status == "Sent":
                logger.debug("Reminder already sent today for booking %s", booking.id)
                skipped_count += 1
                continue

            # 4, 6, 7. Generate reminder and record delivery status, handling errors individually
            try:
                days_until = (trek.start_date - today).days
                time_description = "today" if days_until == 0 else f"in {days_until} day{'s' if days_until > 1 else ''}"
                
                title = f"Trek Reminder: {trek.trek_name}"
                message = (
                    f"Hello {user.full_name}, your upcoming trek '{trek.trek_name}' is scheduled to begin "
                    f"{time_description} on {trek.start_date.strftime('%B %d, %Y')}. "
                    f"Location: {trek.location}. Difficulty: {trek.difficulty}. "
                    f"Please review your packing gear and itinerary!"
                )

                # In-app notification creation
                notification = Notification(
                    user_id=user.id,
                    title=title,
                    message=message,
                    category="reminder"
                )
                db.session.add(notification)

                # Record delivery log
                if existing_log:
                    existing_log.status = "Sent"
                    existing_log.error_message = None
                    existing_log.channel = "In-App"
                else:
                    reminder_log = ReminderLog(
                        booking_id=booking.id,
                        user_id=user.id,
                        trek_id=trek.id,
                        reminder_date=today,
                        status="Sent",
                        channel="In-App"
                    )
                    db.session.add(reminder_log)

                db.session.commit()
                sent_count += 1
                logger.info("Sent reminder for booking %s to user %s", booking.id, user.id)

            except Exception as exc:
                db.session.rollback()
                failed_count += 1
                logger.error("Failed sending reminder for booking %s: %s", booking.id, exc)
                try:
                    # Log failure in database
                    fail_log = ReminderLog(
                        booking_id=booking.id,
                        user_id=user.id,
                        trek_id=trek.id,
                        reminder_date=today,
                        status="Failed",
                        channel="In-App",
                        error_message=str(exc)[:250]
                    )
                    db.session.add(fail_log)
                    db.session.commit()
                except Exception as log_exc:
                    db.session.rollback()
                    logger.error("Could not record reminder failure log: %s", log_exc)

    summary = {
        "status": "success",
        "date": today.isoformat(),
        "treks_evaluated": len(upcoming_treks),
        "reminders_sent": sent_count,
        "reminders_skipped": skipped_count,
        "reminders_failed": failed_count,
    }
    logger.info("Trek reminders job finished: %s", summary)
    return summary

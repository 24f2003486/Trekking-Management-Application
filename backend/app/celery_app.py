"""Celery application factory and configuration for Trekking Management Application V2."""
import os
from celery import Celery, Task
from celery.schedules import crontab
from flask import Flask


def celery_init_app(app: Flask) -> Celery:
    """Initialize and configure a Celery application bound to Flask."""
    
    class FlaskTask(Task):
        """Celery Task subclass that ensures execution inside Flask application context."""
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    
    # Configure Celery from Flask application config
    broker_url = app.config.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
    result_backend = app.config.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
    
    celery_app.conf.update(
        broker_url=broker_url,
        result_backend=result_backend,
        broker_connection_retry_on_startup=True,
        task_always_eager=app.config.get("CELERY_TASK_ALWAYS_EAGER", False),
        task_eager_propagates=app.config.get("CELERY_TASK_EAGER_PROPAGATES", False),
        timezone=app.config.get("CELERY_TIMEZONE", "UTC"),
        enable_utc=True,
        accept_content=["json"],
        task_serializer="json",
        result_serializer="json",
        beat_schedule={
            "daily-trek-reminders": {
                "task": "backend.app.tasks.reminders.send_daily_trek_reminders",
                "schedule": crontab(hour=8, minute=0),
            },
            "monthly-admin-activity-report": {
                "task": "backend.app.tasks.reports.generate_monthly_report",
                "schedule": crontab(day_of_month=1, hour=0, minute=0),
            },
        },
    )
    
    # Import tasks to ensure registration with Celery registry
    import backend.app.tasks.reminders  # noqa: F401
    import backend.app.tasks.reports  # noqa: F401
    import backend.app.tasks.exports  # noqa: F401
    
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app

"""Admin reporting and aggregate statistics routes."""
from flask import Blueprint, request, current_app, send_from_directory
from sqlalchemy import func, desc
from backend.app.extensions import db
from backend.app.models.trek import Trek
from backend.app.models.booking import Booking
from backend.app.models.monthly_report import MonthlyReport
from backend.app.utils.decorators import role_required
from backend.app.utils.responses import success_response, error_response

admin_reports_bp = Blueprint("admin_reports", __name__, url_prefix="/api/admin/reports")


@admin_reports_bp.route("", methods=["GET"])
@role_required("Admin")
def get_reports():
    """
    Retrieve comprehensive aggregate trekking, booking, and operational statistics.
    All metrics are computed via database aggregate queries.
    """
    # 1. Total treks
    total_treks = Trek.query.count()

    # 2. Treks grouped by difficulty
    difficulty_rows = (
        db.session.query(Trek.difficulty, func.count(Trek.id))
        .group_by(Trek.difficulty)
        .all()
    )
    treks_by_difficulty = {diff: 0 for diff in Trek.ALLOWED_DIFFICULTIES}
    for diff, count in difficulty_rows:
        treks_by_difficulty[diff] = count

    # 3. Treks grouped by status
    status_rows = (
        db.session.query(Trek.status, func.count(Trek.id))
        .group_by(Trek.status)
        .all()
    )
    treks_by_status = {stat: 0 for stat in Trek.ALLOWED_STATUSES}
    for stat, count in status_rows:
        treks_by_status[stat] = count

    # 4. Bookings overview and grouping by status
    total_bookings = Booking.query.count()
    booking_status_rows = (
        db.session.query(Booking.booking_status, func.count(Booking.id))
        .group_by(Booking.booking_status)
        .all()
    )
    bookings_by_status = {stat: 0 for stat in Booking.ALLOWED_BOOKING_STATUSES}
    for stat, count in booking_status_rows:
        bookings_by_status[stat] = count

    # 5. Distinct participants
    total_participants = (
        db.session.query(func.count(func.distinct(Booking.user_id))).scalar() or 0
    )

    # 6. Popular treks based on booking count
    popular_query = (
        db.session.query(
            Trek.id,
            Trek.trek_name,
            Trek.difficulty,
            Trek.location,
            func.count(Booking.id).label("booking_count")
        )
        .outerjoin(Booking, Trek.id == Booking.trek_id)
        .group_by(Trek.id)
        .order_by(desc("booking_count"), Trek.trek_name.asc())
        .limit(10)
        .all()
    )
    popular_treks = [
        {
            "id": row.id,
            "name": row.trek_name,
            "trek_name": row.trek_name,
            "difficulty": row.difficulty,
            "location": row.location,
            "booking_count": row.booking_count
        }
        for row in popular_query
    ]

    # 7. Completed treks count
    completed_treks = Trek.query.filter_by(status="Completed").count()

    # 8. Monthly trekking activity (bookings grouped by Year-Month)
    monthly_rows = (
        db.session.query(
            func.strftime("%Y-%m", Booking.booking_date).label("month"),
            func.count(Booking.id)
        )
        .group_by("month")
        .order_by("month")
        .all()
    )
    monthly_activity = [
        {"month": month or "Unknown", "count": count}
        for month, count in monthly_rows
    ]

    report_data = {
        "total_treks": total_treks,
        "completed_treks": completed_treks,
        "treks_by_difficulty": treks_by_difficulty,
        "treks_by_status": treks_by_status,
        "total_bookings": total_bookings,
        "total_participants": total_participants,
        "bookings_by_status": bookings_by_status,
        "popular_treks": popular_treks,
        "monthly_activity": monthly_activity
    }

    return success_response(
        "Administrative reports and statistics retrieved successfully",
        data=report_data
    )


# =============================================================================
# Milestone 7: Monthly Activity Reports
# =============================================================================
@admin_reports_bp.route("/monthly", methods=["GET"])
@role_required("Admin")
def list_monthly_reports():
    """List all generated monthly activity reports, sorted by reporting month descending."""
    reports = MonthlyReport.query.order_by(MonthlyReport.report_month.desc()).all()
    return success_response(
        "Monthly reports retrieved successfully.",
        data={"reports": [r.to_dict() for r in reports]}
    )


@admin_reports_bp.route("/monthly/generate", methods=["POST"])
@role_required("Admin")
def trigger_monthly_report():
    """Trigger monthly activity report generation asynchronously via Celery task."""
    data = request.get_json(silent=True) or {}
    report_month = data.get("month")  # Optional "YYYY-MM"

    from backend.app.tasks.reports import generate_monthly_report
    task = generate_monthly_report.delay(report_month=report_month)

    return success_response(
        "Monthly activity report generation initiated.",
        data={"task_id": task.id, "report_month": report_month},
        status_code=202
    )


@admin_reports_bp.route("/monthly/<int:report_id>/download", methods=["GET"])
@role_required("Admin")
def download_monthly_report(report_id: int):
    """Download or view the generated HTML monthly activity report."""
    report = db.session.get(MonthlyReport, report_id)
    if not report:
        return error_response(f"Monthly report with ID {report_id} not found.", status_code=404)

    reports_dir = current_app.config["REPORTS_DIR"]
    file_path = reports_dir / report.filename
    if not file_path.is_file():
        return error_response("Report file not found on server.", status_code=404)

    as_attachment = request.args.get("download", "false").lower() in ("true", "1")
    return send_from_directory(
        reports_dir,
        report.filename,
        as_attachment=as_attachment,
        mimetype="text/html" if report.file_format == "html" else "application/pdf"
    )

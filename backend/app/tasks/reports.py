"""Celery task for generating monthly Admin trekking activity reports."""
import calendar
import json
import logging
from datetime import date, datetime, timedelta
from celery import shared_task
from flask import current_app, render_template_string
from sqlalchemy import func, text
from backend.app.extensions import db
from backend.app.models.trek import Trek
from backend.app.models.booking import Booking
from backend.app.models.monthly_report import MonthlyReport

logger = logging.getLogger(__name__)

REPORT_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Monthly Trekking Activity Report - {{ month_label }}</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            color: #212529;
            background-color: #f8f9fa;
            margin: 0;
            padding: 24px;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: #ffffff;
            border-radius: 8px;
            padding: 32px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }
        .header {
            border-bottom: 2px solid #0d6efd;
            padding-bottom: 16px;
            margin-bottom: 24px;
        }
        .header h1 {
            margin: 0 0 8px 0;
            color: #0d6efd;
            font-size: 26px;
        }
        .header p {
            margin: 0;
            color: #6c757d;
            font-size: 14px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 32px;
        }
        .stat-card {
            background: #f1f8ff;
            border: 1px solid #c8e1ff;
            border-radius: 6px;
            padding: 16px;
            text-align: center;
        }
        .stat-card.secondary {
            background: #f3f4f6;
            border-color: #e5e7eb;
        }
        .stat-number {
            font-size: 32px;
            font-weight: 700;
            color: #0366d6;
            margin: 4px 0;
        }
        .stat-label {
            font-size: 13px;
            font-weight: 600;
            text-transform: uppercase;
            color: #586069;
            letter-spacing: 0.5px;
        }
        h2 {
            font-size: 18px;
            color: #24292e;
            border-bottom: 1px solid #e1e4e8;
            padding-bottom: 8px;
            margin-top: 24px;
            margin-bottom: 16px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 24px;
            font-size: 14px;
        }
        th, td {
            padding: 10px 12px;
            text-align: left;
            border-bottom: 1px solid #eaecef;
        }
        th {
            background-color: #f6f8fa;
            font-weight: 600;
            color: #24292e;
        }
        tr:hover {
            background-color: #fcfcfc;
        }
        .badge {
            display: inline-block;
            padding: 3px 8px;
            font-size: 12px;
            font-weight: 600;
            border-radius: 12px;
        }
        .badge-success { background-color: #dafbe1; color: #1a7f37; }
        .badge-primary { background-color: #ddf4ff; color: #0969da; }
        .badge-warning { background-color: #fff8c5; color: #9a6700; }
        .empty-state {
            padding: 32px;
            text-align: center;
            background-color: #f6f8fa;
            border-radius: 6px;
            color: #6a737d;
            font-style: italic;
        }
        .footer {
            margin-top: 40px;
            padding-top: 16px;
            border-top: 1px solid #eaecef;
            font-size: 12px;
            color: #8c959f;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Monthly Trekking Activity Report</h1>
            <p>Reporting Period: <strong>{{ month_label }} ({{ start_date }} to {{ end_date }})</strong> | Generated on: {{ generated_at }}</p>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Treks Completed</div>
                <div class="stat-number">{{ total_treks }}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Distinct Participants</div>
                <div class="stat-number">{{ total_participants }}</div>
            </div>
            <div class="stat-card secondary">
                <div class="stat-label">Active / Completed Bookings</div>
                <div class="stat-number" style="color: #24292e;">{{ total_active_bookings }}</div>
            </div>
            <div class="stat-card secondary">
                <div class="stat-label">Cancelled Bookings</div>
                <div class="stat-number" style="color: #cf222e;">{{ total_cancelled_bookings }}</div>
            </div>
        </div>

        <h2>Popular Treks of the Month</h2>
        {% if popular_treks %}
        <table>
            <thead>
                <tr>
                    <th>#</th>
                    <th>Trek Name</th>
                    <th>Location</th>
                    <th>Difficulty</th>
                    <th style="text-align: right;">Participants (Bookings)</th>
                </tr>
            </thead>
            <tbody>
                {% for item in popular_treks %}
                <tr>
                    <td>{{ loop.index }}</td>
                    <td><strong>{{ item.name }}</strong></td>
                    <td>{{ item.location }}</td>
                    <td><span class="badge badge-primary">{{ item.difficulty }}</span></td>
                    <td style="text-align: right; font-weight: 600;">{{ item.booking_count }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% else %}
        <div class="empty-state">
            No active trek bookings recorded for this reporting period.
        </div>
        {% endif %}

        <h2>Expeditions Conducted</h2>
        {% if conducted_treks %}
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Trek Name</th>
                    <th>Dates</th>
                    <th>Duration</th>
                    <th>Operational Progress</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                {% for trek in conducted_treks %}
                <tr>
                    <td>#{{ trek.id }}</td>
                    <td><strong>{{ trek.name }}</strong></td>
                    <td>{{ trek.start_date }} - {{ trek.end_date }}</td>
                    <td>{{ trek.duration_days }} days</td>
                    <td><span class="badge badge-success">{{ trek.operational_progress }}</span></td>
                    <td><span class="badge badge-success">{{ trek.status }}</span></td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% else %}
        <div class="empty-state">
            No completed trekking expeditions conducted during this calendar month.
        </div>
        {% endif %}

        <div class="footer">
            Trekking Management Application V2 &bull; Automated System Audit Report &bull; Confidential Administrative Document
        </div>
    </div>
</body>
</html>
"""


@shared_task(bind=True, name="backend.app.tasks.reports.generate_monthly_report")
def generate_monthly_report(self, target_year: int = None, target_month: int = None, report_month: str = None) -> dict:
    """Generate monthly trekking activity report for Admin in HTML format.
    
    Args:
        target_year: Optional integer year (e.g. 2026).
        target_month: Optional integer month (1-12).
        report_month: Optional string in "YYYY-MM" format.
        
    Returns:
        Dictionary summarizing report generation metrics.
    """
    now = datetime.utcnow()
    
    # 1. Determine target reporting month
    if report_month:
        year, month = map(int, report_month.split("-"))
    elif target_year and target_month:
        year = int(target_year)
        month = int(target_month)
    else:
        # Defaults to previous calendar month
        first_of_current_month = date(now.year, now.month, 1)
        prev_month_last_day = first_of_current_month - timedelta(days=1)
        year = prev_month_last_day.year
        month = prev_month_last_day.month

    month_str = f"{year:04d}-{month:02d}"
    month_name = calendar.month_name[month]
    month_label = f"{month_name} {year}"

    # 2. Define exact calendar date boundaries
    start_date = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day)

    logger.info("Generating monthly trekking activity report for %s (%s to %s)", month_label, start_date, end_date)

    try:
        # 3. Query conducted / completed treks within this month
        conducted_treks_query = Trek.query.filter(
            Trek.start_date >= start_date,
            Trek.start_date <= end_date,
            (Trek.status == "Completed") | (Trek.operational_progress == "Completed")
        ).all()
        total_completed_treks = len(conducted_treks_query)

        # 4. Distinct participants in treks during this month (avoiding double-counting)
        distinct_participants = db.session.query(
            func.count(func.distinct(Booking.user_id))
        ).join(Trek, Booking.trek_id == Trek.id).filter(
            Trek.start_date >= start_date,
            Trek.start_date <= end_date,
            Booking.booking_status.in_(["Booked", "Completed"])
        ).scalar() or 0

        # 5. Monthly booking statistics
        active_bookings_count = db.session.query(
            func.count(Booking.id)
        ).join(Trek, Booking.trek_id == Trek.id).filter(
            Trek.start_date >= start_date,
            Trek.start_date <= end_date,
            Booking.booking_status.in_(["Booked", "Completed"])
        ).scalar() or 0

        cancelled_bookings_count = db.session.query(
            func.count(Booking.id)
        ).join(Trek, Booking.trek_id == Trek.id).filter(
            Trek.start_date >= start_date,
            Trek.start_date <= end_date,
            Booking.booking_status == "Cancelled"
        ).scalar() or 0

        # 6. Popular treks ranked by booking count
        popular_results = db.session.query(
            Trek.id,
            Trek.trek_name,
            Trek.location,
            Trek.difficulty,
            func.count(Booking.id).label("booking_count")
        ).join(Booking, Trek.id == Booking.trek_id).filter(
            Trek.start_date >= start_date,
            Trek.start_date <= end_date,
            Booking.booking_status.in_(["Booked", "Completed"])
        ).group_by(Trek.id, Trek.trek_name, Trek.location, Trek.difficulty).order_by(
            text("booking_count DESC")
        ).limit(5).all()

        popular_treks = [
            {
                "id": r[0],
                "name": r[1],
                "location": r[2],
                "difficulty": r[3],
                "booking_count": r[4],
            }
            for r in popular_results
        ]

        conducted_treks_data = [
            {
                "id": t.id,
                "name": t.trek_name,
                "start_date": t.start_date.isoformat(),
                "end_date": t.end_date.isoformat(),
                "duration_days": t.duration_days,
                "operational_progress": t.operational_progress,
                "status": t.status,
            }
            for t in conducted_treks_query
        ]

        # 7. Render HTML report
        rendered_html = render_template_string(
            REPORT_HTML_TEMPLATE,
            month_label=month_label,
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            generated_at=now.strftime("%Y-%m-%d %H:%M:%S UTC"),
            total_treks=total_completed_treks,
            total_participants=distinct_participants,
            total_active_bookings=active_bookings_count,
            total_cancelled_bookings=cancelled_bookings_count,
            popular_treks=popular_treks,
            conducted_treks=conducted_treks_data,
        )

        # 8. Save report file to private instance directory
        reports_dir = current_app.config["REPORTS_DIR"]
        reports_dir.mkdir(parents=True, exist_ok=True)
        filename = f"monthly_report_{month_str}.html"
        file_path = reports_dir / filename

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(rendered_html)

        # 9. Record / update MonthlyReport in database
        report_record = MonthlyReport.query.filter_by(report_month=month_str).first()
        if not report_record:
            report_record = MonthlyReport(
                report_month=month_str,
                filename=filename,
                file_format="html",
            )
            db.session.add(report_record)

        report_record.filename = filename
        report_record.file_format = "html"
        report_record.status = "Generated"
        report_record.total_treks = total_completed_treks
        report_record.total_participants = distinct_participants
        report_record.total_bookings = active_bookings_count + cancelled_bookings_count
        report_record.popular_treks_summary = json.dumps(popular_treks)
        report_record.generated_at = datetime.utcnow()
        report_record.error_message = None

        db.session.commit()
        logger.info("Monthly report successfully saved to %s", file_path)

        return {
            "status": "success",
            "report_month": month_str,
            "filename": filename,
            "total_treks": total_completed_treks,
            "total_participants": distinct_participants,
            "total_bookings": active_bookings_count + cancelled_bookings_count,
            "popular_treks_count": len(popular_treks),
        }

    except Exception as exc:
        db.session.rollback()
        logger.error("Failed to generate monthly report for %s: %s", month_str, exc)
        try:
            report_record = MonthlyReport.query.filter_by(report_month=month_str).first()
            if not report_record:
                report_record = MonthlyReport(
                    report_month=month_str,
                    filename=f"monthly_report_{month_str}.html",
                    file_format="html",
                )
                db.session.add(report_record)
            report_record.status = "Failed"
            report_record.error_message = str(exc)[:250]
            report_record.generated_at = datetime.utcnow()
            db.session.commit()
        except Exception as rec_err:
            db.session.rollback()
            logger.error("Could not record report failure record: %s", rec_err)
        raise exc

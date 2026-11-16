"""
test_milestone7_jobs.py - Automated tests for Milestone 7 Backend Jobs.
Covers:
- Celery task registration and Flask application context binding.
- Daily trek reminders (upcoming treks, cancelled exclusion, inactive skip, duplicate prevention, resilience).
- Monthly Admin activity reports (metrics, period boundaries, distinct participants, popular treks, HTML report generation, Admin RBAC).
- Asynchronous Trekker CSV exports (asynchronous job lifecycle, user data isolation, CSV format, secure download, 403 unauthorized access).
- In-app Notifications API (listing, unread count, mark-read, user isolation).
"""

import csv
import json
import os
import unittest
from datetime import date, datetime, timedelta
from unittest.mock import patch

from backend.app import create_app
from backend.app.extensions import db
from backend.app.models.user import User
from backend.app.models.trek import Trek
from backend.app.models.booking import Booking
from backend.app.models.notification import Notification
from backend.app.models.reminder_log import ReminderLog
from backend.app.models.monthly_report import MonthlyReport
from backend.app.models.export_job import ExportJob
from backend.app.tasks.reminders import send_daily_trek_reminders
from backend.app.tasks.reports import generate_monthly_report
from backend.app.tasks.exports import export_trekker_history_csv


class Milestone7JobsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Create Admin
        self.admin = User(
            full_name="Admin Director",
            email="admin@test.local",
            role="Admin",
            status="Active"
        )
        self.admin.set_password("AdminPass123!")

        # Create Trekker 1
        self.trekker1 = User(
            full_name="Alice Trekker",
            email="alice@test.local",
            role="Trekker",
            status="Active"
        )
        self.trekker1.set_password("TrekkerPass123!")

        # Create Trekker 2
        self.trekker2 = User(
            full_name="Bob Trekker",
            email="bob@test.local",
            role="Trekker",
            status="Active"
        )
        self.trekker2.set_password("TrekkerPass123!")

        # Create Inactive Trekker
        self.inactive_trekker = User(
            full_name="Inactive Trekker",
            email="inactive@test.local",
            role="Trekker",
            status="Inactive"
        )
        self.inactive_trekker.set_password("TrekkerPass123!")

        db.session.add_all([self.admin, self.trekker1, self.trekker2, self.inactive_trekker])
        db.session.commit()

        # Helper to get auth header
        self.admin_headers = self._get_auth_header("admin@test.local", "AdminPass123!")
        self.trekker1_headers = self._get_auth_header("alice@test.local", "TrekkerPass123!")
        self.trekker2_headers = self._get_auth_header("bob@test.local", "TrekkerPass123!")

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def _get_auth_header(self, email, password):
        res = self.client.post(
            "/api/auth/login",
            data=json.dumps({"email": email, "password": password}),
            content_type="application/json"
        )
        token = json.loads(res.data)["data"]["access_token"]
        return {"Authorization": f"Bearer {token}"}

    # =========================================================================
    # 1. CELERY INFRASTRUCTURE & APPLICATION CONTEXT
    # =========================================================================
    def test_01_celery_task_registration(self):
        """1. Verify Celery app is initialized and Milestone 7 tasks are registered."""
        celery_app = self.app.extensions.get("celery")
        self.assertIsNotNone(celery_app, "Celery extension should be registered on app")

        registered_tasks = celery_app.tasks.keys()
        self.assertIn("backend.app.tasks.reminders.send_daily_trek_reminders", registered_tasks)
        self.assertIn("backend.app.tasks.reports.generate_monthly_report", registered_tasks)
        self.assertIn("backend.app.tasks.exports.export_trekker_history_csv", registered_tasks)

    def test_02_celery_task_runs_with_flask_app_context(self):
        """2. Verify Celery task executes properly in eager mode with Flask app context."""
        # Calling .delay() or calling directly should succeed in testing eager mode
        res = send_daily_trek_reminders.delay()
        self.assertTrue(res.successful())
        summary = res.result
        self.assertEqual(summary["status"], "success")

    # =========================================================================
    # 2. DAILY TREK REMINDERS
    # =========================================================================
    def test_03_upcoming_trek_reminders_sent_to_active_participants(self):
        """3. Verify daily reminders are generated for upcoming treks within window."""
        today = date.today()
        upcoming_trek = Trek(
            name="Roopkund Trek",
            description="High altitude glacial lake",
            location="Uttarakhand",
            difficulty="Hard",
            duration_days=8,
            available_slots=10,
            start_date=today + timedelta(days=2),
            end_date=today + timedelta(days=10),
            status="Open"
        )
        db.session.add(upcoming_trek)
        db.session.commit()

        # Alice has an active Booked reservation
        b1 = Booking(
            user_id=self.trekker1.id,
            trek_id=upcoming_trek.id,
            booking_status="Booked",
            payment_status="Paid"
        )
        db.session.add(b1)
        db.session.commit()

        # Run reminder task for today
        result = send_daily_trek_reminders(target_date=today.isoformat(), window_days=3)
        self.assertEqual(result["reminders_sent"], 1)

        # Check in-app notification created for Alice
        notifs = Notification.query.filter_by(user_id=self.trekker1.id).all()
        self.assertEqual(len(notifs), 1)
        self.assertIn("Roopkund Trek", notifs[0].title)
        self.assertIn("Alice Trekker", notifs[0].message)
        self.assertEqual(notifs[0].category, "reminder")
        self.assertFalse(notifs[0].is_read)

        # Check ReminderLog entry
        log = ReminderLog.query.filter_by(booking_id=b1.id, reminder_date=today).first()
        self.assertIsNotNone(log)
        self.assertEqual(log.status, "Sent")

    def test_04_no_reminders_for_cancelled_or_completed_bookings(self):
        """4. Verify cancelled and completed bookings are NOT sent reminders."""
        today = date.today()
        upcoming_trek = Trek(
            name="Kedarkantha Winter Trek",
            description="Snow summit",
            location="Uttarakhand",
            difficulty="Easy",
            duration_days=5,
            available_slots=12,
            start_date=today + timedelta(days=1),
            end_date=today + timedelta(days=6),
            status="Open"
        )
        db.session.add(upcoming_trek)
        db.session.commit()

        # Alice has a Cancelled booking
        b_cancelled = Booking(
            user_id=self.trekker1.id,
            trek_id=upcoming_trek.id,
            booking_status="Cancelled",
            payment_status="Refunded"
        )
        # Bob has a Completed booking
        b_completed = Booking(
            user_id=self.trekker2.id,
            trek_id=upcoming_trek.id,
            booking_status="Completed",
            payment_status="Paid"
        )
        db.session.add_all([b_cancelled, b_completed])
        db.session.commit()

        result = send_daily_trek_reminders(target_date=today.isoformat(), window_days=3)
        self.assertEqual(result["reminders_sent"], 0)
        self.assertEqual(Notification.query.count(), 0)

    def test_05_no_reminders_for_inactive_users(self):
        """5. Verify inactive user accounts do not receive trek reminders."""
        today = date.today()
        upcoming_trek = Trek(
            name="Hampta Pass Trek",
            description="Crossover trek",
            location="Himachal",
            difficulty="Moderate",
            duration_days=5,
            available_slots=15,
            start_date=today + timedelta(days=2),
            end_date=today + timedelta(days=7),
            status="Open"
        )
        db.session.add(upcoming_trek)
        db.session.commit()

        # Inactive user booking
        b = Booking(
            user_id=self.inactive_trekker.id,
            trek_id=upcoming_trek.id,
            booking_status="Booked",
            payment_status="Paid"
        )
        db.session.add(b)
        db.session.commit()

        result = send_daily_trek_reminders(target_date=today.isoformat(), window_days=3)
        self.assertEqual(result["reminders_sent"], 0)
        self.assertEqual(result["reminders_skipped"], 1)
        self.assertEqual(Notification.query.filter_by(user_id=self.inactive_trekker.id).count(), 0)

    def test_06_duplicate_reminder_prevention_idempotency(self):
        """6. Verify running reminder task repeatedly on the same day avoids duplicate reminders."""
        today = date.today()
        upcoming_trek = Trek(
            name="Valley of Flowers",
            description="National park trek",
            location="Uttarakhand",
            difficulty="Easy",
            duration_days=6,
            available_slots=20,
            start_date=today + timedelta(days=1),
            end_date=today + timedelta(days=7),
            status="Open"
        )
        db.session.add(upcoming_trek)
        db.session.commit()

        b = Booking(
            user_id=self.trekker1.id,
            trek_id=upcoming_trek.id,
            booking_status="Booked",
            payment_status="Paid"
        )
        db.session.add(b)
        db.session.commit()

        # First run: sends 1 reminder
        res1 = send_daily_trek_reminders(target_date=today.isoformat(), window_days=3)
        self.assertEqual(res1["reminders_sent"], 1)
        self.assertEqual(Notification.query.count(), 1)

        # Second run: should detect existing reminder log and skip!
        res2 = send_daily_trek_reminders(target_date=today.isoformat(), window_days=3)
        self.assertEqual(res2["reminders_sent"], 0)
        self.assertEqual(res2["reminders_skipped"], 1)
        self.assertEqual(Notification.query.count(), 1, "No duplicate notification created")

    def test_07_empty_upcoming_treks_handled_gracefully(self):
        """7. Verify reminder task handles empty upcoming trek results without error."""
        today = date.today()
        res = send_daily_trek_reminders(target_date=today.isoformat(), window_days=3)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["treks_evaluated"], 0)
        self.assertEqual(res["reminders_sent"], 0)

    # =========================================================================
    # 3. MONTHLY ADMIN ACTIVITY REPORTS
    # =========================================================================
    def test_08_monthly_report_generation_and_metrics(self):
        """8. Verify monthly report calculates correct conducted treks, distinct participants, and popular treks."""
        # Set up a completed trek in October 2026
        oct_start = date(2026, 10, 5)
        oct_end = date(2026, 10, 10)
        trek_oct = Trek(
            name="Kashmir Great Lakes",
            description="Alpine lakes expedition",
            location="Kashmir",
            difficulty="Moderate",
            duration_days=6,
            available_slots=15,
            start_date=oct_start,
            end_date=oct_end,
            status="Completed",
            operational_progress="Completed"
        )
        db.session.add(trek_oct)
        db.session.commit()

        # Alice and Bob booked trek_oct
        b1 = Booking(
            user_id=self.trekker1.id,
            trek_id=trek_oct.id,
            booking_status="Completed",
            payment_status="Paid"
        )
        b2 = Booking(
            user_id=self.trekker2.id,
            trek_id=trek_oct.id,
            booking_status="Completed",
            payment_status="Paid"
        )
        db.session.add_all([b1, b2])
        db.session.commit()

        # Generate report for 2026-10
        summary = generate_monthly_report(report_month="2026-10")
        self.assertEqual(summary["status"], "success")
        self.assertEqual(summary["total_treks"], 1)
        self.assertEqual(summary["total_participants"], 2)
        self.assertGreaterEqual(summary["popular_treks_count"], 1)

        # Check MonthlyReport in DB
        rep = MonthlyReport.query.filter_by(report_month="2026-10").first()
        self.assertIsNotNone(rep)
        self.assertEqual(rep.status, "Generated")
        self.assertEqual(rep.total_treks, 1)
        self.assertEqual(rep.total_participants, 2)

        # Check physical HTML file exists on disk
        reports_dir = self.app.config["REPORTS_DIR"]
        report_file = reports_dir / rep.filename
        self.assertTrue(report_file.is_file(), "Report file must exist on disk")
        
        with open(report_file, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("Kashmir Great Lakes", content)
            self.assertIn("October 2026", content)

    def test_09_monthly_report_empty_month_handling(self):
        """9. Verify monthly report handles a month with 0 treks gracefully."""
        summary = generate_monthly_report(report_month="2025-01")
        self.assertEqual(summary["status"], "success")
        self.assertEqual(summary["total_treks"], 0)
        self.assertEqual(summary["total_participants"], 0)

        rep = MonthlyReport.query.filter_by(report_month="2025-01").first()
        self.assertIsNotNone(rep)
        self.assertEqual(rep.status, "Generated")

    def test_10_admin_reports_api_access_control(self):
        """10. Verify /api/admin/reports/monthly is strictly restricted to Admin role."""
        # Unauthenticated -> 401
        res = self.client.get("/api/admin/reports/monthly")
        self.assertEqual(res.status_code, 401)

        # Trekker -> 403 Forbidden
        res = self.client.get("/api/admin/reports/monthly", headers=self.trekker1_headers)
        self.assertEqual(res.status_code, 403)

        # Admin -> 200 OK
        res = self.client.get("/api/admin/reports/monthly", headers=self.admin_headers)
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn("reports", data["data"])

    def test_11_admin_reports_download_endpoint(self):
        """11. Verify Admin can download generated monthly report file; others rejected."""
        generate_monthly_report(report_month="2026-09")
        rep = MonthlyReport.query.filter_by(report_month="2026-09").first()

        # Trekker download -> 403
        res = self.client.get(f"/api/admin/reports/monthly/{rep.id}/download", headers=self.trekker1_headers)
        self.assertEqual(res.status_code, 403)

        # Admin download -> 200 OK
        res = self.client.get(f"/api/admin/reports/monthly/{rep.id}/download", headers=self.admin_headers)
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/html", res.content_type)

    # =========================================================================
    # 4. ASYNCHRONOUS TREKKER CSV EXPORT
    # =========================================================================
    def test_12_trekker_can_request_csv_export_returns_202(self):
        """12. Verify Trekker requesting CSV export creates ExportJob and returns HTTP 202."""
        res = self.client.post("/api/trekker/exports", headers=self.trekker1_headers)
        self.assertEqual(res.status_code, 202)
        data = json.loads(res.data)
        self.assertTrue(data["success"])
        job_id = data["data"]["job_id"]

        # In testing eager mode, task has completed immediately
        job = db.session.get(ExportJob, job_id)
        self.assertIsNotNone(job)
        self.assertEqual(job.user_id, self.trekker1.id)
        self.assertEqual(job.status, "Completed")
        self.assertIsNotNone(job.filename)

    def test_13_csv_export_content_and_user_isolation(self):
        """13. Verify exported CSV file contains correct booking records and strictly isolates user data."""
        # Create a trek and bookings
        trek = Trek(
            name="Har Ki Dun",
            description="Cradle of shaped valley",
            location="Uttarakhand",
            difficulty="Moderate",
            duration_days=7,
            available_slots=10,
            start_date=date.today() + timedelta(days=20),
            end_date=date.today() + timedelta(days=27),
            status="Open"
        )
        db.session.add(trek)
        db.session.commit()

        # Alice's booking
        b_alice = Booking(
            user_id=self.trekker1.id,
            trek_id=trek.id,
            booking_status="Booked",
            payment_status="Paid"
        )
        # Bob's booking
        b_bob = Booking(
            user_id=self.trekker2.id,
            trek_id=trek.id,
            booking_status="Booked",
            payment_status="Paid"
        )
        db.session.add_all([b_alice, b_bob])
        db.session.commit()

        # Alice triggers export
        res = self.client.post("/api/trekker/exports", headers=self.trekker1_headers)
        self.assertEqual(res.status_code, 202)
        job_id = json.loads(res.data)["data"]["job_id"]
        job = db.session.get(ExportJob, job_id)

        # Inspect generated CSV file
        exports_dir = self.app.config["EXPORTS_DIR"]
        csv_file = exports_dir / job.filename
        self.assertTrue(csv_file.is_file())

        with open(csv_file, "r", encoding="utf-8") as f:
            reader = list(csv.reader(f))
            headers = reader[0]
            self.assertEqual(headers, [
                "Booking ID", "Trek Name", "Location", "Difficulty", "Duration (Days)",
                "Booking Date", "Booking Status", "Trek Status", "Start Date", "End Date"
            ])
            # Must only have Alice's booking
            self.assertEqual(len(reader), 2, "1 header row + 1 booking row")
            row = reader[1]
            self.assertEqual(row[0], str(b_alice.id))
            self.assertEqual(row[1], "Har Ki Dun")
            self.assertNotEqual(row[0], str(b_bob.id), "Bob's booking must not appear in Alice's CSV")

    def test_14_unauthorized_download_rejection(self):
        """14. Verify Bob cannot download Alice's export file (HTTP 403 Forbidden)."""
        res = self.client.post("/api/trekker/exports", headers=self.trekker1_headers)
        job_id = json.loads(res.data)["data"]["job_id"]

        # Bob attempts to download Alice's job -> 403 Forbidden
        res_bob = self.client.get(f"/api/trekker/exports/{job_id}/download", headers=self.trekker2_headers)
        self.assertEqual(res_bob.status_code, 403)
        self.assertIn("not authorized", json.loads(res_bob.data)["message"].lower())

        # Alice downloads her own job -> 200 OK
        res_alice = self.client.get(f"/api/trekker/exports/{job_id}/download", headers=self.trekker1_headers)
        self.assertEqual(res_alice.status_code, 200)
        self.assertEqual(res_alice.content_type, "text/csv; charset=utf-8")

    def test_15_export_completion_creates_in_app_notification(self):
        """15. Verify export job completion generates an in-app notification for the user."""
        res = self.client.post("/api/trekker/exports", headers=self.trekker1_headers)
        job_id = json.loads(res.data)["data"]["job_id"]

        notifs = Notification.query.filter_by(user_id=self.trekker1.id, category="export").all()
        self.assertEqual(len(notifs), 1)
        self.assertIn(f"Job #{job_id}", notifs[0].message)
        self.assertIn("ready for download", notifs[0].message)

    # =========================================================================
    # 5. NOTIFICATIONS API
    # =========================================================================
    def test_16_notifications_list_and_read(self):
        """16. Verify GET /api/notifications and PATCH /api/notifications/<id>/read."""
        # Create 2 notifications for Alice
        n1 = Notification(
            user_id=self.trekker1.id,
            title="Notification 1",
            message="Test message 1",
            category="general",
            is_read=False
        )
        n2 = Notification(
            user_id=self.trekker1.id,
            title="Notification 2",
            message="Test message 2",
            category="general",
            is_read=False
        )
        # 1 notification for Bob
        n_bob = Notification(
            user_id=self.trekker2.id,
            title="Bob's Notification",
            message="For Bob only",
            category="general",
            is_read=False
        )
        db.session.add_all([n1, n2, n_bob])
        db.session.commit()

        # Alice fetches her notifications
        res = self.client.get("/api/notifications", headers=self.trekker1_headers)
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)["data"]
        self.assertEqual(data["total_count"], 2)
        self.assertEqual(data["unread_count"], 2)

        # Alice marks n1 as read
        res_read = self.client.patch(f"/api/notifications/{n1.id}/read", headers=self.trekker1_headers)
        self.assertEqual(res_read.status_code, 200)
        self.assertTrue(db.session.get(Notification, n1.id).is_read)

        # Alice tries to mark Bob's notification as read -> 403 Forbidden!
        res_forbidden = self.client.patch(f"/api/notifications/{n_bob.id}/read", headers=self.trekker1_headers)
        self.assertEqual(res_forbidden.status_code, 403)


if __name__ == "__main__":
    unittest.main()

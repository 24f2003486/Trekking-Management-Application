"""
test_admin_reports.py - Automated tests for Admin Reports & Statistics APIs.
Covers:
- Test 30: Report stats reflect actual database records (difficulty and booking status breakdown).
- Test 31: Popular treks aggregation ranks correctly based on booking count.
- Test 32: Monthly activity aggregation reflects actual booking timestamps.
"""

import json
import unittest
from datetime import date, timedelta
from backend.app import create_app
from backend.app.extensions import db
from backend.app.models.user import User
from backend.app.models.trek import Trek
from backend.app.models.booking import Booking


class AdminReportsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Admin
        self.admin = User(
            full_name="Admin Test",
            email="admin@test.local",
            role="Admin",
            status="Active"
        )
        self.admin.set_password("AdminPass123!")
        db.session.add(self.admin)

        # Trekkers
        self.trekker1 = User(
            full_name="Trekker One",
            email="one@test.local",
            role="Trekker",
            status="Active"
        )
        self.trekker1.set_password("Pass123!")

        self.trekker2 = User(
            full_name="Trekker Two",
            email="two@test.local",
            role="Trekker",
            status="Active"
        )
        self.trekker2.set_password("Pass123!")

        db.session.add_all([self.trekker1, self.trekker2])
        db.session.commit()

        # Treks: 2 Easy, 1 Moderate, 1 Hard
        self.trek_easy1 = Trek(
            name="Triund Trek",
            description="Easy ridge trek",
            location="Himachal",
            difficulty="Easy",
            duration_days=2,
            available_slots=18,
            start_date=date.today() + timedelta(days=5),
            end_date=date.today() + timedelta(days=7)
        )
        self.trek_easy2 = Trek(
            name="Prashar Lake",
            description="Lake trek",
            location="Himachal",
            difficulty="Easy",
            duration_days=2,
            available_slots=15,
            start_date=date.today() + timedelta(days=10),
            end_date=date.today() + timedelta(days=12)
        )
        self.trek_mod = Trek(
            name="Bhrigu Lake",
            description="Moderate meadow trek",
            location="Himachal",
            difficulty="Moderate",
            duration_days=4,
            available_slots=11,
            start_date=date.today() + timedelta(days=15),
            end_date=date.today() + timedelta(days=19)
        )
        self.trek_diff = Trek(
            name="Pin Parvati",
            description="Trans-Himalayan pass",
            location="Himachal",
            difficulty="Hard",
            duration_days=11,
            available_slots=8,
            start_date=date.today() + timedelta(days=25),
            end_date=date.today() + timedelta(days=36)
        )
        db.session.add_all([self.trek_easy1, self.trek_easy2, self.trek_mod, self.trek_diff])
        db.session.commit()

        # Bookings: 2 on Triund, 1 on Bhrigu
        b1 = Booking(
            user_id=self.trekker1.id,
            trek_id=self.trek_easy1.id,
            status="Booked",
            payment_status="Paid"
        )
        b2 = Booking(
            user_id=self.trekker2.id,
            trek_id=self.trek_easy1.id,
            status="Booked",
            payment_status="Paid"
        )
        b3 = Booking(
            user_id=self.trekker1.id,
            trek_id=self.trek_mod.id,
            status="Completed",
            payment_status="Paid"
        )
        db.session.add_all([b1, b2, b3])
        db.session.commit()

        # Login admin
        res = self.client.post(
            "/api/auth/login",
            data=json.dumps({"email": "admin@test.local", "password": "AdminPass123!"}),
            content_type="application/json"
        )
        self.admin_token = json.loads(res.data)["data"]["access_token"]
        self.admin_headers = {"Authorization": f"Bearer {self.admin_token}"}

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_30_reports_reflect_actual_database_records(self):
        """30. Reports endpoint returns accurate breakdown of difficulty and status."""
        res = self.client.get("/api/admin/reports", headers=self.admin_headers)
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)["data"]

        # Difficulty breakdown: Easy: 2, Moderate: 1, Hard: 1
        raw_diff = data["treks_by_difficulty"]
        diff_dict = raw_diff if isinstance(raw_diff, dict) else {item["difficulty"]: item["count"] for item in raw_diff}
        self.assertEqual(diff_dict.get("Easy"), 2)
        self.assertEqual(diff_dict.get("Moderate"), 1)
        self.assertEqual(diff_dict.get("Hard"), 1)

        # Booking status breakdown: Booked: 2, Completed: 1
        raw_status = data["bookings_by_status"]
        status_dict = raw_status if isinstance(raw_status, dict) else {item["status"]: item["count"] for item in raw_status}
        self.assertEqual(status_dict.get("Booked"), 2)
        self.assertEqual(status_dict.get("Completed"), 1)

    def test_31_popular_treks_ranked_by_booking_count(self):
        """31. Popular treks ranking correctly ranks the most booked trek first."""
        res = self.client.get("/api/admin/reports", headers=self.admin_headers)
        self.assertEqual(res.status_code, 200)
        popular = json.loads(res.data)["data"]["popular_treks"]
        self.assertGreater(len(popular), 0)
        self.assertEqual(popular[0]["name"], "Triund Trek")
        self.assertEqual(popular[0]["booking_count"], 2)

    def test_32_monthly_activity_aggregation(self):
        """32. Monthly activity aggregates bookings by current year-month."""
        res = self.client.get("/api/admin/reports", headers=self.admin_headers)
        self.assertEqual(res.status_code, 200)
        monthly = json.loads(res.data)["data"]["monthly_activity"]
        self.assertGreater(len(monthly), 0)
        current_month = date.today().strftime("%Y-%m")
        current_month_entry = next((m for m in monthly if m["month"] == current_month), None)
        self.assertIsNotNone(current_month_entry)
        self.assertEqual(current_month_entry["count"], 3)


if __name__ == "__main__":
    unittest.main()

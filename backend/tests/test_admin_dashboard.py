"""Tests for Admin overview dashboard and statistics."""
from datetime import date
import unittest
from backend.app import create_app
from backend.app.extensions import db
from backend.app.models import User, Trek, Booking, StaffProfile


class AdminDashboardTestCase(unittest.TestCase):
    """Test suite for GET /api/admin/dashboard."""

    def setUp(self):
        """Configure test client and in-memory database."""
        self.app = create_app("testing")
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Create Admin
        self.admin = User(full_name="Admin Test", email="admin@test.local", role="Admin", status="Active")
        self.admin.set_password("AdminPass123!")

        # Create Trek Staff with profile
        self.staff = User(full_name="Staff One", email="staff1@test.local", role="Trek Staff", status="Active")
        self.staff.set_password("StaffPass123!")

        # Create Trekkers
        self.trekker1 = User(full_name="Trekker One", email="t1@test.local", role="Trekker", status="Active")
        self.trekker1.set_password("Pass123!")
        self.trekker2 = User(full_name="Trekker Two", email="t2@test.local", role="Trekker", status="Blacklisted")
        self.trekker2.set_password("Pass123!")

        db.session.add_all([self.admin, self.staff, self.trekker1, self.trekker2])
        db.session.commit()

        # Add profile for staff
        profile = StaffProfile(user=self.staff, specialization="High Altitude", experience_years=4)
        db.session.add(profile)

        # Add Treks
        self.trek1 = Trek(
            trek_name="Himalayan Pass", location="Himachal", difficulty="Hard",
            duration_days=6, available_slots=10, status="Open",
            start_date=date(2027, 5, 1), end_date=date(2027, 5, 7)
        )
        self.trek2 = Trek(
            trek_name="Valley Walk", location="Uttarakhand", difficulty="Easy",
            duration_days=3, available_slots=20, status="Pending",
            start_date=date(2027, 6, 1), end_date=date(2027, 6, 4)
        )
        db.session.add_all([self.trek1, self.trek2])
        db.session.commit()

        # Add Booking
        booking = Booking(user=self.trekker1, trek=self.trek1, booking_status="Booked", payment_status="Paid")
        db.session.add(booking)
        db.session.commit()

        # Login tokens
        self.admin_token = self._login("admin@test.local", "AdminPass123!")
        self.staff_token = self._login("staff1@test.local", "StaffPass123!")
        self.trekker_token = self._login("t1@test.local", "Pass123!")

    def tearDown(self):
        """Clean up database session and tables."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def _login(self, email, password):
        res = self.client.post("/api/auth/login", json={"email": email, "password": password})
        return res.get_json()["data"]["access_token"]

    def _auth_header(self, token):
        return {"Authorization": f"Bearer {token}"}

    def test_01_admin_can_retrieve_dashboard_statistics(self):
        """1. Admin can retrieve dashboard statistics."""
        res = self.client.get("/api/admin/dashboard", headers=self._auth_header(self.admin_token))
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertIn("total_treks", data["data"])

    def test_02_statistics_reflect_actual_database_records(self):
        """2. Statistics reflect actual database records."""
        res = self.client.get("/api/admin/dashboard", headers=self._auth_header(self.admin_token))
        stats = res.get_json()["data"]

        self.assertEqual(stats["total_treks"], 2)
        self.assertEqual(stats["total_users"], 4)
        self.assertEqual(stats["total_staff"], 1)
        self.assertEqual(stats["total_trekkers"], 2)
        self.assertEqual(stats["total_admins"], 1)
        self.assertEqual(stats["total_bookings"], 1)
        self.assertEqual(stats["open_treks"], 1)
        self.assertEqual(stats["pending_treks"], 1)
        self.assertEqual(stats["active_users"], 3)
        self.assertEqual(stats["blacklisted_users"], 1)

    def test_03_non_admin_users_cannot_access_dashboard(self):
        """3. Non-admin users cannot access the dashboard endpoint (HTTP 403)."""
        res_staff = self.client.get("/api/admin/dashboard", headers=self._auth_header(self.staff_token))
        self.assertEqual(res_staff.status_code, 403)

        res_trekker = self.client.get("/api/admin/dashboard", headers=self._auth_header(self.trekker_token))
        self.assertEqual(res_trekker.status_code, 403)


if __name__ == "__main__":
    unittest.main()

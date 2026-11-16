"""Automated tests for Trek Staff dashboard endpoint."""
from datetime import date
import unittest
from backend.app import create_app
from backend.app.extensions import db
from backend.app.models import User, Trek, Booking, StaffProfile


class StaffDashboardTestCase(unittest.TestCase):
    """Test suite verifying /api/staff/dashboard functionality and metrics."""

    def setUp(self):
        """Configure test client and initialize database with test staff, trekkers and treks."""
        self.app = create_app("testing")
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Create Primary Trek Staff
        self.staff1 = User(
            full_name="Aarav Sharma",
            email="aarav.staff@test.local",
            role="Trek Staff",
            status="Active"
        )
        self.staff1.set_password("StaffPass123!")

        # Create Secondary Trek Staff (for data isolation checks)
        self.staff2 = User(
            full_name="Maya Nair",
            email="maya.staff@test.local",
            role="Trek Staff",
            status="Active"
        )
        self.staff2.set_password("StaffPass123!")

        # Create Inactive Staff
        self.inactive_staff = User(
            full_name="Inactive Staff",
            email="inactive.staff@test.local",
            role="Trek Staff",
            status="Inactive"
        )
        self.inactive_staff.set_password("StaffPass123!")

        # Create Trekker
        self.trekker = User(
            full_name="Rohan Trekker",
            email="rohan@test.local",
            role="Trekker",
            status="Active"
        )
        self.trekker.set_password("TrekkerPass123!")

        db.session.add_all([self.staff1, self.staff2, self.inactive_staff, self.trekker])
        db.session.commit()

        # Add Staff Profiles
        p1 = StaffProfile(user=self.staff1, specialization="High Altitude Lead", experience_years=7)
        p2 = StaffProfile(user=self.staff2, specialization="Wilderness Medical", experience_years=4)
        db.session.add_all([p1, p2])
        db.session.commit()

        # Create Treks assigned to staff1
        self.trek1 = Trek(
            trek_name="Roopkund Expedition",
            location="Uttarakhand",
            difficulty="Hard",
            duration_days=8,
            available_slots=15,
            status="Open",
            operational_progress="Started",
            start_date=date(2027, 6, 1),
            end_date=date(2027, 6, 8),
            assigned_staff_id=self.staff1.id
        )
        self.trek2 = Trek(
            trek_name="Kedarkantha Winter Trek",
            location="Uttarakhand",
            difficulty="Easy",
            duration_days=5,
            available_slots=20,
            status="Closed",
            operational_progress="Completed",
            start_date=date(2027, 1, 10),
            end_date=date(2027, 1, 14),
            assigned_staff_id=self.staff1.id
        )
        self.trek3 = Trek(
            trek_name="Valley of Flowers",
            location="Uttarakhand",
            difficulty="Moderate",
            duration_days=6,
            available_slots=10,
            status="Open",
            operational_progress="Ongoing",
            start_date=date(2027, 7, 15),
            end_date=date(2027, 7, 20),
            assigned_staff_id=self.staff1.id
        )

        # Create Trek assigned to staff2 (should NOT appear in staff1's metrics)
        self.trek_staff2 = Trek(
            trek_name="Hampta Pass Trek",
            location="Himachal Pradesh",
            difficulty="Moderate",
            duration_days=5,
            available_slots=12,
            status="Open",
            operational_progress="Not Started",
            start_date=date(2027, 8, 1),
            end_date=date(2027, 8, 5),
            assigned_staff_id=self.staff2.id
        )

        db.session.add_all([self.trek1, self.trek2, self.trek3, self.trek_staff2])
        db.session.commit()

        # Add Bookings for staff1's treks
        b1 = Booking(user_id=self.trekker.id, trek_id=self.trek1.id, booking_status="Booked", payment_status="Paid")
        b2 = Booking(user_id=self.trekker.id, trek_id=self.trek3.id, booking_status="Booked", payment_status="Paid")
        b3 = Booking(user_id=self.trekker.id, trek_id=self.trek2.id, booking_status="Cancelled", payment_status="Refunded")
        db.session.add_all([b1, b2, b3])
        db.session.commit()

        # Tokens
        self.token_staff1 = self._get_token(self.staff1.email, "StaffPass123!")
        self.token_staff2 = self._get_token(self.staff2.email, "StaffPass123!")
        self.token_inactive = self._get_token(self.inactive_staff.email, "StaffPass123!")
        self.token_trekker = self._get_token(self.trekker.email, "TrekkerPass123!")

    def tearDown(self):
        """Clean up database session and drop all tables."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def _get_token(self, email, password):
        res = self.client.post("/api/auth/login", json={"email": email, "password": password})
        if res.status_code == 200:
            return res.get_json()["data"]["access_token"]
        return None

    def _auth(self, token):
        return {"Authorization": f"Bearer {token}"}

    def test_unauthenticated_dashboard_rejected(self):
        """Verify unauthenticated access to staff dashboard returns HTTP 401."""
        res = self.client.get("/api/staff/dashboard")
        self.assertEqual(res.status_code, 401)
        self.assertFalse(res.get_json()["success"])

    def test_trekker_cannot_access_staff_dashboard(self):
        """Verify Trekker user receives HTTP 403 Forbidden on staff dashboard."""
        res = self.client.get("/api/staff/dashboard", headers=self._auth(self.token_trekker))
        self.assertEqual(res.status_code, 403)
        self.assertFalse(res.get_json()["success"])

    def test_inactive_staff_rejected(self):
        """Verify Inactive staff cannot access dashboard (HTTP 403)."""
        # When user is inactive, login fails or decorator blocks access
        if self.token_inactive:
            res = self.client.get("/api/staff/dashboard", headers=self._auth(self.token_inactive))
            self.assertEqual(res.status_code, 403)

    def test_active_staff_receives_accurate_metrics(self):
        """Verify active staff dashboard returns calculated real DB metrics."""
        res = self.client.get("/api/staff/dashboard", headers=self._auth(self.token_staff1))
        self.assertEqual(res.status_code, 200)
        data = res.get_json()["data"]

        # Check role and profile info
        self.assertEqual(data["role"], "Trek Staff")
        self.assertEqual(data["staff_name"], "Aarav Sharma")
        self.assertEqual(data["specialization"], "High Altitude Lead")
        self.assertEqual(data["experience_years"], 7)

        # Check metrics
        self.assertEqual(data["total_assigned_treks"], 3)
        self.assertEqual(data["open_treks"], 2)
        self.assertEqual(data["closed_treks"], 1)
        self.assertEqual(data["ongoing_treks"], 1)
        self.assertEqual(data["completed_treks"], 1)
        # Active participants across assigned treks: b1 (Roopkund) + b2 (Valley of Flowers) = 2 (b3 is Cancelled)
        self.assertEqual(data["total_participants"], 2)

    def test_metrics_isolated_between_staff_members(self):
        """Verify staff2 metrics only reflect their own assigned trek."""
        res = self.client.get("/api/staff/dashboard", headers=self._auth(self.token_staff2))
        self.assertEqual(res.status_code, 200)
        data = res.get_json()["data"]

        self.assertEqual(data["staff_name"], "Maya Nair")
        self.assertEqual(data["total_assigned_treks"], 1)
        self.assertEqual(data["open_treks"], 1)
        self.assertEqual(data["total_participants"], 0)


if __name__ == "__main__":
    unittest.main()

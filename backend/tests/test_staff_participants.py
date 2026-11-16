"""Automated tests for Trek Staff participant management and privacy."""
from datetime import date
import unittest
from backend.app import create_app
from backend.app.extensions import db
from backend.app.models import User, Trek, Booking, StaffProfile


class StaffParticipantsTestCase(unittest.TestCase):
    """Test suite verifying participant roster visibility and data privacy for staff."""

    def setUp(self):
        """Configure test environment with staff, assigned trek, and multiple bookings."""
        self.app = create_app("testing")
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Assigned Staff
        self.staff = User(
            full_name="Lead Guide Meera",
            email="meera@test.local",
            role="Trek Staff",
            status="Active"
        )
        self.staff.set_password("StaffPass123!")

        # Other Staff
        self.other_staff = User(
            full_name="Other Guide",
            email="other@test.local",
            role="Trek Staff",
            status="Active"
        )
        self.other_staff.set_password("StaffPass123!")

        # Trekkers
        self.trekker1 = User(
            full_name="Vikram Seth",
            email="vikram@test.local",
            contact_number="+91 9876543210",
            role="Trekker",
            status="Active"
        )
        self.trekker1.set_password("SecretHash123!")

        self.trekker2 = User(
            full_name="Ananya Roy",
            email="ananya@test.local",
            contact_number="+91 9123456789",
            role="Trekker",
            status="Active"
        )
        self.trekker2.set_password("SecretHash456!")

        db.session.add_all([self.staff, self.other_staff, self.trekker1, self.trekker2])
        db.session.commit()

        # Add Staff Profiles (mandatory for Trek Staff authentication)
        p1 = StaffProfile(user_id=self.staff.id, specialization="Expedition Medic", experience_years=5)
        p2 = StaffProfile(user_id=self.other_staff.id, specialization="Climbing Instructor", experience_years=4)
        db.session.add_all([p1, p2])
        db.session.commit()

        # Trek
        self.trek = Trek(
            trek_name="Sandakphu Phalut Trek",
            location="West Bengal",
            difficulty="Moderate",
            duration_days=6,
            available_slots=15,
            status="Open",
            operational_progress="Started",
            start_date=date(2027, 4, 1),
            end_date=date(2027, 4, 6),
            assigned_staff_id=self.staff.id
        )
        db.session.add(self.trek)
        db.session.commit()

        # Bookings: 1 Active, 1 Cancelled
        self.booking_active = Booking(
            user_id=self.trekker1.id,
            trek_id=self.trek.id,
            booking_status="Booked",
            payment_status="Paid"
        )
        self.booking_cancelled = Booking(
            user_id=self.trekker2.id,
            trek_id=self.trek.id,
            booking_status="Cancelled",
            payment_status="Refunded"
        )
        db.session.add_all([self.booking_active, self.booking_cancelled])
        db.session.commit()

        self.token_staff = self._get_token("meera@test.local", "StaffPass123!")
        self.token_other_staff = self._get_token("other@test.local", "StaffPass123!")

    def tearDown(self):
        """Clean up database session and drop all tables."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def _get_token(self, email, password):
        res = self.client.post("/api/auth/login", json={"email": email, "password": password})
        return res.get_json()["data"]["access_token"]

    def _auth(self, token):
        return {"Authorization": f"Bearer {token}"}

    def test_get_participants_success(self):
        """Verify staff can retrieve participant list with correct count breakdown."""
        res = self.client.get(
            f"/api/staff/treks/{self.trek.id}/participants",
            headers=self._auth(self.token_staff)
        )
        self.assertEqual(res.status_code, 200)
        data = res.get_json()["data"]

        self.assertEqual(data["summary"]["total"], 2)
        self.assertEqual(data["summary"]["active"], 1)
        self.assertEqual(data["summary"]["cancelled"], 1)
        self.assertEqual(len(data["participants"]), 2)

    def test_participant_privacy_never_exposes_password_hash(self):
        """Verify user credentials and password hashes are NEVER exposed in participant roster."""
        res = self.client.get(
            f"/api/staff/treks/{self.trek.id}/participants",
            headers=self._auth(self.token_staff)
        )
        self.assertEqual(res.status_code, 200)
        raw_text = res.get_data(as_text=True)

        self.assertNotIn("SecretHash", raw_text)
        self.assertNotIn("password_hash", raw_text)

        for item in res.get_json()["data"]["participants"]:
            self.assertNotIn("password_hash", item)
            self.assertNotIn("password_hash", item.get("participant", {}))
            self.assertNotIn("password_hash", item.get("user", {}))

    def test_filter_participants_by_status(self):
        """Verify filtering participants by active vs cancelled status."""
        # Active only
        res_active = self.client.get(
            f"/api/staff/treks/{self.trek.id}/participants?status=Booked",
            headers=self._auth(self.token_staff)
        )
        self.assertEqual(res_active.status_code, 200)
        active_list = res_active.get_json()["data"]["participants"]
        self.assertEqual(len(active_list), 1)
        self.assertEqual(active_list[0]["booking_status"], "Booked")
        self.assertEqual(active_list[0]["participant"]["full_name"], "Vikram Seth")

        # Cancelled only
        res_cancelled = self.client.get(
            f"/api/staff/treks/{self.trek.id}/participants?status=Cancelled",
            headers=self._auth(self.token_staff)
        )
        self.assertEqual(res_cancelled.status_code, 200)
        cancelled_list = res_cancelled.get_json()["data"]["participants"]
        self.assertEqual(len(cancelled_list), 1)
        self.assertEqual(cancelled_list[0]["booking_status"], "Cancelled")
        self.assertEqual(cancelled_list[0]["participant"]["full_name"], "Ananya Roy")

    def test_unassigned_staff_cannot_view_participants(self):
        """Verify unassigned staff member receives HTTP 403 when requesting participants."""
        res = self.client.get(
            f"/api/staff/treks/{self.trek.id}/participants",
            headers=self._auth(self.token_other_staff)
        )
        self.assertEqual(res.status_code, 403)
        self.assertFalse(res.get_json()["success"])

    def test_participants_nonexistent_trek_returns_404(self):
        """Verify requesting participants for non-existent trek returns HTTP 404."""
        res = self.client.get(
            "/api/staff/treks/99999/participants",
            headers=self._auth(self.token_staff)
        )
        self.assertEqual(res.status_code, 404)


if __name__ == "__main__":
    unittest.main()

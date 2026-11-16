"""Automated tests for Trek Staff trek operations: slots, status, and progress."""
from datetime import date
import unittest
from backend.app import create_app
from backend.app.extensions import db
from backend.app.models import User, Trek, Booking, StaffProfile


class StaffOperationsTestCase(unittest.TestCase):
    """Test suite verifying trek operation controls (slots, status, progress)."""

    def setUp(self):
        """Configure test environment with staff, trekker, and assigned trek."""
        self.app = create_app("testing")
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Staff 1 (Assigned)
        self.staff1 = User(
            full_name="Operations Staff",
            email="ops.staff@test.local",
            role="Trek Staff",
            status="Active"
        )
        self.staff1.set_password("StaffPass123!")

        # Staff 2 (Unassigned)
        self.staff2 = User(
            full_name="Other Staff",
            email="other.staff@test.local",
            role="Trek Staff",
            status="Active"
        )
        self.staff2.set_password("StaffPass123!")

        # Trekker
        self.trekker = User(
            full_name="Booking Trekker",
            email="trekker@test.local",
            role="Trekker",
            status="Active"
        )
        self.trekker.set_password("TrekkerPass123!")

        db.session.add_all([self.staff1, self.staff2, self.trekker])
        db.session.commit()

        # Add Staff Profiles (mandatory for Trek Staff authentication)
        p1 = StaffProfile(user_id=self.staff1.id, specialization="Field Lead", experience_years=6)
        p2 = StaffProfile(user_id=self.staff2.id, specialization="Safety Officer", experience_years=4)
        db.session.add_all([p1, p2])
        db.session.commit()

        # Assigned Trek
        self.trek = Trek(
            trek_name="Har Ki Dun Valley",
            location="Uttarakhand",
            difficulty="Moderate",
            duration_days=7,
            available_slots=10,
            status="Open",
            operational_progress="Not Started",
            start_date=date(2027, 5, 10),
            end_date=date(2027, 5, 16),
            assigned_staff_id=self.staff1.id
        )
        db.session.add(self.trek)
        db.session.commit()

        self.token_staff1 = self._get_token("ops.staff@test.local", "StaffPass123!")
        self.token_staff2 = self._get_token("other.staff@test.local", "StaffPass123!")

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

    # --- Capacity / Slots Tests ---

    def test_update_slots_success(self):
        """Verify staff can update available slots when valid."""
        res = self.client.patch(
            f"/api/staff/treks/{self.trek.id}/slots",
            headers=self._auth(self.token_staff1),
            json={"available_slots": 15}
        )
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.get_json()["success"])

        # Verify DB updated
        trek = db.session.get(Trek, self.trek.id)
        self.assertEqual(trek.available_slots, 15)

    def test_update_slots_reject_negative(self):
        """Verify slot update rejects negative capacity with HTTP 400."""
        res = self.client.patch(
            f"/api/staff/treks/{self.trek.id}/slots",
            headers=self._auth(self.token_staff1),
            json={"available_slots": -5}
        )
        self.assertEqual(res.status_code, 400)
        self.assertFalse(res.get_json()["success"])

    def test_update_slots_reject_below_active_bookings(self):
        """Verify slot update cannot reduce capacity below existing active bookings."""
        # Add 3 active bookings
        for i in range(3):
            u = User(
                full_name=f"Participant {i}",
                email=f"p{i}@test.local",
                role="Trekker",
                status="Active"
            )
            u.set_password("Pass123!")
            db.session.add(u)
            db.session.commit()
            b = Booking(user_id=u.id, trek_id=self.trek.id, booking_status="Booked")
            db.session.add(b)
        db.session.commit()

        # Attempt to set slots to 2 (< 3 active bookings)
        res = self.client.patch(
            f"/api/staff/treks/{self.trek.id}/slots",
            headers=self._auth(self.token_staff1),
            json={"available_slots": 2}
        )
        self.assertEqual(res.status_code, 400)
        self.assertFalse(res.get_json()["success"])
        self.assertIn("3 active bookings", res.get_json()["message"])

        # Setting slots exactly to 3 should succeed
        res = self.client.patch(
            f"/api/staff/treks/{self.trek.id}/slots",
            headers=self._auth(self.token_staff1),
            json={"available_slots": 3}
        )
        self.assertEqual(res.status_code, 200)

    def test_update_slots_unauthorized_staff_forbidden(self):
        """Verify unassigned staff cannot update slots (HTTP 403)."""
        res = self.client.patch(
            f"/api/staff/treks/{self.trek.id}/slots",
            headers=self._auth(self.token_staff2),
            json={"available_slots": 20}
        )
        self.assertEqual(res.status_code, 403)

    # --- Booking Status Tests ---

    def test_toggle_booking_status_open_and_closed(self):
        """Verify staff can toggle status between Open and Closed."""
        # Close trek
        res = self.client.patch(
            f"/api/staff/treks/{self.trek.id}/status",
            headers=self._auth(self.token_staff1),
            json={"status": "Closed"}
        )
        self.assertEqual(res.status_code, 200)
        trek = db.session.get(Trek, self.trek.id)
        self.assertEqual(trek.status, "Closed")

        # Reopen trek
        res = self.client.patch(
            f"/api/staff/treks/{self.trek.id}/status",
            headers=self._auth(self.token_staff1),
            json={"status": "Open"}
        )
        self.assertEqual(res.status_code, 200)
        trek = db.session.get(Trek, self.trek.id)
        self.assertEqual(trek.status, "Open")

    def test_staff_cannot_set_admin_statuses(self):
        """Verify staff cannot set administrative statuses like Pending or Approved."""
        for admin_status in ["Pending", "Approved"]:
            res = self.client.patch(
                f"/api/staff/treks/{self.trek.id}/status",
                headers=self._auth(self.token_staff1),
                json={"status": admin_status}
            )
            self.assertEqual(res.status_code, 400)
            self.assertFalse(res.get_json()["success"])

    def test_cannot_modify_status_on_completed_trek(self):
        """Verify staff cannot modify status of an already completed trek."""
        self.trek.status = "Completed"
        self.trek.operational_progress = "Completed"
        db.session.commit()

        res = self.client.patch(
            f"/api/staff/treks/{self.trek.id}/status",
            headers=self._auth(self.token_staff1),
            json={"status": "Open"}
        )
        self.assertEqual(res.status_code, 400)
        self.assertFalse(res.get_json()["success"])

    # --- Operational Progress Lifecycle Tests ---

    def test_valid_progress_state_machine_transitions(self):
        """Verify lifecycle progression: Not Started -> Started -> Ongoing -> Completed."""
        # 1. Not Started -> Started
        res1 = self.client.patch(
            f"/api/staff/treks/{self.trek.id}/progress",
            headers=self._auth(self.token_staff1),
            json={"operational_progress": "Started"}
        )
        self.assertEqual(res1.status_code, 200)
        self.assertEqual(db.session.get(Trek, self.trek.id).operational_progress, "Started")

        # 2. Started -> Ongoing
        res2 = self.client.patch(
            f"/api/staff/treks/{self.trek.id}/progress",
            headers=self._auth(self.token_staff1),
            json={"operational_progress": "Ongoing"}
        )
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(db.session.get(Trek, self.trek.id).operational_progress, "Ongoing")

        # 3. Ongoing -> Completed
        res3 = self.client.patch(
            f"/api/staff/treks/{self.trek.id}/progress",
            headers=self._auth(self.token_staff1),
            json={"operational_progress": "Completed"}
        )
        self.assertEqual(res3.status_code, 200)
        completed_trek = db.session.get(Trek, self.trek.id)
        self.assertEqual(completed_trek.operational_progress, "Completed")
        # Booking status should automatically be Closed
        self.assertEqual(completed_trek.status, "Closed")

    def test_reject_backwards_progress_transition(self):
        """Verify state machine rejects backwards or invalid transitions."""
        self.trek.operational_progress = "Ongoing"
        db.session.commit()

        # Attempt Ongoing -> Not Started
        res = self.client.patch(
            f"/api/staff/treks/{self.trek.id}/progress",
            headers=self._auth(self.token_staff1),
            json={"operational_progress": "Not Started"}
        )
        self.assertEqual(res.status_code, 400)
        self.assertFalse(res.get_json()["success"])
        self.assertIn("Invalid progress transition", res.get_json()["message"])

    def test_reject_transition_from_completed_terminal_state(self):
        """Verify Completed is terminal and cannot transition to any other stage."""
        self.trek.operational_progress = "Completed"
        db.session.commit()

        res = self.client.patch(
            f"/api/staff/treks/{self.trek.id}/progress",
            headers=self._auth(self.token_staff1),
            json={"operational_progress": "Ongoing"}
        )
        self.assertEqual(res.status_code, 400)
        self.assertFalse(res.get_json()["success"])

    def test_reject_invalid_progress_stage_name(self):
        """Verify invalid stage name is rejected with HTTP 400."""
        res = self.client.patch(
            f"/api/staff/treks/{self.trek.id}/progress",
            headers=self._auth(self.token_staff1),
            json={"operational_progress": "RandomStage"}
        )
        self.assertEqual(res.status_code, 400)


if __name__ == "__main__":
    unittest.main()

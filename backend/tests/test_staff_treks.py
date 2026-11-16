"""Automated tests for Trek Staff assigned treks retrieval and isolation."""
from datetime import date
import unittest
from backend.app import create_app
from backend.app.extensions import db
from backend.app.models import User, Trek, StaffProfile


class StaffTreksTestCase(unittest.TestCase):
    """Test suite verifying /api/staff/treks endpoints and ownership isolation."""

    def setUp(self):
        """Configure test environment with two staff users and assigned/unassigned treks."""
        self.app = create_app("testing")
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Staff 1
        self.staff1 = User(
            full_name="Lead Guide Rajesh",
            email="rajesh@test.local",
            role="Trek Staff",
            status="Active"
        )
        self.staff1.set_password("StaffPass123!")

        # Staff 2
        self.staff2 = User(
            full_name="Assistant Guide Priya",
            email="priya@test.local",
            role="Trek Staff",
            status="Active"
        )
        self.staff2.set_password("StaffPass123!")

        db.session.add_all([self.staff1, self.staff2])
        db.session.commit()

        # Add Staff Profiles (mandatory for Trek Staff authentication)
        p1 = StaffProfile(user_id=self.staff1.id, specialization="High Altitude", experience_years=5)
        p2 = StaffProfile(user_id=self.staff2.id, specialization="Trail Navigation", experience_years=3)
        db.session.add_all([p1, p2])
        db.session.commit()

        # Treks assigned to Staff 1
        self.trek_staff1_a = Trek(
            trek_name="Kuari Pass Winter Trek",
            location="Joshimath",
            difficulty="Moderate",
            duration_days=6,
            available_slots=18,
            status="Open",
            operational_progress="Not Started",
            start_date=date(2027, 2, 1),
            end_date=date(2027, 2, 6),
            assigned_staff_id=self.staff1.id
        )
        self.trek_staff1_b = Trek(
            trek_name="Pangarchulla Peak",
            location="Joshimath",
            difficulty="Hard",
            duration_days=7,
            available_slots=12,
            status="Closed",
            operational_progress="Ongoing",
            start_date=date(2027, 3, 10),
            end_date=date(2027, 3, 16),
            assigned_staff_id=self.staff1.id
        )

        # Trek assigned to Staff 2
        self.trek_staff2 = Trek(
            trek_name="Brahmatal Trek",
            location="Lohajung",
            difficulty="Moderate",
            duration_days=6,
            available_slots=20,
            status="Open",
            operational_progress="Started",
            start_date=date(2027, 1, 15),
            end_date=date(2027, 1, 20),
            assigned_staff_id=self.staff2.id
        )

        # Unassigned Trek
        self.trek_unassigned = Trek(
            trek_name="Unassigned Expedition",
            location="Manali",
            difficulty="Easy",
            duration_days=3,
            available_slots=25,
            status="Approved",
            operational_progress="Not Started",
            start_date=date(2027, 5, 1),
            end_date=date(2027, 5, 3),
            assigned_staff_id=None
        )

        db.session.add_all([self.trek_staff1_a, self.trek_staff1_b, self.trek_staff2, self.trek_unassigned])
        db.session.commit()

        self.token_staff1 = self._get_token("rajesh@test.local", "StaffPass123!")
        self.token_staff2 = self._get_token("priya@test.local", "StaffPass123!")

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

    def test_list_assigned_treks_strictly_isolated(self):
        """Verify list endpoint only returns treks assigned to the authenticated staff member."""
        res = self.client.get("/api/staff/treks", headers=self._auth(self.token_staff1))
        self.assertEqual(res.status_code, 200)
        data = res.get_json()["data"]

        trek_ids = [t["id"] for t in data["treks"]]
        self.assertEqual(len(trek_ids), 2)
        self.assertIn(self.trek_staff1_a.id, trek_ids)
        self.assertIn(self.trek_staff1_b.id, trek_ids)
        self.assertNotIn(self.trek_staff2.id, trek_ids)
        self.assertNotIn(self.trek_unassigned.id, trek_ids)

    def test_list_assigned_treks_filter_by_status(self):
        """Verify filtering assigned treks by booking status."""
        res = self.client.get("/api/staff/treks?status=Open", headers=self._auth(self.token_staff1))
        self.assertEqual(res.status_code, 200)
        treks = res.get_json()["data"]["treks"]
        self.assertEqual(len(treks), 1)
        self.assertEqual(treks[0]["id"], self.trek_staff1_a.id)

    def test_list_assigned_treks_filter_by_progress(self):
        """Verify filtering assigned treks by operational progress."""
        res = self.client.get("/api/staff/treks?progress=Ongoing", headers=self._auth(self.token_staff1))
        self.assertEqual(res.status_code, 200)
        treks = res.get_json()["data"]["treks"]
        self.assertEqual(len(treks), 1)
        self.assertEqual(treks[0]["id"], self.trek_staff1_b.id)

    def test_get_assigned_trek_details_success(self):
        """Verify staff member can retrieve details of their assigned trek."""
        res = self.client.get(
            f"/api/staff/treks/{self.trek_staff1_a.id}",
            headers=self._auth(self.token_staff1)
        )
        self.assertEqual(res.status_code, 200)
        data = res.get_json()["data"]
        self.assertEqual(data["id"], self.trek_staff1_a.id)
        self.assertEqual(data["trek_name"], "Kuari Pass Winter Trek")

    def test_get_unassigned_trek_forbidden(self):
        """Verify staff member cannot retrieve details of another staff's trek (HTTP 403)."""
        res = self.client.get(
            f"/api/staff/treks/{self.trek_staff2.id}",
            headers=self._auth(self.token_staff1)
        )
        self.assertEqual(res.status_code, 403)
        self.assertFalse(res.get_json()["success"])
        self.assertIn("not authorized", res.get_json()["message"].lower())

    def test_get_unassigned_to_anyone_trek_forbidden(self):
        """Verify staff member cannot retrieve an unassigned trek (HTTP 403)."""
        res = self.client.get(
            f"/api/staff/treks/{self.trek_unassigned.id}",
            headers=self._auth(self.token_staff1)
        )
        self.assertEqual(res.status_code, 403)
        self.assertFalse(res.get_json()["success"])

    def test_get_nonexistent_trek_returns_404(self):
        """Verify requesting non-existent trek ID returns HTTP 404."""
        res = self.client.get(
            "/api/staff/treks/99999",
            headers=self._auth(self.token_staff1)
        )
        self.assertEqual(res.status_code, 404)
        self.assertFalse(res.get_json()["success"])


if __name__ == "__main__":
    unittest.main()

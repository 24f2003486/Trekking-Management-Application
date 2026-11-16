"""Automated tests for Trekker trek browsing, search, and filters."""
from datetime import date
import unittest
from backend.app import create_app
from backend.app.extensions import db
from backend.app.models import User, Trek, Booking


class TrekkerTreksTestCase(unittest.TestCase):
    """Test suite verifying trek catalog browsing, search, and filtering for Trekkers."""

    def setUp(self):
        self.app = create_app("testing")
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Trekker
        self.trekker = User(
            full_name="Explorer Ananya",
            email="ananya@test.local",
            role="Trekker",
            status="Active"
        )
        self.trekker.set_password("Pass123!")
        db.session.add(self.trekker)
        db.session.commit()

        self.token = self._get_token("ananya@test.local", "Pass123!")

        # Create Treks with varying statuses, difficulties, durations, and locations
        self.trek_open_easy = Trek(
            trek_name="Triund Weekend Trek",
            location="Dharamshala, Himachal Pradesh",
            difficulty="Easy",
            duration_days=2,
            available_slots=20,
            status="Open",
            operational_progress="Not Started",
            start_date=date(2027, 5, 1),
            end_date=date(2027, 5, 2)
        )
        self.trek_open_moderate = Trek(
            trek_name="Kedarkantha Winter Summit",
            location="Sankri, Uttarakhand",
            difficulty="Moderate",
            duration_days=5,
            available_slots=15,
            status="Open",
            operational_progress="Not Started",
            start_date=date(2027, 1, 10),
            end_date=date(2027, 1, 14)
        )
        self.trek_open_hard = Trek(
            trek_name="Pin Parvati Pass",
            location="Kullu to Spiti, Himachal Pradesh",
            difficulty="Hard",
            duration_days=11,
            available_slots=10,
            status="Open",
            operational_progress="Not Started",
            start_date=date(2027, 8, 1),
            end_date=date(2027, 8, 11)
        )
        # Closed trek (should NOT appear in bookable browse)
        self.trek_closed = Trek(
            trek_name="Closed Expedition",
            location="Uttarakhand",
            difficulty="Moderate",
            duration_days=6,
            available_slots=12,
            status="Closed",
            operational_progress="Not Started",
            start_date=date(2027, 6, 1),
            end_date=date(2027, 6, 6)
        )
        # Completed trek (should NOT appear in bookable browse)
        self.trek_completed = Trek(
            trek_name="Concluded Expedition",
            location="Ladakh",
            difficulty="Hard",
            duration_days=8,
            available_slots=10,
            status="Completed",
            operational_progress="Completed",
            start_date=date(2026, 9, 1),
            end_date=date(2026, 9, 8)
        )

        db.session.add_all([
            self.trek_open_easy,
            self.trek_open_moderate,
            self.trek_open_hard,
            self.trek_closed,
            self.trek_completed
        ])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def _get_token(self, email, password):
        res = self.client.post("/api/auth/login", json={"email": email, "password": password})
        return res.get_json()["data"]["access_token"]

    def _auth(self):
        return {"Authorization": f"Bearer {self.token}"}

    def test_browse_treks_returns_only_open_uncompleted_treks(self):
        """Verify only Open and non-completed treks appear in available treks list."""
        res = self.client.get("/api/trekker/treks", headers=self._auth())
        self.assertEqual(res.status_code, 200)
        data = res.get_json()["data"]

        trek_ids = [t["id"] for t in data["treks"]]
        self.assertEqual(len(trek_ids), 3)
        self.assertIn(self.trek_open_easy.id, trek_ids)
        self.assertIn(self.trek_open_moderate.id, trek_ids)
        self.assertIn(self.trek_open_hard.id, trek_ids)
        self.assertNotIn(self.trek_closed.id, trek_ids)
        self.assertNotIn(self.trek_completed.id, trek_ids)

    def test_search_treks_by_name_and_location(self):
        """Verify keyword search across trek name and geographic location."""
        # Search by trek name keyword
        res_name = self.client.get("/api/trekker/treks?search=Kedarkantha", headers=self._auth())
        self.assertEqual(res_name.status_code, 200)
        treks = res_name.get_json()["data"]["treks"]
        self.assertEqual(len(treks), 1)
        self.assertEqual(treks[0]["id"], self.trek_open_moderate.id)

        # Search by location keyword
        res_loc = self.client.get("/api/trekker/treks?search=Himachal", headers=self._auth())
        self.assertEqual(res_loc.status_code, 200)
        treks_loc = res_loc.get_json()["data"]["treks"]
        self.assertEqual(len(treks_loc), 2)

    def test_filter_by_difficulty(self):
        """Verify filtering available treks by difficulty level."""
        res = self.client.get("/api/trekker/treks?difficulty=Easy", headers=self._auth())
        self.assertEqual(res.status_code, 200)
        treks = res.get_json()["data"]["treks"]
        self.assertEqual(len(treks), 1)
        self.assertEqual(treks[0]["id"], self.trek_open_easy.id)

    def test_filter_by_duration(self):
        """Verify filtering by exact duration or min/max duration."""
        # Exact duration
        res = self.client.get("/api/trekker/treks?duration=5", headers=self._auth())
        self.assertEqual(res.status_code, 200)
        treks = res.get_json()["data"]["treks"]
        self.assertEqual(len(treks), 1)
        self.assertEqual(treks[0]["id"], self.trek_open_moderate.id)

        # Range filter
        res_range = self.client.get("/api/trekker/treks?min_duration=3&max_duration=12", headers=self._auth())
        self.assertEqual(res_range.status_code, 200)
        treks_range = res_range.get_json()["data"]["treks"]
        self.assertEqual(len(treks_range), 2)

    def test_pagination(self):
        """Verify pagination metadata and page slicing."""
        res = self.client.get("/api/trekker/treks?per_page=2&page=1", headers=self._auth())
        self.assertEqual(res.status_code, 200)
        data = res.get_json()["data"]
        self.assertEqual(len(data["treks"]), 2)
        self.assertEqual(data["pagination"]["total"], 3)
        self.assertEqual(data["pagination"]["pages"], 2)
        self.assertTrue(data["pagination"]["has_next"])

    def test_get_single_trek_details(self):
        """Verify single trek details endpoint returns full metadata and booking indicators."""
        res = self.client.get(f"/api/trekker/treks/{self.trek_open_easy.id}", headers=self._auth())
        self.assertEqual(res.status_code, 200)
        data = res.get_json()["data"]

        self.assertEqual(data["id"], self.trek_open_easy.id)
        self.assertEqual(data["trek_name"], "Triund Weekend Trek")
        self.assertEqual(data["available_slots"], 20)
        self.assertEqual(data["remaining_slots"], 20)
        self.assertTrue(data["can_book"])
        self.assertFalse(data["has_active_booking"])

    def test_get_nonexistent_trek_returns_404(self):
        """Verify requesting non-existent trek returns HTTP 404."""
        res = self.client.get("/api/trekker/treks/99999", headers=self._auth())
        self.assertEqual(res.status_code, 404)


if __name__ == "__main__":
    unittest.main()

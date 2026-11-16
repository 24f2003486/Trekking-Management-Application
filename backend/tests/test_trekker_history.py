"""Automated tests for Trekker booking history, details privacy, and dashboard metrics."""
from datetime import date
import unittest
from backend.app import create_app
from backend.app.extensions import db
from backend.app.models import User, Trek, Booking


class TrekkerHistoryTestCase(unittest.TestCase):
    """Test suite verifying booking history isolation, detail views, and dashboard aggregations."""

    def setUp(self):
        self.app = create_app("testing")
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Trekker A
        self.trekker_a = User(
            full_name="Alok Nath",
            email="alok@test.local",
            role="Trekker",
            status="Active"
        )
        self.trekker_a.set_password("Pass123!")

        # Trekker B
        self.trekker_b = User(
            full_name="Bhavna Shah",
            email="bhavna@test.local",
            role="Trekker",
            status="Active"
        )
        self.trekker_b.set_password("Pass123!")

        db.session.add_all([self.trekker_a, self.trekker_b])
        db.session.commit()

        # Treks
        self.trek1 = Trek(
            trek_name="Valley of Flowers Expedition",
            location="Chamoli, Uttarakhand",
            difficulty="Moderate",
            duration_days=6,
            available_slots=15,
            status="Open",
            operational_progress="Not Started",
            start_date=date(2027, 7, 10),
            end_date=date(2027, 7, 15)
        )
        self.trek2 = Trek(
            trek_name="Har Ki Dun Valley",
            location="Uttarakhand",
            difficulty="Moderate",
            duration_days=7,
            available_slots=20,
            status="Open",
            operational_progress="Started",
            start_date=date(2027, 8, 1),
            end_date=date(2027, 8, 7)
        )
        db.session.add_all([self.trek1, self.trek2])
        db.session.commit()

        # Bookings for Trekker A: 1 Booked, 1 Cancelled
        self.b_a1 = Booking(user_id=self.trekker_a.id, trek_id=self.trek1.id, booking_status="Booked", payment_status="Paid")
        self.b_a2 = Booking(user_id=self.trekker_a.id, trek_id=self.trek2.id, booking_status="Cancelled", payment_status="Refunded")

        # Booking for Trekker B: 1 Booked
        self.b_b1 = Booking(user_id=self.trekker_b.id, trek_id=self.trek1.id, booking_status="Booked", payment_status="Paid")

        db.session.add_all([self.b_a1, self.b_a2, self.b_b1])
        db.session.commit()

        self.token_a = self._get_token("alok@test.local", "Pass123!")
        self.token_b = self._get_token("bhavna@test.local", "Pass123!")

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def _get_token(self, email, password):
        res = self.client.post("/api/auth/login", json={"email": email, "password": password})
        return res.get_json()["data"]["access_token"]

    def _auth(self, token):
        return {"Authorization": f"Bearer {token}"}

    def test_booking_history_strictly_isolated_to_authenticated_user(self):
        """Verify Trekker A only sees their own bookings, never Trekker B's."""
        res = self.client.get("/api/trekker/bookings", headers=self._auth(self.token_a))
        self.assertEqual(res.status_code, 200)
        data = res.get_json()["data"]

        booking_ids = [b["id"] for b in data["bookings"]]
        self.assertEqual(len(booking_ids), 2)
        self.assertIn(self.b_a1.id, booking_ids)
        self.assertIn(self.b_a2.id, booking_ids)
        self.assertNotIn(self.b_b1.id, booking_ids)

    def test_filter_booking_history_by_status(self):
        """Verify filtering booking history by status (e.g. Booked vs Cancelled)."""
        # Filter Booked only
        res_booked = self.client.get("/api/trekker/bookings?status=Booked", headers=self._auth(self.token_a))
        self.assertEqual(res_booked.status_code, 200)
        bookings = res_booked.get_json()["data"]["bookings"]
        self.assertEqual(len(bookings), 1)
        self.assertEqual(bookings[0]["id"], self.b_a1.id)
        self.assertEqual(bookings[0]["booking_status"], "Booked")

        # Filter Cancelled only
        res_cancelled = self.client.get("/api/trekker/bookings?status=Cancelled", headers=self._auth(self.token_a))
        self.assertEqual(res_cancelled.status_code, 200)
        bookings_c = res_cancelled.get_json()["data"]["bookings"]
        self.assertEqual(len(bookings_c), 1)
        self.assertEqual(bookings_c[0]["id"], self.b_a2.id)
        self.assertEqual(bookings_c[0]["booking_status"], "Cancelled")

    def test_get_own_booking_details_success(self):
        """Verify Trekker can view details of their own booking."""
        res = self.client.get(f"/api/trekker/bookings/{self.b_a1.id}", headers=self._auth(self.token_a))
        self.assertEqual(res.status_code, 200)
        data = res.get_json()["data"]
        self.assertEqual(data["id"], self.b_a1.id)
        self.assertEqual(data["trek_name"], "Valley of Flowers Expedition")

    def test_get_other_user_booking_details_forbidden(self):
        """Verify Trekker A receives HTTP 403 Forbidden when requesting Trekker B's booking."""
        res = self.client.get(f"/api/trekker/bookings/{self.b_b1.id}", headers=self._auth(self.token_a))
        self.assertEqual(res.status_code, 403)
        self.assertFalse(res.get_json()["success"])
        self.assertIn("not authorized", res.get_json()["message"].lower())

    def test_get_nonexistent_booking_returns_404(self):
        """Verify requesting non-existent booking ID returns HTTP 404."""
        res = self.client.get("/api/trekker/bookings/99999", headers=self._auth(self.token_a))
        self.assertEqual(res.status_code, 404)

    def test_trekker_dashboard_returns_accurate_metrics(self):
        """Verify /api/trekker/dashboard aggregates real DB counts for authenticated user."""
        res = self.client.get("/api/trekker/dashboard", headers=self._auth(self.token_a))
        self.assertEqual(res.status_code, 200)
        data = res.get_json()["data"]

        self.assertEqual(data["role"], "Trekker")
        self.assertEqual(data["trekker_name"], "Alok Nath")
        self.assertEqual(data["total_bookings"], 2)
        self.assertEqual(data["active_bookings"], 1)
        self.assertEqual(data["cancelled_bookings"], 1)
        self.assertEqual(len(data["upcoming_treks"]), 1)
        self.assertEqual(data["upcoming_treks"][0]["id"], self.b_a1.id)


if __name__ == "__main__":
    unittest.main()

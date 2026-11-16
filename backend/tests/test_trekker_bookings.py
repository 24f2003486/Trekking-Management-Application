"""Automated tests for Trekker booking creation, validations, and capacity guards."""
from datetime import date
import unittest
from backend.app import create_app
from backend.app.extensions import db
from backend.app.models import User, Trek, Booking


class TrekkerBookingsTestCase(unittest.TestCase):
    """Test suite verifying trek reservation workflows, duplicate prevention, and capacity limits."""

    def setUp(self):
        self.app = create_app("testing")
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Trekker 1
        self.trekker1 = User(
            full_name="Pooja Verma",
            email="pooja@test.local",
            role="Trekker",
            status="Active"
        )
        self.trekker1.set_password("Pass123!")

        # Trekker 2
        self.trekker2 = User(
            full_name="Amit Patel",
            email="amit@test.local",
            role="Trekker",
            status="Active"
        )
        self.trekker2.set_password("Pass123!")

        # Inactive Trekker
        self.inactive_trekker = User(
            full_name="Inactive User",
            email="inactive@test.local",
            role="Trekker",
            status="Inactive"
        )
        self.inactive_trekker.set_password("Pass123!")

        db.session.add_all([self.trekker1, self.trekker2, self.inactive_trekker])
        db.session.commit()

        # Treks:
        # 1. Open Trek with 2 slots
        self.trek_open = Trek(
            trek_name="Brahmatal Ridge Trek",
            location="Uttarakhand",
            difficulty="Moderate",
            duration_days=6,
            available_slots=2,
            status="Open",
            operational_progress="Not Started",
            start_date=date(2027, 2, 10),
            end_date=date(2027, 2, 15)
        )
        # 2. Closed Trek
        self.trek_closed = Trek(
            trek_name="Roopkund Secret Trail",
            location="Uttarakhand",
            difficulty="Hard",
            duration_days=8,
            available_slots=10,
            status="Closed",
            operational_progress="Not Started",
            start_date=date(2027, 6, 1),
            end_date=date(2027, 6, 8)
        )
        # 3. Completed Trek
        self.trek_completed = Trek(
            trek_name="Finished Expedition",
            location="Himachal",
            difficulty="Easy",
            duration_days=3,
            available_slots=15,
            status="Completed",
            operational_progress="Completed",
            start_date=date(2026, 8, 1),
            end_date=date(2026, 8, 3)
        )

        db.session.add_all([self.trek_open, self.trek_closed, self.trek_completed])
        db.session.commit()

        self.token_trekker1 = self._get_token("pooja@test.local", "Pass123!")
        self.token_trekker2 = self._get_token("amit@test.local", "Pass123!")
        self.token_inactive = self._get_token("inactive@test.local", "Pass123!")

    def tearDown(self):
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

    def test_successful_trek_booking(self):
        """Verify successful booking creates record with status 'Booked' and returns HTTP 201."""
        res = self.client.post(
            "/api/trekker/bookings",
            headers=self._auth(self.token_trekker1),
            json={"trek_id": self.trek_open.id}
        )
        self.assertEqual(res.status_code, 201)
        data = res.get_json()["data"]

        self.assertEqual(data["booking_status"], "Booked")
        self.assertEqual(data["trek_id"], self.trek_open.id)

        # Verify DB record
        booking = Booking.query.filter_by(user_id=self.trekker1.id, trek_id=self.trek_open.id).first()
        self.assertIsNotNone(booking)
        self.assertEqual(booking.booking_status, "Booked")

    def test_duplicate_active_booking_rejected(self):
        """Verify attempting duplicate active booking returns HTTP 409 Conflict."""
        # First booking succeeds
        res1 = self.client.post(
            "/api/trekker/bookings",
            headers=self._auth(self.token_trekker1),
            json={"trek_id": self.trek_open.id}
        )
        self.assertEqual(res1.status_code, 201)

        # Second booking attempt by same user on same trek rejected
        res2 = self.client.post(
            "/api/trekker/bookings",
            headers=self._auth(self.token_trekker1),
            json={"trek_id": self.trek_open.id}
        )
        self.assertEqual(res2.status_code, 409)
        self.assertIn("already have an active reservation", res2.get_json()["message"])

    def test_booking_closed_trek_rejected(self):
        """Verify attempting to book a closed trek returns HTTP 400 Bad Request."""
        res = self.client.post(
            "/api/trekker/bookings",
            headers=self._auth(self.token_trekker1),
            json={"trek_id": self.trek_closed.id}
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn("not open for bookings", res.get_json()["message"])

    def test_booking_completed_trek_rejected(self):
        """Verify attempting to book a completed trek returns HTTP 400 Bad Request."""
        res = self.client.post(
            "/api/trekker/bookings",
            headers=self._auth(self.token_trekker1),
            json={"trek_id": self.trek_completed.id}
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn("already concluded", res.get_json()["message"])

    def test_booking_full_trek_rejected(self):
        """Verify attempting to book when available slots are exhausted returns HTTP 409 Conflict."""
        # Trek capacity is 2 slots. Book 1st slot with Trekker 1
        res1 = self.client.post(
            "/api/trekker/bookings",
            headers=self._auth(self.token_trekker1),
            json={"trek_id": self.trek_open.id}
        )
        self.assertEqual(res1.status_code, 201)

        # Book 2nd slot with Trekker 2
        res2 = self.client.post(
            "/api/trekker/bookings",
            headers=self._auth(self.token_trekker2),
            json={"trek_id": self.trek_open.id}
        )
        self.assertEqual(res2.status_code, 201)

        # Create Trekker 3 and attempt booking 3rd slot (exceeds capacity)
        trekker3 = User(full_name="Third Trekker", email="third@test.local", role="Trekker", status="Active")
        trekker3.set_password("Pass123!")
        db.session.add(trekker3)
        db.session.commit()
        token3 = self._get_token("third@test.local", "Pass123!")

        res3 = self.client.post(
            "/api/trekker/bookings",
            headers=self._auth(token3),
            json={"trek_id": self.trek_open.id}
        )
        self.assertEqual(res3.status_code, 409)
        self.assertIn("fully booked", res3.get_json()["message"])

    def test_booking_nonexistent_trek_returns_404(self):
        """Verify attempting to book non-existent trek returns HTTP 404."""
        res = self.client.post(
            "/api/trekker/bookings",
            headers=self._auth(self.token_trekker1),
            json={"trek_id": 99999}
        )
        self.assertEqual(res.status_code, 404)

    def test_missing_trek_id_returns_400(self):
        """Verify missing trek_id in body returns HTTP 400."""
        res = self.client.post(
            "/api/trekker/bookings",
            headers=self._auth(self.token_trekker1),
            json={}
        )
        self.assertEqual(res.status_code, 400)

    def test_cancelled_booking_permits_subsequent_booking(self):
        """Verify that after a reservation is Cancelled, the user can book the trek again."""
        # 1. Initial booking
        res1 = self.client.post(
            "/api/trekker/bookings",
            headers=self._auth(self.token_trekker1),
            json={"trek_id": self.trek_open.id}
        )
        self.assertEqual(res1.status_code, 201)
        booking_id = res1.get_json()["data"]["id"]

        # 2. Cancel previous booking
        b = db.session.get(Booking, booking_id)
        b.booking_status = "Cancelled"
        db.session.commit()

        # 3. New booking by same user on same trek should now succeed
        res2 = self.client.post(
            "/api/trekker/bookings",
            headers=self._auth(self.token_trekker1),
            json={"trek_id": self.trek_open.id}
        )
        self.assertEqual(res2.status_code, 201)
        self.assertNotEqual(res2.get_json()["data"]["id"], booking_id)


if __name__ == "__main__":
    unittest.main()

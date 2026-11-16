"""
test_admin_bookings.py - Automated tests for Admin Booking Management APIs.
Covers:
- Test 27: Admin can view all bookings with pagination and status filter.
- Test 28: Admin can view single booking details by ID.
- Test 29: Admin booking APIs are read-only; historical records preserved and no mutation endpoints exist.
"""

import json
import unittest
from datetime import date, timedelta
from backend.app import create_app
from backend.app.extensions import db
from backend.app.models.user import User
from backend.app.models.trek import Trek
from backend.app.models.booking import Booking


class AdminBookingsTestCase(unittest.TestCase):
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

        # Trekker
        self.trekker = User(
            full_name="Trekker Joe",
            email="joe@test.local",
            role="Trekker",
            status="Active"
        )
        self.trekker.set_password("Pass123!")
        db.session.add(self.trekker)

        # Trek
        self.trek = Trek(
            name="Kashmir Great Lakes",
            description="Seven alpine lakes",
            location="Kashmir",
            difficulty="Hard",
            duration_days=7,
            available_slots=14,
            start_date=date.today() + timedelta(days=40),
            end_date=date.today() + timedelta(days=47)
        )
        db.session.add(self.trek)
        db.session.commit()

        # Create 3 Bookings with different statuses
        self.b1 = Booking(
            user_id=self.trekker.id,
            trek_id=self.trek.id,
            status="Booked",
            payment_status="Paid"
        )
        self.b2 = Booking(
            user_id=self.trekker.id,
            trek_id=self.trek.id,
            status="Cancelled",
            payment_status="Refunded"
        )
        self.b3 = Booking(
            user_id=self.trekker.id,
            trek_id=self.trek.id,
            status="Completed",
            payment_status="Paid"
        )
        db.session.add_all([self.b1, self.b2, self.b3])
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

    def test_27_admin_can_view_all_bookings_and_filter_by_status(self):
        """27. Admin can view all bookings with pagination and status filter."""
        # List all
        res = self.client.get("/api/admin/bookings", headers=self.admin_headers)
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data["data"]["pagination"]["total_items"], 3)

        # Filter by Cancelled
        res_cancelled = self.client.get("/api/admin/bookings?status=Cancelled", headers=self.admin_headers)
        self.assertEqual(res_cancelled.status_code, 200)
        data_cancelled = json.loads(res_cancelled.data)
        self.assertEqual(len(data_cancelled["data"]["bookings"]), 1)
        self.assertEqual(data_cancelled["data"]["bookings"][0]["status"], "Cancelled")

        # Filter by Booked
        res_booked = self.client.get("/api/admin/bookings?status=Booked", headers=self.admin_headers)
        self.assertEqual(res_booked.status_code, 200)
        data_booked = json.loads(res_booked.data)
        self.assertEqual(len(data_booked["data"]["bookings"]), 1)
        self.assertEqual(data_booked["data"]["bookings"][0]["status"], "Booked")

    def test_28_admin_can_view_single_booking_details(self):
        """28. Admin can view details of a single booking by ID."""
        res = self.client.get(f"/api/admin/bookings/{self.b1.id}", headers=self.admin_headers)
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data["data"]["id"], self.b1.id)
        self.assertEqual(data["data"]["user"]["email"], "joe@test.local")
        self.assertEqual(data["data"]["trek"]["name"], "Kashmir Great Lakes")
        self.assertEqual(data["data"]["payment_status"], "Paid")

    def test_29_admin_booking_api_is_read_only(self):
        """29. Admin booking APIs preserve history: no mutation (POST/PUT/DELETE) routes exist."""
        # POST not allowed on /api/admin/bookings
        res_post = self.client.post("/api/admin/bookings", headers=self.admin_headers)
        self.assertEqual(res_post.status_code, 405)

        # DELETE not allowed on /api/admin/bookings/<id>
        res_del = self.client.delete(f"/api/admin/bookings/{self.b1.id}", headers=self.admin_headers)
        self.assertEqual(res_del.status_code, 405)

        # PUT not allowed on /api/admin/bookings/<id>
        res_put = self.client.put(f"/api/admin/bookings/{self.b1.id}", headers=self.admin_headers)
        self.assertEqual(res_put.status_code, 405)


if __name__ == "__main__":
    unittest.main()

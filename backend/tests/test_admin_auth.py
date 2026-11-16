"""
test_admin_auth.py - Automated tests for Admin Authorization and Role-Based Access Control.
Covers:
- Test 33: Unauthenticated requests to any Admin endpoint return HTTP 401.
- Test 34: Trek Staff cannot access Admin endpoints (HTTP 403).
- Test 35: Trekker cannot access Admin endpoints (HTTP 403).
"""

import json
import unittest
from backend.app import create_app
from backend.app.extensions import db
from backend.app.models.user import User
from backend.app.models.staff_profile import StaffProfile


class AdminAuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Trek Staff
        self.staff = User(
            full_name="Staff Guide",
            email="staff@test.local",
            role="Trek Staff",
            status="Active"
        )
        self.staff.set_password("StaffPass123!")
        db.session.add(self.staff)
        db.session.flush()
        db.session.add(StaffProfile(user_id=self.staff.id, specialization="Navigation"))

        # Trekker
        self.trekker = User(
            full_name="Trekker Joe",
            email="trekker@test.local",
            role="Trekker",
            status="Active"
        )
        self.trekker.set_password("TrekkerPass123!")
        db.session.add(self.trekker)

        db.session.commit()

        # Login Staff
        res_staff = self.client.post(
            "/api/auth/login",
            data=json.dumps({"email": "staff@test.local", "password": "StaffPass123!"}),
            content_type="application/json"
        )
        self.staff_token = json.loads(res_staff.data)["data"]["access_token"]
        self.staff_headers = {"Authorization": f"Bearer {self.staff_token}"}

        # Login Trekker
        res_trekker = self.client.post(
            "/api/auth/login",
            data=json.dumps({"email": "trekker@test.local", "password": "TrekkerPass123!"}),
            content_type="application/json"
        )
        self.trekker_token = json.loads(res_trekker.data)["data"]["access_token"]
        self.trekker_headers = {"Authorization": f"Bearer {self.trekker_token}"}

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_33_unauthenticated_requests_to_admin_endpoints_rejected(self):
        """33. Requests without JWT token return HTTP 401 across all admin endpoints."""
        endpoints = [
            ("GET", "/api/admin/dashboard"),
            ("GET", "/api/admin/treks"),
            ("POST", "/api/admin/treks"),
            ("GET", "/api/admin/staff"),
            ("POST", "/api/admin/staff"),
            ("GET", "/api/admin/users"),
            ("GET", "/api/admin/bookings"),
            ("GET", "/api/admin/reports")
        ]
        for method, ep in endpoints:
            if method == "GET":
                res = self.client.get(ep)
            else:
                res = self.client.post(ep, data=json.dumps({}), content_type="application/json")
            self.assertEqual(res.status_code, 401, f"Failed on unauthenticated {method} {ep}")

    def test_34_trek_staff_cannot_access_admin_endpoints(self):
        """34. Authenticated Trek Staff receives HTTP 403 on all admin endpoints."""
        endpoints = [
            ("GET", "/api/admin/dashboard"),
            ("GET", "/api/admin/treks"),
            ("POST", "/api/admin/treks"),
            ("GET", "/api/admin/staff"),
            ("POST", "/api/admin/staff"),
            ("GET", "/api/admin/users"),
            ("GET", "/api/admin/bookings"),
            ("GET", "/api/admin/reports")
        ]
        for method, ep in endpoints:
            if method == "GET":
                res = self.client.get(ep, headers=self.staff_headers)
            else:
                res = self.client.post(ep, data=json.dumps({}), headers=self.staff_headers, content_type="application/json")
            self.assertEqual(res.status_code, 403, f"Staff was not rejected on {method} {ep}")

    def test_35_trekker_cannot_access_admin_endpoints(self):
        """35. Authenticated Trekker receives HTTP 403 on all admin endpoints."""
        endpoints = [
            ("GET", "/api/admin/dashboard"),
            ("GET", "/api/admin/treks"),
            ("POST", "/api/admin/treks"),
            ("GET", "/api/admin/staff"),
            ("POST", "/api/admin/staff"),
            ("GET", "/api/admin/users"),
            ("GET", "/api/admin/bookings"),
            ("GET", "/api/admin/reports")
        ]
        for method, ep in endpoints:
            if method == "GET":
                res = self.client.get(ep, headers=self.trekker_headers)
            else:
                res = self.client.post(ep, data=json.dumps({}), headers=self.trekker_headers, content_type="application/json")
            self.assertEqual(res.status_code, 403, f"Trekker was not rejected on {method} {ep}")


if __name__ == "__main__":
    unittest.main()

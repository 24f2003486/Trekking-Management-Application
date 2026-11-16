"""Automated tests for Role-Based Access Control (RBAC) and dashboard endpoints."""
from datetime import timedelta
import unittest
from flask_jwt_extended import create_access_token
from backend.app import create_app
from backend.app.extensions import db
from backend.app.models import User, StaffProfile


class RBACTestCase(unittest.TestCase):
    """Test suite verifying role-based endpoint authorization."""

    def setUp(self):
        """Configure test client and initialize database with test users."""
        self.app = create_app("testing")
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Create Admin
        self.admin = User(
            full_name="Admin User",
            email="admin@test.local",
            role="Admin",
            status="Active"
        )
        self.admin.set_password("AdminPass123!")

        # Create Trek Staff with profile
        self.staff = User(
            full_name="Staff User",
            email="staff@test.local",
            role="Trek Staff",
            status="Active"
        )
        self.staff.set_password("StaffPass123!")

        # Create Trekker
        self.trekker = User(
            full_name="Trekker User",
            email="trekker@test.local",
            role="Trekker",
            status="Active"
        )
        self.trekker.set_password("TrekkerPass123!")

        db.session.add_all([self.admin, self.staff, self.trekker])
        db.session.commit()

        # Add StaffProfile for Staff
        profile = StaffProfile(user=self.staff, specialization="Guide", experience_years=3)
        db.session.add(profile)
        db.session.commit()

        # Generate tokens
        self.admin_token = self._get_token("admin@test.local", "AdminPass123!")
        self.staff_token = self._get_token("staff@test.local", "StaffPass123!")
        self.trekker_token = self._get_token("trekker@test.local", "TrekkerPass123!")

    def tearDown(self):
        """Clean up database session and drop all tables."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def _get_token(self, email, password):
        res = self.client.post("/api/auth/login", json={"email": email, "password": password})
        return res.get_json()["data"]["access_token"]

    def _auth_header(self, token):
        return {"Authorization": f"Bearer {token}"}

    # --- RBAC Tests (15 - 21) ---

    def test_15_admin_can_access_admin_endpoint(self):
        """15. Verify Admin user can access /api/admin/dashboard."""
        res = self.client.get(
            "/api/admin/dashboard",
            headers=self._auth_header(self.admin_token)
        )
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["role"], "Admin")

    def test_16_trekker_cannot_access_admin_endpoint(self):
        """16. Verify Trekker cannot access /api/admin/dashboard (HTTP 403)."""
        res = self.client.get(
            "/api/admin/dashboard",
            headers=self._auth_header(self.trekker_token)
        )
        self.assertEqual(res.status_code, 403)
        self.assertFalse(res.get_json()["success"])

    def test_17_staff_cannot_access_admin_endpoint(self):
        """17. Verify Trek Staff cannot access /api/admin/dashboard (HTTP 403)."""
        res = self.client.get(
            "/api/admin/dashboard",
            headers=self._auth_header(self.staff_token)
        )
        self.assertEqual(res.status_code, 403)
        self.assertFalse(res.get_json()["success"])

    def test_18_trekker_can_access_trekker_endpoint(self):
        """18. Verify Trekker can access /api/trekker/dashboard."""
        res = self.client.get(
            "/api/trekker/dashboard",
            headers=self._auth_header(self.trekker_token)
        )
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["role"], "Trekker")

    def test_19_admin_cannot_access_trekker_only_endpoint(self):
        """19. Verify Admin cannot access exclusive /api/trekker/dashboard (HTTP 403)."""
        res = self.client.get(
            "/api/trekker/dashboard",
            headers=self._auth_header(self.admin_token)
        )
        self.assertEqual(res.status_code, 403)
        self.assertFalse(res.get_json()["success"])

    def test_staff_can_access_staff_endpoint(self):
        """Verify Trek Staff can access /api/staff/dashboard."""
        res = self.client.get(
            "/api/staff/dashboard",
            headers=self._auth_header(self.staff_token)
        )
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["role"], "Trek Staff")

    def test_trekker_cannot_access_staff_endpoint(self):
        """Verify Trekker cannot access /api/staff/dashboard (HTTP 403)."""
        res = self.client.get(
            "/api/staff/dashboard",
            headers=self._auth_header(self.trekker_token)
        )
        self.assertEqual(res.status_code, 403)
        self.assertFalse(res.get_json()["success"])

    def test_20_unauthenticated_api_requests_rejected(self):
        """20. Verify requests without Authorization header are rejected (HTTP 401)."""
        for endpoint in ["/api/admin/dashboard", "/api/staff/dashboard", "/api/trekker/dashboard", "/api/auth/me"]:
            res = self.client.get(endpoint)
            self.assertEqual(res.status_code, 401, f"Endpoint {endpoint} allowed unauthenticated access!")
            self.assertFalse(res.get_json()["success"])

    def test_21_expired_tokens_rejected(self):
        """21. Verify expired tokens are rejected with HTTP 401."""
        # Create an already-expired token (-1 second)
        expired_token = create_access_token(
            identity=str(self.trekker.id),
            expires_delta=timedelta(seconds=-1)
        )

        res = self.client.get(
            "/api/trekker/dashboard",
            headers=self._auth_header(expired_token)
        )
        self.assertEqual(res.status_code, 401)
        self.assertFalse(res.get_json()["success"])
        self.assertIn("expired", res.get_json()["message"].lower())


if __name__ == "__main__":
    unittest.main()


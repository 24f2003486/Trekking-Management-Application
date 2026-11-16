"""Automated tests for logout and token blocklist invalidation."""
import unittest
from backend.app import create_app
from backend.app.extensions import db
from backend.app.models import User, TokenBlocklist


class LogoutTestCase(unittest.TestCase):
    """Test suite verifying logout and token invalidation."""

    def setUp(self):
        """Configure test client and in-memory database."""
        self.app = create_app("testing")
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Create user
        self.user = User(
            full_name="Logout Tester",
            email="logout@example.com",
            role="Trekker",
            status="Active"
        )
        self.user.set_password("SecurePass123!")
        db.session.add(self.user)
        db.session.commit()

        # Login to obtain token
        res = self.client.post("/api/auth/login", json={
            "email": "logout@example.com",
            "password": "SecurePass123!"
        })
        self.token = res.get_json()["data"]["access_token"]
        self.auth_headers = {"Authorization": f"Bearer {self.token}"}

    def tearDown(self):
        """Clean up database session and drop all tables."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_22_successful_logout(self):
        """22. Verify successful logout adds token to blocklist."""
        # Initial check: token works on protected endpoint
        res = self.client.get("/api/auth/me", headers=self.auth_headers)
        self.assertEqual(res.status_code, 200)

        # Logout
        logout_res = self.client.post("/api/auth/logout", headers=self.auth_headers)
        data = logout_res.get_json()

        self.assertEqual(logout_res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertIn("logged out", data["message"].lower())

        # Verify JTI stored in SQLite database
        self.assertEqual(TokenBlocklist.query.count(), 1)

    def test_23_invalidated_token_cannot_be_reused(self):
        """23. Verify invalidated (logged out) token is rejected on subsequent requests."""
        # Perform logout
        self.client.post("/api/auth/logout", headers=self.auth_headers)

        # Attempt to access protected endpoint with the revoked token
        res = self.client.get("/api/auth/me", headers=self.auth_headers)
        data = res.get_json()

        self.assertEqual(res.status_code, 401)
        self.assertFalse(data["success"])
        self.assertIn("revoked", data["message"].lower())

        # Attempt to access role-protected dashboard with the revoked token
        dash_res = self.client.get("/api/trekker/dashboard", headers=self.auth_headers)
        self.assertEqual(dash_res.status_code, 401)
        self.assertFalse(dash_res.get_json()["success"])


if __name__ == "__main__":
    unittest.main()


"""Automated tests for Trekker profile management and authorization."""
import unittest
from backend.app import create_app
from backend.app.extensions import db
from backend.app.models import User, StaffProfile


class TrekkerProfileTestCase(unittest.TestCase):
    """Test suite verifying Trekker profile retrieval and update endpoints."""

    def setUp(self):
        self.app = create_app("testing")
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Trekker User
        self.trekker = User(
            full_name="Rohan Trekker",
            email="rohan@test.local",
            contact_number="+91 9876543210",
            role="Trekker",
            status="Active"
        )
        self.trekker.set_password("SecretPass123!")

        # Inactive Trekker
        self.inactive_trekker = User(
            full_name="Inactive Trekker",
            email="inactive@test.local",
            role="Trekker",
            status="Inactive"
        )
        self.inactive_trekker.set_password("SecretPass123!")

        # Admin
        self.admin = User(
            full_name="System Admin",
            email="admin@test.local",
            role="Admin",
            status="Active"
        )
        self.admin.set_password("AdminPass123!")

        # Staff
        self.staff = User(
            full_name="Staff Guide",
            email="staff@test.local",
            role="Trek Staff",
            status="Active"
        )
        self.staff.set_password("StaffPass123!")

        db.session.add_all([self.trekker, self.inactive_trekker, self.admin, self.staff])
        db.session.commit()

        # Staff profile
        profile = StaffProfile(user_id=self.staff.id, specialization="High Altitude", experience_years=4)
        db.session.add(profile)
        db.session.commit()

        self.trekker_token = self._get_token("rohan@test.local", "SecretPass123!")
        self.admin_token = self._get_token("admin@test.local", "AdminPass123!")
        self.staff_token = self._get_token("staff@test.local", "StaffPass123!")

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

    def test_active_trekker_can_retrieve_profile(self):
        """Verify active Trekker can retrieve their profile without exposing password_hash."""
        res = self.client.get("/api/trekker/profile", headers=self._auth(self.trekker_token))
        self.assertEqual(res.status_code, 200)
        data = res.get_json()["data"]

        self.assertEqual(data["full_name"], "Rohan Trekker")
        self.assertEqual(data["email"], "rohan@test.local")
        self.assertEqual(data["contact_number"], "+91 9876543210")
        self.assertEqual(data["role"], "Trekker")
        self.assertNotIn("password_hash", data)

    def test_admin_and_staff_cannot_access_trekker_profile(self):
        """Verify Admin and Trek Staff are rejected on Trekker-only profile endpoint (HTTP 403)."""
        res_admin = self.client.get("/api/trekker/profile", headers=self._auth(self.admin_token))
        self.assertEqual(res_admin.status_code, 403)

        res_staff = self.client.get("/api/trekker/profile", headers=self._auth(self.staff_token))
        self.assertEqual(res_staff.status_code, 403)

    def test_unauthenticated_profile_access_rejected(self):
        """Verify requests without JWT return HTTP 401."""
        res = self.client.get("/api/trekker/profile")
        self.assertEqual(res.status_code, 401)

    def test_update_profile_permitted_fields(self):
        """Verify Trekker can update full_name and contact_number."""
        res = self.client.put(
            "/api/trekker/profile",
            headers=self._auth(self.trekker_token),
            json={
                "full_name": "Rohan Sharma",
                "contact_number": "+91 9111122223"
            }
        )
        self.assertEqual(res.status_code, 200)
        data = res.get_json()["data"]
        self.assertEqual(data["full_name"], "Rohan Sharma")
        self.assertEqual(data["contact_number"], "+91 9111122223")

        # Verify DB updated
        user = db.session.get(User, self.trekker.id)
        self.assertEqual(user.full_name, "Rohan Sharma")
        self.assertEqual(user.contact_number, "+91 9111122223")

    def test_update_profile_rejects_role_and_status_mutation(self):
        """Verify attempts to mutate role or status return HTTP 400."""
        # Attempt role escalation
        res_role = self.client.put(
            "/api/trekker/profile",
            headers=self._auth(self.trekker_token),
            json={"role": "Admin"}
        )
        self.assertEqual(res_role.status_code, 400)
        self.assertIn("Role modification", res_role.get_json()["message"])

        # Attempt status modification
        res_status = self.client.put(
            "/api/trekker/profile",
            headers=self._auth(self.trekker_token),
            json={"status": "Blacklisted"}
        )
        self.assertEqual(res_status.status_code, 400)
        self.assertIn("Status modification", res_status.get_json()["message"])

    def test_update_profile_validation_errors(self):
        """Verify empty full name and invalid phone format return HTTP 400."""
        # Empty name
        res_empty = self.client.put(
            "/api/trekker/profile",
            headers=self._auth(self.trekker_token),
            json={"full_name": "   "}
        )
        self.assertEqual(res_empty.status_code, 400)

        # Invalid phone
        res_phone = self.client.put(
            "/api/trekker/profile",
            headers=self._auth(self.trekker_token),
            json={"contact_number": "invalid-letters"}
        )
        self.assertEqual(res_phone.status_code, 400)


if __name__ == "__main__":
    unittest.main()

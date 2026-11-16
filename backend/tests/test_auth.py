"""Automated tests for user registration, authentication, login, and profile retrieval."""
import json
import unittest
from backend.app import create_app
from backend.app.extensions import db
from backend.app.models import User, StaffProfile


class AuthTestCase(unittest.TestCase):
    """Test suite for authentication endpoints."""

    def setUp(self):
        """Configure test client and in-memory database."""
        self.app = create_app("testing")
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        """Clean up database session and tables."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # --- Registration Tests (1 - 7) ---

    def test_01_successful_trekker_registration(self):
        """1. Verify successful Trekker registration with valid fields."""
        payload = {
            "full_name": "Trekker One",
            "email": "trekker1@example.com",
            "password": "Password123!",
            "confirm_password": "Password123!",
            "contact_number": "+91-9876543210"
        }
        res = self.client.post("/api/auth/register", json=payload)
        data = res.get_json()

        self.assertEqual(res.status_code, 201)
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["email"], "trekker1@example.com")
        self.assertEqual(data["data"]["role"], "Trekker")
        self.assertEqual(data["data"]["status"], "Active")
        self.assertNotIn("password_hash", data["data"])

    def test_02_duplicate_email_registration_rejected(self):
        """2. Verify that registration fails if the email already exists."""
        user = User(
            full_name="Existing User",
            email="existing@example.com",
            role="Trekker",
            status="Active"
        )
        user.set_password("OldPassword123!")
        db.session.add(user)
        db.session.commit()

        payload = {
            "full_name": "New Person",
            "email": "existing@example.com",
            "password": "NewPassword123!",
            "confirm_password": "NewPassword123!"
        }
        res = self.client.post("/api/auth/register", json=payload)
        data = res.get_json()

        self.assertEqual(res.status_code, 409)
        self.assertFalse(data["success"])
        self.assertIn("already exists", data["message"])

    def test_03_missing_required_fields_rejected(self):
        """3. Verify missing required fields are rejected with HTTP 400."""
        payload = {
            "full_name": "",
            "email": "",
            "password": "",
            "confirm_password": ""
        }
        res = self.client.post("/api/auth/register", json=payload)
        data = res.get_json()

        self.assertEqual(res.status_code, 400)
        self.assertFalse(data["success"])
        self.assertIn("full_name", data["errors"])
        self.assertIn("email", data["errors"])
        self.assertIn("password", data["errors"])

    def test_04_password_and_confirmation_mismatch_rejected(self):
        """4. Verify password and confirm password mismatch is rejected."""
        payload = {
            "full_name": "Mismatch Tester",
            "email": "mismatch@example.com",
            "password": "Password123!",
            "confirm_password": "DifferentPassword!"
        }
        res = self.client.post("/api/auth/register", json=payload)
        data = res.get_json()

        self.assertEqual(res.status_code, 400)
        self.assertFalse(data["success"])
        self.assertIn("confirm_password", data["errors"])

    def test_05_password_hashing_verification(self):
        """5. Verify password is securely hashed and plain-text is never stored."""
        payload = {
            "full_name": "Hash Tester",
            "email": "hash@example.com",
            "password": "SecretPassword123!",
            "confirm_password": "SecretPassword123!"
        }
        res = self.client.post("/api/auth/register", json=payload)
        self.assertEqual(res.status_code, 201)

        user = User.query.filter_by(email="hash@example.com").first()
        self.assertIsNotNone(user)
        self.assertNotEqual(user.password_hash, "SecretPassword123!")
        self.assertTrue(user.check_password("SecretPassword123!"))
        self.assertFalse(user.check_password("WrongSecret"))

    def test_06_attempted_admin_role_escalation_rejected(self):
        """6. Verify client cannot escalate role to Admin on registration."""
        payload = {
            "full_name": "Escalation Tester",
            "email": "fakeadmin@example.com",
            "password": "Password123!",
            "confirm_password": "Password123!",
            "role": "Admin"
        }
        res = self.client.post("/api/auth/register", json=payload)
        self.assertEqual(res.status_code, 403)
        self.assertFalse(res.get_json()["success"])

        # Confirm user was not created
        self.assertIsNone(User.query.filter_by(email="fakeadmin@example.com").first())

    def test_07_attempted_staff_role_escalation_rejected(self):
        """7. Verify client cannot escalate role to Trek Staff on registration."""
        payload = {
            "full_name": "Escalation Staff",
            "email": "fakestaff@example.com",
            "password": "Password123!",
            "confirm_password": "Password123!",
            "role": "Trek Staff"
        }
        res = self.client.post("/api/auth/register", json=payload)
        self.assertEqual(res.status_code, 403)
        self.assertFalse(res.get_json()["success"])

        # Confirm user was not created
        self.assertIsNone(User.query.filter_by(email="fakestaff@example.com").first())

    # --- Login Tests (8 - 14) ---

    def test_08_successful_admin_login(self):
        """8. Verify Admin can log in and receives JWT access token."""
        admin = User(
            full_name="System Administrator",
            email="admin@trekkingapp.local",
            role="Admin",
            status="Active"
        )
        admin.set_password("AdminPass123!")
        db.session.add(admin)
        db.session.commit()

        res = self.client.post("/api/auth/login", json={
            "email": "admin@trekkingapp.local",
            "password": "AdminPass123!"
        })
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertIn("access_token", data["data"])
        self.assertEqual(data["data"]["user"]["role"], "Admin")
        self.assertEqual(data["data"]["user"]["email"], "admin@trekkingapp.local")

    def test_09_successful_trek_staff_login(self):
        """9. Verify Trek Staff (with staff profile) can log in successfully."""
        staff = User(
            full_name="Alex Staff",
            email="staff@trekkingapp.local",
            role="Trek Staff",
            status="Active"
        )
        staff.set_password("StaffPass123!")
        db.session.add(staff)
        db.session.commit()

        profile = StaffProfile(user=staff, specialization="High Altitude", experience_years=4)
        db.session.add(profile)
        db.session.commit()

        res = self.client.post("/api/auth/login", json={
            "email": "staff@trekkingapp.local",
            "password": "StaffPass123!"
        })
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertIn("access_token", data["data"])
        self.assertEqual(data["data"]["user"]["role"], "Trek Staff")

    def test_10_successful_trekker_login(self):
        """10. Verify Trekker can log in successfully."""
        trekker = User(
            full_name="Sam Trekker",
            email="sam@example.com",
            role="Trekker",
            status="Active"
        )
        trekker.set_password("TrekkerPass123!")
        db.session.add(trekker)
        db.session.commit()

        res = self.client.post("/api/auth/login", json={
            "email": "sam@example.com",
            "password": "TrekkerPass123!"
        })
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertIn("access_token", data["data"])
        self.assertEqual(data["data"]["user"]["role"], "Trekker")

    def test_11_invalid_password_rejected(self):
        """11. Verify invalid password returns 401 generic error."""
        user = User(
            full_name="User Test",
            email="user@example.com",
            role="Trekker",
            status="Active"
        )
        user.set_password("CorrectPassword!")
        db.session.add(user)
        db.session.commit()

        res = self.client.post("/api/auth/login", json={
            "email": "user@example.com",
            "password": "WrongPassword!"
        })
        self.assertEqual(res.status_code, 401)
        self.assertFalse(res.get_json()["success"])
        self.assertEqual(res.get_json()["message"], "Invalid email or password.")

    def test_12_unknown_email_rejected(self):
        """12. Verify unknown email returns generic 401 error."""
        res = self.client.post("/api/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "AnyPassword123!"
        })
        self.assertEqual(res.status_code, 401)
        self.assertFalse(res.get_json()["success"])
        self.assertEqual(res.get_json()["message"], "Invalid email or password.")

    def test_13_inactive_account_rejected(self):
        """13. Verify Inactive accounts are rejected with HTTP 403."""
        inactive_user = User(
            full_name="Inactive Person",
            email="inactive@example.com",
            role="Trekker",
            status="Inactive"
        )
        inactive_user.set_password("Password123!")
        db.session.add(inactive_user)
        db.session.commit()

        res = self.client.post("/api/auth/login", json={
            "email": "inactive@example.com",
            "password": "Password123!"
        })
        self.assertEqual(res.status_code, 403)
        self.assertFalse(res.get_json()["success"])
        self.assertIn("inactive", res.get_json()["message"].lower())

    def test_14_blacklisted_account_rejected(self):
        """14. Verify Blacklisted accounts are rejected with HTTP 403."""
        banned_user = User(
            full_name="Banned Person",
            email="banned@example.com",
            role="Trekker",
            status="Blacklisted"
        )
        banned_user.set_password("Password123!")
        db.session.add(banned_user)
        db.session.commit()

        res = self.client.post("/api/auth/login", json={
            "email": "banned@example.com",
            "password": "Password123!"
        })
        self.assertEqual(res.status_code, 403)
        self.assertFalse(res.get_json()["success"])
        self.assertIn("blacklisted", res.get_json()["message"].lower())

    # --- Profile Retrieval Test (/api/auth/me) ---

    def test_get_current_user_profile(self):
        """Verify /api/auth/me returns the authenticated user's profile."""
        user = User(
            full_name="Me Tester",
            email="me@example.com",
            role="Trekker",
            status="Active"
        )
        user.set_password("Pass123!")
        db.session.add(user)
        db.session.commit()

        # Login to obtain token
        login_res = self.client.post("/api/auth/login", json={
            "email": "me@example.com",
            "password": "Pass123!"
        })
        token = login_res.get_json()["data"]["access_token"]

        # Call /api/auth/me with Bearer token
        res = self.client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["user"]["email"], "me@example.com")
        self.assertNotIn("password_hash", data["data"]["user"])


if __name__ == "__main__":
    unittest.main()


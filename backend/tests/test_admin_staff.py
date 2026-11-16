"""
test_admin_staff.py - Automated tests for Admin Staff Management APIs.
Covers:
- Test 11: Admin can create Trek Staff account with profile (atomic).
- Test 12: Staff profile auto-created on staff account creation.
- Test 13: Duplicate email for staff registration rejected.
- Test 14: Staff password is securely hashed.
- Test 15: Admin can update staff profile / user info.
- Test 16: Admin can change staff status (Active, Inactive, Blacklisted).
- Test 17: Attempt to assign invalid roles or create staff with invalid data handled appropriately.
"""

import json
import unittest
from backend.app import create_app
from backend.app.extensions import db
from backend.app.models.user import User
from backend.app.models.staff_profile import StaffProfile


class AdminStaffTestCase(unittest.TestCase):
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

    def test_11_and_12_admin_creates_staff_with_atomic_profile(self):
        """11 & 12. Admin can create Trek Staff with profile atomically."""
        payload = {
            "full_name": "Nawang Dorje",
            "email": "nawang@trekking.local",
            "password": "SecureStaffPass123!",
            "specialization": "Winter Expeditions",
            "experience_years": 8,
            "phone_number": "9811223344",
            "emergency_contact": "9811223300"
        }

        res = self.client.post(
            "/api/admin/staff",
            data=json.dumps(payload),
            headers=self.admin_headers,
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 201)
        data = json.loads(res.data)
        self.assertEqual(data["data"]["role"], "Trek Staff")
        self.assertEqual(data["data"]["email"], "nawang@trekking.local")
        self.assertEqual(data["data"]["staff_profile"]["specialization"], "Winter Expeditions")
        self.assertEqual(data["data"]["staff_profile"]["experience_years"], 8)

        # Verify DB directly
        staff_user = User.query.filter_by(email="nawang@trekking.local").first()
        self.assertIsNotNone(staff_user)
        self.assertEqual(staff_user.role, "Trek Staff")
        self.assertIsNotNone(staff_user.staff_profile)
        self.assertEqual(staff_user.staff_profile.experience_years, 8)

    def test_13_duplicate_email_for_staff_rejected(self):
        """13. Duplicate email for staff registration is rejected with HTTP 409."""
        existing = User(
            full_name="Existing User",
            email="existing@test.local",
            role="Trekker",
            status="Active"
        )
        existing.set_password("Pass123!")
        db.session.add(existing)
        db.session.commit()

        payload = {
            "full_name": "Staff With Duplicate Email",
            "email": "existing@test.local",
            "password": "NewStaffPass123!",
            "specialization": "Rock Climbing"
        }

        res = self.client.post(
            "/api/admin/staff",
            data=json.dumps(payload),
            headers=self.admin_headers,
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 409)

    def test_14_staff_password_is_securely_hashed(self):
        """14. Staff password is never stored in plain text and hashes properly."""
        raw_password = "SecretPassword123!"
        payload = {
            "full_name": "Tenzing Norgay",
            "email": "tenzing@himalaya.local",
            "password": raw_password,
            "specialization": "Summit Leader"
        }

        res = self.client.post(
            "/api/admin/staff",
            data=json.dumps(payload),
            headers=self.admin_headers,
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 201)

        user = User.query.filter_by(email="tenzing@himalaya.local").first()
        self.assertNotEqual(user.password_hash, raw_password)
        self.assertTrue(user.check_password(raw_password))
        self.assertFalse(user.check_password("WrongPassword!"))

    def test_15_admin_can_update_staff_profile(self):
        """15. Admin can update staff user details and profile."""
        staff = User(
            full_name="Pasang Lhamu",
            email="pasang@test.local",
            role="Trek Staff",
            status="Active"
        )
        staff.set_password("Pass123!")
        db.session.add(staff)
        db.session.flush()

        staff.contact_number = "9123456789"
        profile = StaffProfile(
            user_id=staff.id,
            specialization="Alpine Guide",
            experience_years=3
        )
        db.session.add(profile)
        db.session.commit()

        update_payload = {
            "full_name": "Pasang Lhamu Sherpa",
            "specialization": "High Altitude Expeditions",
            "experience_years": 4
        }

        res = self.client.put(
            f"/api/admin/staff/{staff.id}",
            data=json.dumps(update_payload),
            headers=self.admin_headers,
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data["data"]["full_name"], "Pasang Lhamu Sherpa")
        self.assertEqual(data["data"]["staff_profile"]["specialization"], "High Altitude Expeditions")
        self.assertEqual(data["data"]["staff_profile"]["experience_years"], 4)

    def test_16_admin_can_change_staff_status(self):
        """16. Admin can change staff status to Active, Inactive, Blacklisted."""
        staff = User(
            full_name="Staff One",
            email="staff1@test.local",
            role="Trek Staff",
            status="Active"
        )
        staff.set_password("Pass123!")
        db.session.add(staff)
        db.session.flush()
        db.session.add(StaffProfile(user_id=staff.id, specialization="Tracking"))
        db.session.commit()

        # Update to Inactive
        res = self.client.patch(
            f"/api/admin/staff/{staff.id}/status",
            data=json.dumps({"status": "Inactive"}),
            headers=self.admin_headers,
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(json.loads(res.data)["data"]["status"], "Inactive")

        # Update to Blacklisted
        res = self.client.patch(
            f"/api/admin/staff/{staff.id}/status",
            data=json.dumps({"status": "Blacklisted"}),
            headers=self.admin_headers,
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(json.loads(res.data)["data"]["status"], "Blacklisted")

        # Invalid status
        res = self.client.patch(
            f"/api/admin/staff/{staff.id}/status",
            data=json.dumps({"status": "Suspended"}),
            headers=self.admin_headers,
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 400)

    def test_17_invalid_staff_creation_data_rejected(self):
        """17. Creating staff with missing fields or negative experience is rejected."""
        # Missing required password
        res = self.client.post(
            "/api/admin/staff",
            data=json.dumps({"full_name": "No Password", "email": "nopass@test.local"}),
            headers=self.admin_headers,
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 400)

        # Negative experience
        res = self.client.post(
            "/api/admin/staff",
            data=json.dumps({
                "full_name": "Neg Exp",
                "email": "negexp@test.local",
                "password": "ValidPass123!",
                "experience_years": -3
            }),
            headers=self.admin_headers,
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 400)


if __name__ == "__main__":
    unittest.main()

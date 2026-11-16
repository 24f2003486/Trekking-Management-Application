"""
test_admin_users.py - Automated tests for Admin Trekker User Management APIs.
Covers:
- Test 18: Admin can list Trekkers with pagination.
- Test 19: Admin can search Trekkers by name or email.
- Test 20: Admin can update permitted Trekker fields (full_name, phone, emergency_contact).
- Test 21: Admin can deactivate Trekker (status to Inactive).
- Test 22: Blacklisted Trekker cannot log in (HTTP 403).
- Test 23: Role escalation/mutation forbidden; cannot modify Admin accounts via user endpoint.
"""

import json
import unittest
from backend.app import create_app
from backend.app.extensions import db
from backend.app.models.user import User


class AdminUsersTestCase(unittest.TestCase):
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

        # Trekkers
        self.trekker1 = User(
            full_name="Alice Smith",
            email="alice@example.local",
            role="Trekker",
            status="Active"
        )
        self.trekker1.set_password("AlicePass123!")

        self.trekker2 = User(
            full_name="Bob Jones",
            email="bob@example.local",
            role="Trekker",
            status="Active"
        )
        self.trekker2.set_password("BobPass123!")

        db.session.add_all([self.trekker1, self.trekker2])
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

    def test_18_admin_can_list_trekkers_with_pagination(self):
        """18. Admin can list Trekkers with pagination."""
        for i in range(15):
            u = User(
                full_name=f"Trekker Extra {i}",
                email=f"trekker{i}@test.local",
                role="Trekker",
                status="Active"
            )
            u.set_password("Pass123!")
            db.session.add(u)
        db.session.commit()

        res = self.client.get("/api/admin/users?page=1&per_page=10", headers=self.admin_headers)
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(len(data["data"]["users"]), 10)
        self.assertEqual(data["data"]["pagination"]["total_items"], 17)  # 2 + 15
        self.assertEqual(data["data"]["pagination"]["total_pages"], 2)

    def test_19_admin_can_search_trekkers_by_name_or_email(self):
        """19. Admin can search Trekkers by name or email."""
        res = self.client.get("/api/admin/users?search=Alice", headers=self.admin_headers)
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(len(data["data"]["users"]), 1)
        self.assertEqual(data["data"]["users"][0]["email"], "alice@example.local")

        res_email = self.client.get("/api/admin/users?search=bob@example", headers=self.admin_headers)
        self.assertEqual(res_email.status_code, 200)
        data_email = json.loads(res_email.data)
        self.assertEqual(len(data_email["data"]["users"]), 1)
        self.assertEqual(data_email["data"]["users"][0]["full_name"], "Bob Jones")

    def test_20_admin_can_update_permitted_trekker_fields(self):
        """20. Admin can update permitted Trekker fields (e.g. name, phone, emergency contact)."""
        payload = {
            "full_name": "Alice Wonderland",
            "phone_number": "9988776655"
        }
        res = self.client.put(
            f"/api/admin/users/{self.trekker1.id}",
            data=json.dumps(payload),
            headers=self.admin_headers,
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data["data"]["full_name"], "Alice Wonderland")
        self.assertEqual(data["data"]["phone_number"], "9988776655")

    def test_21_admin_can_deactivate_trekker(self):
        """21. Admin can change Trekker status to Inactive."""
        res = self.client.patch(
            f"/api/admin/users/{self.trekker1.id}/status",
            data=json.dumps({"status": "Inactive"}),
            headers=self.admin_headers,
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(json.loads(res.data)["data"]["status"], "Inactive")

        # Inactive user cannot log in
        login_res = self.client.post(
            "/api/auth/login",
            data=json.dumps({"email": "alice@example.local", "password": "AlicePass123!"}),
            content_type="application/json"
        )
        self.assertEqual(login_res.status_code, 403)

    def test_22_blacklisted_trekker_cannot_access_or_login(self):
        """22. Blacklisted user cannot log in."""
        res = self.client.patch(
            f"/api/admin/users/{self.trekker2.id}/status",
            data=json.dumps({"status": "Blacklisted"}),
            headers=self.admin_headers,
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)

        login_res = self.client.post(
            "/api/auth/login",
            data=json.dumps({"email": "bob@example.local", "password": "BobPass123!"}),
            content_type="application/json"
        )
        self.assertEqual(login_res.status_code, 403)

    def test_23_role_escalation_forbidden_and_admin_cannot_be_modified(self):
        """23. Cannot change user role via update; cannot modify Admin accounts via user endpoint."""
        # Attempt to change role of trekker
        payload = {"role": "Admin"}
        res = self.client.put(
            f"/api/admin/users/{self.trekker1.id}",
            data=json.dumps(payload),
            headers=self.admin_headers,
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 400)

        # Attempt to modify Admin user through /api/admin/users/<admin_id>
        res_admin = self.client.put(
            f"/api/admin/users/{self.admin.id}",
            data=json.dumps({"full_name": "Hacked Admin"}),
            headers=self.admin_headers,
            content_type="application/json"
        )
        self.assertEqual(res_admin.status_code, 403)


if __name__ == "__main__":
    unittest.main()

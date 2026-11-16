"""
test_admin_assignments.py - Automated tests for Admin Trek Staff Assignment APIs.
Covers:
- Test 24: Admin can assign active Trek Staff to trek.
- Test 25: Assigning non-staff user or inactive staff to trek is rejected.
- Test 26: Admin can unassign (set null) or reassign staff to a trek.
"""

import json
import unittest
from datetime import date, timedelta
from backend.app import create_app
from backend.app.extensions import db
from backend.app.models.user import User
from backend.app.models.staff_profile import StaffProfile
from backend.app.models.trek import Trek


class AdminAssignmentsTestCase(unittest.TestCase):
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

        # Staff 1
        self.staff1 = User(
            full_name="Guide One",
            email="guide1@test.local",
            role="Trek Staff",
            status="Active"
        )
        self.staff1.set_password("Pass123!")
        db.session.add(self.staff1)
        db.session.flush()
        db.session.add(StaffProfile(user_id=self.staff1.id, specialization="Glaciers"))

        # Staff 2
        self.staff2 = User(
            full_name="Guide Two",
            email="guide2@test.local",
            role="Trek Staff",
            status="Active"
        )
        self.staff2.set_password("Pass123!")
        db.session.add(self.staff2)
        db.session.flush()
        db.session.add(StaffProfile(user_id=self.staff2.id, specialization="Rock Climbing"))

        # Inactive Staff
        self.inactive_staff = User(
            full_name="Inactive Guide",
            email="inactive@test.local",
            role="Trek Staff",
            status="Inactive"
        )
        self.inactive_staff.set_password("Pass123!")
        db.session.add(self.inactive_staff)
        db.session.flush()
        db.session.add(StaffProfile(user_id=self.inactive_staff.id, specialization="Desert"))

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
            name="Valley of Flowers",
            description="UNESCO World Heritage flora trek",
            location="Uttarakhand",
            difficulty="Moderate",
            duration_days=6,
            available_slots=20,
            start_date=date.today() + timedelta(days=30),
            end_date=date.today() + timedelta(days=36)
        )
        db.session.add(self.trek)
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

    def test_24_admin_can_assign_active_staff_to_trek(self):
        """24. Admin can assign active Trek Staff to trek."""
        res = self.client.put(
            f"/api/admin/treks/{self.trek.id}/assign-staff",
            data=json.dumps({"assigned_staff_id": self.staff1.id}),
            headers=self.admin_headers,
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data["data"]["assigned_staff_id"], self.staff1.id)
        self.assertEqual(data["data"]["assigned_staff_name"], "Guide One")

    def test_25_assigning_non_staff_or_inactive_staff_rejected(self):
        """25. Assigning non-staff user or inactive staff to trek is rejected (HTTP 400)."""
        # Assign Trekker
        res = self.client.put(
            f"/api/admin/treks/{self.trek.id}/assign-staff",
            data=json.dumps({"assigned_staff_id": self.trekker.id}),
            headers=self.admin_headers,
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 400)

        # Assign Inactive Staff
        res_inact = self.client.put(
            f"/api/admin/treks/{self.trek.id}/assign-staff",
            data=json.dumps({"assigned_staff_id": self.inactive_staff.id}),
            headers=self.admin_headers,
            content_type="application/json"
        )
        self.assertEqual(res_inact.status_code, 400)

    def test_26_admin_can_unassign_or_reassign_staff(self):
        """26. Admin can reassign to another staff or unassign staff (set to None)."""
        # First assign staff1
        self.client.put(
            f"/api/admin/treks/{self.trek.id}/assign-staff",
            data=json.dumps({"assigned_staff_id": self.staff1.id}),
            headers=self.admin_headers,
            content_type="application/json"
        )

        # Reassign to staff2
        res = self.client.put(
            f"/api/admin/treks/{self.trek.id}/assign-staff",
            data=json.dumps({"assigned_staff_id": self.staff2.id}),
            headers=self.admin_headers,
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(json.loads(res.data)["data"]["assigned_staff_id"], self.staff2.id)

        # Unassign (None)
        res_unassign = self.client.put(
            f"/api/admin/treks/{self.trek.id}/assign-staff",
            data=json.dumps({"assigned_staff_id": None}),
            headers=self.admin_headers,
            content_type="application/json"
        )
        self.assertEqual(res_unassign.status_code, 200)
        self.assertIsNone(json.loads(res_unassign.data)["data"]["assigned_staff_id"])
        self.assertIsNone(json.loads(res_unassign.data)["data"]["assigned_staff_name"])


if __name__ == "__main__":
    unittest.main()

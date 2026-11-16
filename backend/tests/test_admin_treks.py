"""
test_admin_treks.py - Automated tests for Admin Trek Management APIs.
Covers:
- Test 4: Admin can create new trek.
- Test 5: Admin can update trek.
- Test 6: Admin can retrieve trek details.
- Test 7: Admin can list treks with pagination/filter/search.
- Test 8: Invalid trek data rejected (negative slots/duration, end < start, bad difficulty).
- Test 9: Trek creation/update with non-staff or invalid staff rejected.
- Test 10: Safe deletion of trek (allowed when 0 bookings, blocked when bookings exist).
"""

import json
import unittest
from datetime import date, timedelta
from backend.app import create_app
from backend.app.extensions import db
from backend.app.models.user import User
from backend.app.models.staff_profile import StaffProfile
from backend.app.models.trek import Trek
from backend.app.models.booking import Booking


class AdminTreksTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Create Admin
        self.admin = User(
            full_name="Admin Test",
            email="admin@test.local",
            role="Admin",
            status="Active"
        )
        self.admin.set_password("AdminPass123!")
        db.session.add(self.admin)

        # Create Trek Staff with profile
        self.staff = User(
            full_name="Staff Guide",
            email="guide@test.local",
            role="Trek Staff",
            status="Active",
            contact_number="9876543210"
        )
        self.staff.set_password("StaffPass123!")
        db.session.add(self.staff)
        db.session.flush()

        self.staff_profile = StaffProfile(
            user_id=self.staff.id,
            specialization="High Altitude",
            experience_years=5
        )
        db.session.add(self.staff_profile)

        # Create Trekker
        self.trekker = User(
            full_name="Trekker Joe",
            email="joe@test.local",
            role="Trekker",
            status="Active"
        )
        self.trekker.set_password("TrekkerPass123!")
        db.session.add(self.trekker)

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

    def test_04_admin_can_create_new_trek(self):
        """4. Admin can create new trek with valid fields."""
        start = (date.today() + timedelta(days=10)).isoformat()
        end = (date.today() + timedelta(days=15)).isoformat()

        payload = {
            "name": "Roopkund Mystery Lake",
            "description": "High altitude glacial lake trek in Uttarakhand.",
            "location": "Uttarakhand, Himalayas",
            "difficulty": "Hard",
            "duration_days": 6,
            "available_slots": 20,
            "start_date": start,
            "end_date": end,
            "assigned_staff_id": self.staff.id
        }

        res = self.client.post(
            "/api/admin/treks",
            data=json.dumps(payload),
            headers=self.admin_headers,
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 201)
        data = json.loads(res.data)
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["data"]["name"], "Roopkund Mystery Lake")
        self.assertEqual(data["data"]["available_slots"], 20)
        self.assertEqual(data["data"]["assigned_staff_id"], self.staff.id)

    def test_05_admin_can_update_trek(self):
        """5. Admin can update an existing trek."""
        trek = Trek(
            name="Kedarkantha Peak",
            description="Winter snow trek",
            location="Uttarakhand",
            difficulty="Easy",
            duration_days=4,
            available_slots=15,
            start_date=date.today() + timedelta(days=5),
            end_date=date.today() + timedelta(days=9)
        )
        db.session.add(trek)
        db.session.commit()

        update_payload = {
            "difficulty": "Moderate",
            "available_slots": 18,
            "assigned_staff_id": self.staff.id
        }

        res = self.client.put(
            f"/api/admin/treks/{trek.id}",
            data=json.dumps(update_payload),
            headers=self.admin_headers,
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data["data"]["difficulty"], "Moderate")
        self.assertEqual(data["data"]["available_slots"], 18)
        self.assertEqual(data["data"]["assigned_staff_id"], self.staff.id)

    def test_06_admin_can_retrieve_trek_details(self):
        """6. Admin can retrieve trek details by ID."""
        trek = Trek(
            name="Hampta Pass",
            description="Crossover trek from Kullu to Spiti",
            location="Himachal Pradesh",
            difficulty="Moderate",
            duration_days=5,
            available_slots=18,
            start_date=date.today() + timedelta(days=20),
            end_date=date.today() + timedelta(days=25),
            assigned_staff_id=self.staff.id
        )
        db.session.add(trek)
        db.session.commit()

        res = self.client.get(f"/api/admin/treks/{trek.id}", headers=self.admin_headers)
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data["data"]["id"], trek.id)
        self.assertEqual(data["data"]["name"], "Hampta Pass")
        self.assertEqual(data["data"]["assigned_staff_name"], "Staff Guide")

    def test_07_admin_can_list_treks_with_pagination_and_filters(self):
        """7. Admin can list treks with pagination, search, and difficulty/status filter."""
        for i in range(12):
            diff = "Easy" if i % 2 == 0 else "Hard"
            t = Trek(
                name=f"Trek {i:02d}",
                description="Sample trek description",
                location="Himalayas",
                difficulty=diff,
                duration_days=3,
                available_slots=10,
                start_date=date.today() + timedelta(days=i + 1),
                end_date=date.today() + timedelta(days=i + 4)
            )
            db.session.add(t)
        db.session.commit()

        # Test pagination (page 1, per_page 5)
        res = self.client.get("/api/admin/treks?page=1&per_page=5", headers=self.admin_headers)
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(len(data["data"]["treks"]), 5)
        self.assertEqual(data["data"]["pagination"]["total_items"], 12)
        self.assertEqual(data["data"]["pagination"]["total_pages"], 3)

        # Test search filter
        res = self.client.get("/api/admin/treks?search=Trek 05", headers=self.admin_headers)
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(len(data["data"]["treks"]), 1)
        self.assertEqual(data["data"]["treks"][0]["name"], "Trek 05")

        # Test difficulty filter
        res = self.client.get("/api/admin/treks?difficulty=Easy", headers=self.admin_headers)
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data["data"]["pagination"]["total_items"], 6)

    def test_08_invalid_trek_data_rejected(self):
        """8. Invalid trek data is rejected with appropriate HTTP status."""
        today = date.today()

        # End date before start date
        bad_dates = {
            "name": "Bad Dates Trek",
            "location": "North",
            "difficulty": "Easy",
            "duration_days": 3,
            "available_slots": 10,
            "start_date": (today + timedelta(days=10)).isoformat(),
            "end_date": (today + timedelta(days=5)).isoformat()
        }
        res = self.client.post("/api/admin/treks", data=json.dumps(bad_dates), headers=self.admin_headers, content_type="application/json")
        self.assertEqual(res.status_code, 400)

        # Invalid difficulty
        bad_diff = {
            "name": "Bad Difficulty Trek",
            "location": "North",
            "difficulty": "Extreme",
            "duration_days": 3,
            "available_slots": 10,
            "start_date": (today + timedelta(days=5)).isoformat(),
            "end_date": (today + timedelta(days=8)).isoformat()
        }
        res = self.client.post("/api/admin/treks", data=json.dumps(bad_diff), headers=self.admin_headers, content_type="application/json")
        self.assertEqual(res.status_code, 400)

        # Negative duration
        bad_duration = {
            "name": "Bad Duration Trek",
            "location": "North",
            "difficulty": "Easy",
            "duration_days": -2,
            "available_slots": 10,
            "start_date": (today + timedelta(days=5)).isoformat(),
            "end_date": (today + timedelta(days=8)).isoformat()
        }
        res = self.client.post("/api/admin/treks", data=json.dumps(bad_duration), headers=self.admin_headers, content_type="application/json")
        self.assertEqual(res.status_code, 400)

    def test_09_trek_creation_with_non_staff_or_invalid_staff_rejected(self):
        """9. Trek assignment to non-staff user or non-existent staff is rejected."""
        today = date.today()

        # Assign to Trekker
        payload_trekker = {
            "name": "Trekker Assigned",
            "location": "South",
            "difficulty": "Moderate",
            "duration_days": 3,
            "available_slots": 10,
            "start_date": (today + timedelta(days=5)).isoformat(),
            "end_date": (today + timedelta(days=8)).isoformat(),
            "assigned_staff_id": self.trekker.id
        }
        res = self.client.post("/api/admin/treks", data=json.dumps(payload_trekker), headers=self.admin_headers, content_type="application/json")
        self.assertEqual(res.status_code, 400)

        # Assign to non-existent ID
        payload_invalid_id = {
            "name": "Unknown Staff Trek",
            "location": "South",
            "difficulty": "Moderate",
            "duration_days": 3,
            "available_slots": 10,
            "start_date": (today + timedelta(days=5)).isoformat(),
            "end_date": (today + timedelta(days=8)).isoformat(),
            "assigned_staff_id": 9999
        }
        res = self.client.post("/api/admin/treks", data=json.dumps(payload_invalid_id), headers=self.admin_headers, content_type="application/json")
        self.assertIn(res.status_code, (400, 404))

    def test_10_safe_deletion_of_trek(self):
        """10. Safe deletion: trek with 0 bookings can be deleted; trek with bookings is rejected."""
        trek1 = Trek(
            name="Deletable Trek",
            description="Has no bookings",
            location="Valley",
            difficulty="Easy",
            duration_days=2,
            available_slots=10,
            start_date=date.today() + timedelta(days=5),
            end_date=date.today() + timedelta(days=7)
        )
        trek2 = Trek(
            name="Booked Trek",
            description="Has a booking",
            location="Peak",
            difficulty="Hard",
            duration_days=5,
            available_slots=9,
            start_date=date.today() + timedelta(days=10),
            end_date=date.today() + timedelta(days=15)
        )
        db.session.add_all([trek1, trek2])
        db.session.commit()

        # Add booking to trek2
        booking = Booking(
            user_id=self.trekker.id,
            trek_id=trek2.id,
            booking_status="Booked",
            payment_status="Paid"
        )
        db.session.add(booking)
        db.session.commit()

        # Try to delete trek2 (has booking) -> MUST FAIL HTTP 400
        res = self.client.delete(f"/api/admin/treks/{trek2.id}", headers=self.admin_headers)
        self.assertEqual(res.status_code, 400)
        self.assertIn("cannot delete", json.loads(res.data)["message"].lower())

        # Delete trek1 (0 bookings) -> MUST SUCCEED HTTP 200
        res = self.client.delete(f"/api/admin/treks/{trek1.id}", headers=self.admin_headers)
        self.assertEqual(res.status_code, 200)

        # Confirm trek1 is gone from DB
        self.assertIsNone(db.session.get(Trek, trek1.id))


if __name__ == "__main__":
    unittest.main()

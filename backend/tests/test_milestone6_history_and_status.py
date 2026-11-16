"""Automated tests for Milestone 6: Trek Booking History and Trek Status Tracking."""
from datetime import date, timedelta
import unittest
from backend.app import create_app
from backend.app.extensions import db
from backend.app.models import User, Trek, Booking, StaffProfile
from flask_jwt_extended import create_access_token


class Milestone6HistoryAndStatusTestCase(unittest.TestCase):
    """Test suite verifying Milestone 6 requirements."""

    def setUp(self):
        self.app = create_app("testing")
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Admin User
        self.admin = User(
            full_name="Admin Director",
            email="admin@trekking.local",
            role="Admin",
            status="Active"
        )
        self.admin.set_password("AdminPass123!")

        # Trek Staff 1
        self.staff1 = User(
            full_name="Staff Guide Alpha",
            email="staff1@trekking.local",
            role="Trek Staff",
            status="Active"
        )
        self.staff1.set_password("StaffPass123!")

        # Trek Staff 2
        self.staff2 = User(
            full_name="Staff Guide Beta",
            email="staff2@trekking.local",
            role="Trek Staff",
            status="Active"
        )
        self.staff2.set_password("StaffPass123!")

        # Trekker 1
        self.trekker1 = User(
            full_name="Trekker Alice",
            email="alice@test.local",
            role="Trekker",
            status="Active"
        )
        self.trekker1.set_password("AlicePass123!")

        # Trekker 2
        self.trekker2 = User(
            full_name="Trekker Bob",
            email="bob@test.local",
            role="Trekker",
            status="Active"
        )
        self.trekker2.set_password("BobPass123!")

        db.session.add_all([self.admin, self.staff1, self.staff2, self.trekker1, self.trekker2])
        db.session.commit()

        # Staff profiles
        sp1 = StaffProfile(user_id=self.staff1.id, specialization="High Altitude", experience_years=5)
        sp2 = StaffProfile(user_id=self.staff2.id, specialization="Trail Navigation", experience_years=3)
        db.session.add_all([sp1, sp2])
        db.session.commit()

        # Tokens
        self.admin_token = create_access_token(identity=str(self.admin.id))
        self.staff1_token = create_access_token(identity=str(self.staff1.id))
        self.staff2_token = create_access_token(identity=str(self.staff2.id))
        self.trekker1_token = create_access_token(identity=str(self.trekker1.id))
        self.trekker2_token = create_access_token(identity=str(self.trekker2.id))

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def _auth(self, token):
        return {"Authorization": f"Bearer {token}"}

    def _create_trek(self, name="Everest Base Trail", status="Open", progress="Not Started", slots=5, staff=None):
        trek = Trek(
            trek_name=name,
            location="Sikkim Himalayas",
            difficulty="Moderate",
            duration_days=7,
            available_slots=slots,
            status=status,
            operational_progress=progress,
            assigned_staff_id=staff.id if staff else None,
            start_date=date.today() + timedelta(days=20),
            end_date=date.today() + timedelta(days=27)
        )
        db.session.add(trek)
        db.session.commit()
        return trek

    # =========================================================================
    # 1. Booking Status & State Transitions
    # =========================================================================

    def test_booked_to_completed_after_trek_completion(self):
        """Verify active Booked reservations transition to Completed when trek operational progress is Completed."""
        trek = self._create_trek(status="Open", progress="Started", staff=self.staff1)

        # Alice and Bob book slots
        res_a = self.client.post("/api/trekker/bookings", headers=self._auth(self.trekker1_token), json={"trek_id": trek.id})
        res_b = self.client.post("/api/trekker/bookings", headers=self._auth(self.trekker2_token), json={"trek_id": trek.id})
        self.assertEqual(res_a.status_code, 201)
        self.assertEqual(res_b.status_code, 201)

        # Staff updates progress: Started -> Ongoing -> Completed
        self.client.patch(
            f"/api/staff/treks/{trek.id}/progress",
            headers=self._auth(self.staff1_token),
            json={"operational_progress": "Ongoing"}
        )
        res_comp = self.client.patch(
            f"/api/staff/treks/{trek.id}/progress",
            headers=self._auth(self.staff1_token),
            json={"operational_progress": "Completed"}
        )
        self.assertEqual(res_comp.status_code, 200)

        # Verify in database: bookings are now Completed
        bookings = Booking.query.filter_by(trek_id=trek.id).all()
        self.assertEqual(len(bookings), 2)
        for b in bookings:
            self.assertEqual(b.booking_status, "Completed")

        # Verify trek booking status was automatically closed
        updated_trek = db.session.get(Trek, trek.id)
        self.assertEqual(updated_trek.status, "Closed")
        self.assertEqual(updated_trek.operational_progress, "Completed")

    def test_cancelled_records_preserved_on_trek_completion(self):
        """Verify pre-existing Cancelled bookings remain Cancelled (intact audit history) on trek completion."""
        trek = self._create_trek(status="Open", progress="Started", staff=self.staff1)

        # Alice books and then cancels
        res_a = self.client.post("/api/trekker/bookings", headers=self._auth(self.trekker1_token), json={"trek_id": trek.id})
        self.assertEqual(res_a.status_code, 201)
        booking_id = res_a.get_json()["data"]["id"]

        res_cancel = self.client.post(f"/api/trekker/bookings/{booking_id}/cancel", headers=self._auth(self.trekker1_token))
        self.assertEqual(res_cancel.status_code, 200)

        # Bob books
        res_b = self.client.post("/api/trekker/bookings", headers=self._auth(self.trekker2_token), json={"trek_id": trek.id})
        self.assertEqual(res_b.status_code, 201)

        # Staff marks Completed
        self.client.patch(
            f"/api/staff/treks/{trek.id}/progress",
            headers=self._auth(self.staff1_token),
            json={"operational_progress": "Ongoing"}
        )
        self.client.patch(
            f"/api/staff/treks/{trek.id}/progress",
            headers=self._auth(self.staff1_token),
            json={"operational_progress": "Completed"}
        )

        # Check bookings: Alice's booking remains Cancelled; Bob's is Completed
        b_alice = db.session.get(Booking, booking_id)
        self.assertEqual(b_alice.booking_status, "Cancelled")

        b_bob = Booking.query.filter_by(user_id=self.trekker2.id, trek_id=trek.id).first()
        self.assertEqual(b_bob.booking_status, "Completed")

    def test_completed_booking_cannot_be_reverted(self):
        """Verify Completed booking records cannot be reverted to Booked or Cancelled."""
        trek = self._create_trek(status="Completed", progress="Completed", staff=self.staff1)
        booking = Booking(
            user_id=self.trekker1.id,
            trek_id=trek.id,
            booking_status="Completed",
            payment_status="Paid"
        )
        db.session.add(booking)
        db.session.commit()

        # Attempt to revert in model to Booked
        with self.assertRaises(ValueError):
            booking.booking_status = "Booked"

        # Attempt to revert in model to Cancelled
        with self.assertRaises(ValueError):
            booking.booking_status = "Cancelled"

    def test_cancelled_booking_cannot_be_reverted(self):
        """Verify Cancelled booking records cannot be reverted to Booked or Completed."""
        trek = self._create_trek(status="Open", staff=self.staff1)
        booking = Booking(
            user_id=self.trekker1.id,
            trek_id=trek.id,
            booking_status="Cancelled",
            payment_status="Refunded"
        )
        db.session.add(booking)
        db.session.commit()

        # Attempt to revert in model to Booked
        with self.assertRaises(ValueError):
            booking.booking_status = "Booked"

        # Attempt to revert in model to Completed
        with self.assertRaises(ValueError):
            booking.booking_status = "Completed"

    def test_trekker_can_cancel_active_booking_and_rebook(self):
        """Verify Trekker can cancel an active booking, which releases capacity and allows subsequent rebooking."""
        trek = self._create_trek(status="Open", slots=1, staff=self.staff1)

        # 1. Alice books the only available slot
        res1 = self.client.post("/api/trekker/bookings", headers=self._auth(self.trekker1_token), json={"trek_id": trek.id})
        self.assertEqual(res1.status_code, 201)
        b1_id = res1.get_json()["data"]["id"]

        # Trek is now full; Bob's booking is rejected
        res_bob_fail = self.client.post("/api/trekker/bookings", headers=self._auth(self.trekker2_token), json={"trek_id": trek.id})
        self.assertEqual(res_bob_fail.status_code, 409)

        # 2. Alice cancels her booking
        res_cancel = self.client.post(f"/api/trekker/bookings/{b1_id}/cancel", headers=self._auth(self.trekker1_token))
        self.assertEqual(res_cancel.status_code, 200)
        self.assertEqual(res_cancel.get_json()["data"]["booking"]["booking_status"], "Cancelled")

        # 3. Bob can now book the freed slot
        res_bob_ok = self.client.post("/api/trekker/bookings", headers=self._auth(self.trekker2_token), json={"trek_id": trek.id})
        self.assertEqual(res_bob_ok.status_code, 201)

        # Both records exist in database (historical preservation)
        self.assertEqual(Booking.query.filter_by(trek_id=trek.id).count(), 2)

    def test_trekker_cannot_cancel_completed_booking_or_completed_trek(self):
        """Verify attempting to cancel a Completed booking returns HTTP 400."""
        trek = self._create_trek(status="Completed", progress="Completed", staff=self.staff1)
        booking = Booking(
            user_id=self.trekker1.id,
            trek_id=trek.id,
            booking_status="Completed",
            payment_status="Paid"
        )
        db.session.add(booking)
        db.session.commit()

        res = self.client.post(f"/api/trekker/bookings/{booking.id}/cancel", headers=self._auth(self.trekker1_token))
        self.assertEqual(res.status_code, 400)
        self.assertIn("Completed bookings cannot be cancelled", res.get_json()["message"])

    def test_trekker_cannot_cancel_another_user_booking(self):
        """Verify Trekker A cannot cancel Trekker B's booking (HTTP 403 Forbidden)."""
        trek = self._create_trek(status="Open", slots=5, staff=self.staff1)
        res_bob = self.client.post("/api/trekker/bookings", headers=self._auth(self.trekker2_token), json={"trek_id": trek.id})
        self.assertEqual(res_bob.status_code, 201)
        bob_booking_id = res_bob.get_json()["data"]["id"]

        # Alice attempts to cancel Bob's booking
        res_alice_attack = self.client.post(f"/api/trekker/bookings/{bob_booking_id}/cancel", headers=self._auth(self.trekker1_token))
        self.assertEqual(res_alice_attack.status_code, 403)

    # =========================================================================
    # 2. Trek Status Tracking & Lifecycle
    # =========================================================================

    def test_pending_and_approved_treks_cannot_be_booked(self):
        """Verify Pending and Approved treks cannot accept bookings."""
        trek_pending = self._create_trek(name="Pending Ridge", status="Pending", slots=10)
        trek_approved = self._create_trek(name="Approved Peak", status="Approved", slots=10)

        res_p = self.client.post("/api/trekker/bookings", headers=self._auth(self.trekker1_token), json={"trek_id": trek_pending.id})
        self.assertEqual(res_p.status_code, 400)
        self.assertIn("not open for bookings", res_p.get_json()["message"])

        res_a = self.client.post("/api/trekker/bookings", headers=self._auth(self.trekker1_token), json={"trek_id": trek_approved.id})
        self.assertEqual(res_a.status_code, 400)
        self.assertIn("not open for bookings", res_a.get_json()["message"])

    def test_closed_and_completed_treks_cannot_be_booked(self):
        """Verify Closed and Completed treks reject booking attempts."""
        trek_closed = self._create_trek(name="Closed Pass", status="Closed", slots=10)
        trek_completed = self._create_trek(name="Completed Summit", status="Completed", progress="Completed", slots=10)

        res_c = self.client.post("/api/trekker/bookings", headers=self._auth(self.trekker1_token), json={"trek_id": trek_closed.id})
        self.assertEqual(res_c.status_code, 400)

        res_comp = self.client.post("/api/trekker/bookings", headers=self._auth(self.trekker1_token), json={"trek_id": trek_completed.id})
        self.assertEqual(res_comp.status_code, 400)

    def test_completed_trek_cannot_be_reopened(self):
        """Verify completed treks cannot be reopened to Open, Pending, Approved or Closed by Admin or Staff."""
        trek = self._create_trek(name="Finished Circuit", status="Completed", progress="Completed", staff=self.staff1)

        # Admin attempts to reopen to Open
        res_admin_open = self.client.put(
            f"/api/admin/treks/{trek.id}",
            headers=self._auth(self.admin_token),
            json={"status": "Open"}
        )
        self.assertEqual(res_admin_open.status_code, 400)
        self.assertIn("Completed treks cannot be reopened", str(res_admin_open.get_json()))

        # Admin attempts to revert progress to Ongoing
        res_admin_prog = self.client.put(
            f"/api/admin/treks/{trek.id}",
            headers=self._auth(self.admin_token),
            json={"operational_progress": "Ongoing"}
        )
        self.assertEqual(res_admin_prog.status_code, 400)

        # Staff attempts to reopen
        res_staff_status = self.client.patch(
            f"/api/staff/treks/{trek.id}/status",
            headers=self._auth(self.staff1_token),
            json={"status": "Open"}
        )
        self.assertEqual(res_staff_status.status_code, 400)

        # Staff attempts to revert progress
        res_staff_prog = self.client.patch(
            f"/api/staff/treks/{trek.id}/progress",
            headers=self._auth(self.staff1_token),
            json={"operational_progress": "Ongoing"}
        )
        self.assertEqual(res_staff_prog.status_code, 400)

    # =========================================================================
    # 3. Role-Based Historical Access
    # =========================================================================

    def test_admin_can_view_all_historical_bookings_and_search(self):
        """Verify Admin can view and filter all bookings (Booked, Cancelled, Completed) and search by ID/name."""
        trek = self._create_trek(name="Valley of Flowers", status="Open", slots=10, staff=self.staff1)

        # Alice: Booked -> Cancelled
        res_a = self.client.post("/api/trekker/bookings", headers=self._auth(self.trekker1_token), json={"trek_id": trek.id})
        a_id = res_a.get_json()["data"]["id"]
        self.client.post(f"/api/trekker/bookings/{a_id}/cancel", headers=self._auth(self.trekker1_token))

        # Bob: Booked -> Completed
        res_b = self.client.post("/api/trekker/bookings", headers=self._auth(self.trekker2_token), json={"trek_id": trek.id})
        b_id = res_b.get_json()["data"]["id"]
        b_obj = db.session.get(Booking, b_id)
        b_obj.booking_status = "Completed"
        db.session.commit()

        # Admin views all
        res_all = self.client.get("/api/admin/bookings", headers=self._auth(self.admin_token))
        self.assertEqual(res_all.status_code, 200)
        self.assertEqual(res_all.get_json()["data"]["pagination"]["total"], 2)

        # Admin filters Cancelled
        res_c = self.client.get("/api/admin/bookings?status=Cancelled", headers=self._auth(self.admin_token))
        self.assertEqual(res_c.status_code, 200)
        self.assertEqual(len(res_c.get_json()["data"]["bookings"]), 1)
        self.assertEqual(res_c.get_json()["data"]["bookings"][0]["booking_status"], "Cancelled")

        # Admin filters Completed
        res_comp = self.client.get("/api/admin/bookings?status=Completed", headers=self._auth(self.admin_token))
        self.assertEqual(res_comp.status_code, 200)
        self.assertEqual(len(res_comp.get_json()["data"]["bookings"]), 1)
        self.assertEqual(res_comp.get_json()["data"]["bookings"][0]["booking_status"], "Completed")

        # Admin searches by Trekker name
        res_search_name = self.client.get("/api/admin/bookings?search=Alice", headers=self._auth(self.admin_token))
        self.assertEqual(res_search_name.status_code, 200)
        self.assertEqual(len(res_search_name.get_json()["data"]["bookings"]), 1)

        # Admin searches by Trek ID
        res_search_tid = self.client.get(f"/api/admin/bookings?search={trek.id}", headers=self._auth(self.admin_token))
        self.assertEqual(res_search_tid.status_code, 200)
        self.assertEqual(len(res_search_tid.get_json()["data"]["bookings"]), 2)

    def test_staff_can_view_assigned_trek_participants_including_history(self):
        """Verify Trek Staff can view all participant records (active, cancelled, completed) for assigned treks."""
        trek = self._create_trek(name="Staff Assigned Trek", status="Open", slots=10, staff=self.staff1)

        # Alice: Cancelled
        res_a = self.client.post("/api/trekker/bookings", headers=self._auth(self.trekker1_token), json={"trek_id": trek.id})
        a_id = res_a.get_json()["data"]["id"]
        self.client.post(f"/api/trekker/bookings/{a_id}/cancel", headers=self._auth(self.trekker1_token))

        # Bob: Active
        self.client.post("/api/trekker/bookings", headers=self._auth(self.trekker2_token), json={"trek_id": trek.id})

        res_roster = self.client.get(f"/api/staff/treks/{trek.id}/participants", headers=self._auth(self.staff1_token))
        self.assertEqual(res_roster.status_code, 200)
        data = res_roster.get_json()["data"]
        self.assertEqual(data["summary"]["total"], 2)
        self.assertEqual(data["summary"]["active"], 1)
        self.assertEqual(data["summary"]["cancelled"], 1)

    def test_staff_cannot_access_unassigned_trek_participants(self):
        """Verify Staff 2 receives HTTP 403 when attempting to access Staff 1's trek participants."""
        trek = self._create_trek(name="Staff1 Only Trek", status="Open", slots=10, staff=self.staff1)

        res = self.client.get(f"/api/staff/treks/{trek.id}/participants", headers=self._auth(self.staff2_token))
        self.assertEqual(res.status_code, 403)
        self.assertIn("not authorized", res.get_json()["message"])

    def test_trekker_can_view_only_own_booking_history(self):
        """Verify Trekker Alice can only see her own booking history and receives 403 when trying to access Bob's."""
        trek = self._create_trek(name="Shared Trail", status="Open", slots=10, staff=self.staff1)

        # Alice books
        res_a = self.client.post("/api/trekker/bookings", headers=self._auth(self.trekker1_token), json={"trek_id": trek.id})
        a_id = res_a.get_json()["data"]["id"]

        # Bob books
        res_b = self.client.post("/api/trekker/bookings", headers=self._auth(self.trekker2_token), json={"trek_id": trek.id})
        b_id = res_b.get_json()["data"]["id"]

        # Alice's history has only 1 booking
        res_history = self.client.get("/api/trekker/bookings", headers=self._auth(self.trekker1_token))
        self.assertEqual(res_history.status_code, 200)
        alice_bookings = res_history.get_json()["data"]["bookings"]
        self.assertEqual(len(alice_bookings), 1)
        self.assertEqual(alice_bookings[0]["id"], a_id)

        # Alice attempts to access Bob's booking details directly
        res_direct = self.client.get(f"/api/trekker/bookings/{b_id}", headers=self._auth(self.trekker1_token))
        self.assertEqual(res_direct.status_code, 403)

    # =========================================================================
    # 4. Data Consistency Across Roles
    # =========================================================================

    def test_data_consistency_across_admin_staff_and_trekker(self):
        """Verify end-to-end data consistency across Admin, Staff, and Trekker views on trek completion."""
        trek = self._create_trek(name="Consistency Trek", status="Open", progress="Started", slots=5, staff=self.staff1)

        # Alice books
        res_a = self.client.post("/api/trekker/bookings", headers=self._auth(self.trekker1_token), json={"trek_id": trek.id})
        a_id = res_a.get_json()["data"]["id"]

        # Bob books
        res_b = self.client.post("/api/trekker/bookings", headers=self._auth(self.trekker2_token), json={"trek_id": trek.id})
        b_id = res_b.get_json()["data"]["id"]

        # Alice cancels her reservation
        self.client.post(f"/api/trekker/bookings/{a_id}/cancel", headers=self._auth(self.trekker1_token))

        # Staff progresses trek to Completed
        self.client.patch(f"/api/staff/treks/{trek.id}/progress", headers=self._auth(self.staff1_token), json={"operational_progress": "Ongoing"})
        self.client.patch(f"/api/staff/treks/{trek.id}/progress", headers=self._auth(self.staff1_token), json={"operational_progress": "Completed"})

        # 1. Check Trekker Bob's view
        res_bob = self.client.get(f"/api/trekker/bookings/{b_id}", headers=self._auth(self.trekker2_token))
        self.assertEqual(res_bob.status_code, 200)
        bob_booking = res_bob.get_json()["data"]["booking"]
        self.assertEqual(bob_booking["booking_status"], "Completed")
        self.assertEqual(bob_booking["trek_operational_progress"], "Completed")

        # 2. Check Trekker Alice's view
        res_alice = self.client.get(f"/api/trekker/bookings/{a_id}", headers=self._auth(self.trekker1_token))
        self.assertEqual(res_alice.status_code, 200)
        alice_booking = res_alice.get_json()["data"]["booking"]
        self.assertEqual(alice_booking["booking_status"], "Cancelled")

        # 3. Check Staff Participant roster
        res_staff = self.client.get(f"/api/staff/treks/{trek.id}/participants", headers=self._auth(self.staff1_token))
        self.assertEqual(res_staff.status_code, 200)
        summary = res_staff.get_json()["data"]["summary"]
        self.assertEqual(summary["total"], 2)
        self.assertEqual(summary["cancelled"], 1)
        self.assertEqual(summary["completed"], 1)
        self.assertEqual(summary["active"], 0)

        # 4. Check Admin Historical Bookings
        res_admin = self.client.get("/api/admin/bookings", headers=self._auth(self.admin_token))
        self.assertEqual(res_admin.status_code, 200)
        admin_bookings = res_admin.get_json()["data"]["bookings"]
        statuses = [b["booking_status"] for b in admin_bookings]
        self.assertIn("Completed", statuses)
        self.assertIn("Cancelled", statuses)


if __name__ == "__main__":
    unittest.main()

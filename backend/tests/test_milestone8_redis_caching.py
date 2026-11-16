"""Comprehensive automated test suite for Milestone 8: Redis Caching and Performance Optimization."""
import time
import unittest
from datetime import date, datetime
from unittest.mock import patch
import redis
from backend.app import create_app
from backend.app.extensions import db
from backend.app.models.user import User
from backend.app.models.trek import Trek
from backend.app.models.booking import Booking
from backend.app.models.staff_profile import StaffProfile
from backend.app.services.cache_service import cache_service


class Milestone8RedisCachingTestCase(unittest.TestCase):
    """Test suite verifying Redis caching, invalidation, TTL expiry, and error tolerance."""

    def setUp(self):
        """Set up test application, clean database, and fresh cache state."""
        self.app = create_app("testing")
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Clean cache state before each test
        cache_service.clear_all()

        # Create Admin
        self.admin = User(
            full_name="Admin Director",
            email="admin.cache@test.local",
            role="Admin",
            status="Active"
        )
        self.admin.set_password("AdminPass123!")
        db.session.add(self.admin)

        # Create Staff
        self.staff = User(
            full_name="Staff Guide",
            email="staff.cache@test.local",
            role="Trek Staff",
            status="Active"
        )
        self.staff.set_password("StaffPass123!")
        db.session.add(self.staff)
        db.session.flush()

        profile = StaffProfile(user_id=self.staff.id, specialization="High Altitude", experience_years=5)
        db.session.add(profile)

        # Create Trekker 1
        self.trekker1 = User(
            full_name="Trekker Alice",
            email="alice.cache@test.local",
            role="Trekker",
            status="Active"
        )
        self.trekker1.set_password("TrekkerPass123!")
        db.session.add(self.trekker1)

        # Create Trekker 2
        self.trekker2 = User(
            full_name="Trekker Bob",
            email="bob.cache@test.local",
            role="Trekker",
            status="Active"
        )
        self.trekker2.set_password("TrekkerPass123!")
        db.session.add(self.trekker2)

        # Create sample open treks
        self.trek1 = Trek(
            trek_name="Roopkund Mystery Lake",
            location="Chamoli, Uttarakhand",
            difficulty="Hard",
            duration_days=8,
            available_slots=15,
            status="Open",
            operational_progress="Not Started",
            start_date=date(2027, 6, 1),
            end_date=date(2027, 6, 8),
            assigned_staff_id=self.staff.id
        )
        self.trek2 = Trek(
            trek_name="Hampta Pass Crossing",
            location="Manali, Himachal Pradesh",
            difficulty="Moderate",
            duration_days=5,
            available_slots=20,
            status="Open",
            operational_progress="Not Started",
            start_date=date(2027, 7, 10),
            end_date=date(2027, 7, 14),
            assigned_staff_id=self.staff.id
        )
        db.session.add_all([self.trek1, self.trek2])
        db.session.commit()

        # Tokens
        self.admin_token = self._get_token("admin.cache@test.local", "AdminPass123!")
        self.staff_token = self._get_token("staff.cache@test.local", "StaffPass123!")
        self.trekker1_token = self._get_token("alice.cache@test.local", "TrekkerPass123!")
        self.trekker2_token = self._get_token("bob.cache@test.local", "TrekkerPass123!")

    def tearDown(self):
        """Clean up database session, tables, and cache state."""
        cache_service.clear_all()
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def _get_token(self, email: str, password: str) -> str:
        """Authenticate and obtain JWT bearer token."""
        res = self.client.post("/api/auth/login", json={"email": email, "password": password})
        self.assertEqual(res.status_code, 200)
        return res.get_json()["data"]["access_token"]

    def _auth_header(self, token: str) -> dict:
        """Helper to construct Authorization bearer header."""
        return {"Authorization": f"Bearer {token}"}

    # =========================================================================
    # Test 1 & 2: Cache MISS on first request, Cache HIT on repeated request
    # =========================================================================
    def test_01_and_02_cache_miss_then_cache_hit(self):
        """Verify first request is a cache MISS and subsequent identical request is a cache HIT."""
        # 1. First request -> MISS
        res1 = self.client.get("/api/trekker/treks", headers=self._auth_header(self.trekker1_token))
        self.assertEqual(res1.status_code, 200)
        self.assertEqual(res1.headers.get("X-Cache"), "MISS")
        data1 = res1.get_json()["data"]
        self.assertEqual(len(data1["treks"]), 2)

        # 2. Second request -> HIT
        res2 = self.client.get("/api/trekker/treks", headers=self._auth_header(self.trekker1_token))
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(res2.headers.get("X-Cache"), "HIT")
        data2 = res2.get_json()["data"]
        self.assertEqual(data1["treks"], data2["treks"])

        # Admin trek listing also tests HIT/MISS
        admin_res1 = self.client.get("/api/admin/treks", headers=self._auth_header(self.admin_token))
        self.assertEqual(admin_res1.status_code, 200)
        self.assertEqual(admin_res1.headers.get("X-Cache"), "MISS")

        admin_res2 = self.client.get("/api/admin/treks", headers=self._auth_header(self.admin_token))
        self.assertEqual(admin_res2.status_code, 200)
        self.assertEqual(admin_res2.headers.get("X-Cache"), "HIT")

    # =========================================================================
    # Test 3: Different search filters produce different cache keys
    # =========================================================================
    def test_03_different_search_filters_produce_different_cache_keys(self):
        """Verify different filter parameters (search, difficulty, location) generate independent cache entries."""
        # Query 1: Hard treks
        res_hard = self.client.get("/api/trekker/treks?difficulty=Hard", headers=self._auth_header(self.trekker1_token))
        self.assertEqual(res_hard.status_code, 200)
        self.assertEqual(res_hard.headers.get("X-Cache"), "MISS")
        data_hard = res_hard.get_json()["data"]["treks"]
        self.assertEqual(len(data_hard), 1)
        self.assertEqual(data_hard[0]["trek_name"], "Roopkund Mystery Lake")

        # Query 2: Moderate treks (must be a MISS and return different data)
        res_mod = self.client.get("/api/trekker/treks?difficulty=Moderate", headers=self._auth_header(self.trekker1_token))
        self.assertEqual(res_mod.status_code, 200)
        self.assertEqual(res_mod.headers.get("X-Cache"), "MISS")
        data_mod = res_mod.get_json()["data"]["treks"]
        self.assertEqual(len(data_mod), 1)
        self.assertEqual(data_mod[0]["trek_name"], "Hampta Pass Crossing")

        # Second request for Hard treks must now be a HIT and still return Roopkund
        res_hard_hit = self.client.get("/api/trekker/treks?difficulty=Hard", headers=self._auth_header(self.trekker1_token))
        self.assertEqual(res_hard_hit.status_code, 200)
        self.assertEqual(res_hard_hit.headers.get("X-Cache"), "HIT")
        self.assertEqual(res_hard_hit.get_json()["data"]["treks"][0]["trek_name"], "Roopkund Mystery Lake")

    # =========================================================================
    # Test 4: Different pagination values produce different cache keys
    # =========================================================================
    def test_04_different_pagination_values_produce_different_cache_keys(self):
        """Verify requests with different page or per_page values do not collide in cache."""
        res_p1 = self.client.get("/api/trekker/treks?page=1&per_page=1", headers=self._auth_header(self.trekker1_token))
        self.assertEqual(res_p1.status_code, 200)
        self.assertEqual(res_p1.headers.get("X-Cache"), "MISS")
        p1_treks = res_p1.get_json()["data"]["treks"]
        self.assertEqual(len(p1_treks), 1)

        res_p2 = self.client.get("/api/trekker/treks?page=2&per_page=1", headers=self._auth_header(self.trekker1_token))
        self.assertEqual(res_p2.status_code, 200)
        self.assertEqual(res_p2.headers.get("X-Cache"), "MISS")
        p2_treks = res_p2.get_json()["data"]["treks"]
        self.assertEqual(len(p2_treks), 1)
        self.assertNotEqual(p1_treks[0]["id"], p2_treks[0]["id"])

        # Page 1 must hit cache
        res_p1_hit = self.client.get("/api/trekker/treks?page=1&per_page=1", headers=self._auth_header(self.trekker1_token))
        self.assertEqual(res_p1_hit.headers.get("X-Cache"), "HIT")

    # =========================================================================
    # Test 5: Cache entries expire after their TTL
    # =========================================================================
    def test_05_cache_entries_expire_after_ttl(self):
        """Verify cache entries expire and produce a cache MISS after TTL duration."""
        key = cache_service.build_key("test", "expiring_item")
        # Store with very short TTL of 1 second
        cache_service.set(key, {"message": "temporary"}, timeout=1)

        # Immediate read -> HIT
        self.assertEqual(cache_service.get(key), {"message": "temporary"})

        # Wait for TTL expiration
        time.sleep(1.2)

        # After TTL -> MISS (None)
        self.assertIsNone(cache_service.get(key))

    # =========================================================================
    # Test 6: Creating a trek invalidates the listing cache
    # =========================================================================
    def test_06_creating_trek_invalidates_listing_cache(self):
        """Verify creating a trek via admin API invalidates both trekker and admin listing caches."""
        # Populate cache
        res_initial = self.client.get("/api/trekker/treks", headers=self._auth_header(self.trekker1_token))
        self.assertEqual(res_initial.headers.get("X-Cache"), "MISS")
        self.assertEqual(len(res_initial.get_json()["data"]["treks"]), 2)

        # Verify it is cached
        res_cached = self.client.get("/api/trekker/treks", headers=self._auth_header(self.trekker1_token))
        self.assertEqual(res_cached.headers.get("X-Cache"), "HIT")

        # Admin creates a new trek
        payload = {
            "name": "Kashmir Great Lakes",
            "location": "Sonamarg, J&K",
            "difficulty": "Moderate",
            "duration_days": 7,
            "available_slots": 18,
            "status": "Open",
            "start_date": "2027-08-01",
            "end_date": "2027-08-07"
        }
        res_create = self.client.post("/api/admin/treks", json=payload, headers=self._auth_header(self.admin_token))
        self.assertEqual(res_create.status_code, 201)

        # Listing cache must now be invalidated -> Next request is a MISS and contains 3 treks
        res_after = self.client.get("/api/trekker/treks", headers=self._auth_header(self.trekker1_token))
        self.assertEqual(res_after.headers.get("X-Cache"), "MISS")
        treks = res_after.get_json()["data"]["treks"]
        self.assertEqual(len(treks), 3)
        trek_names = [t["trek_name"] for t in treks]
        self.assertIn("Kashmir Great Lakes", trek_names)

    # =========================================================================
    # Test 7: Updating a trek invalidates relevant listing and detail caches
    # =========================================================================
    def test_07_updating_trek_invalidates_listing_and_detail_caches(self):
        """Verify updating a trek invalidates its detail cache and catalog listings."""
        # Prime detail cache
        res_det1 = self.client.get(f"/api/trekker/treks/{self.trek1.id}", headers=self._auth_header(self.trekker1_token))
        self.assertEqual(res_det1.headers.get("X-Cache"), "MISS")

        res_det2 = self.client.get(f"/api/trekker/treks/{self.trek1.id}", headers=self._auth_header(self.trekker1_token))
        self.assertEqual(res_det2.headers.get("X-Cache"), "HIT")
        self.assertEqual(res_det2.get_json()["data"]["trek_name"], "Roopkund Mystery Lake")

        # Admin updates trek name
        res_update = self.client.put(
            f"/api/admin/treks/{self.trek1.id}",
            json={"name": "Roopkund Skeleton Lake Expedition"},
            headers=self._auth_header(self.admin_token)
        )
        self.assertEqual(res_update.status_code, 200)

        # Detail cache must be a MISS and reflect updated name
        res_det_after = self.client.get(f"/api/trekker/treks/{self.trek1.id}", headers=self._auth_header(self.trekker1_token))
        self.assertEqual(res_det_after.headers.get("X-Cache"), "MISS")
        self.assertEqual(res_det_after.get_json()["data"]["trek_name"], "Roopkund Skeleton Lake Expedition")

    # =========================================================================
    # Test 8: Deleting a trek invalidates relevant caches
    # =========================================================================
    def test_08_deleting_trek_invalidates_relevant_caches(self):
        """Verify deleting a trek invalidates its cached listing and details."""
        # Create a deletable trek with no bookings
        t = Trek(
            trek_name="Temporary Short Hike",
            location="Shimla",
            difficulty="Easy",
            duration_days=1,
            available_slots=10,
            status="Open",
            start_date=date(2027, 9, 1),
            end_date=date(2027, 9, 1)
        )
        db.session.add(t)
        db.session.commit()

        # Prime listing and detail cache
        self.client.get("/api/trekker/treks", headers=self._auth_header(self.trekker1_token))
        self.client.get(f"/api/trekker/treks/{t.id}", headers=self._auth_header(self.trekker1_token))

        # Delete trek via admin
        res_del = self.client.delete(f"/api/admin/treks/{t.id}", headers=self._auth_header(self.admin_token))
        self.assertEqual(res_del.status_code, 200)

        # Next listing query must be a MISS and omit deleted trek
        res_list = self.client.get("/api/trekker/treks", headers=self._auth_header(self.trekker1_token))
        self.assertEqual(res_list.headers.get("X-Cache"), "MISS")
        self.assertNotIn(t.id, [x["id"] for x in res_list.get_json()["data"]["treks"]])

        # Detail query must return 404
        res_get = self.client.get(f"/api/trekker/treks/{t.id}", headers=self._auth_header(self.trekker1_token))
        self.assertEqual(res_get.status_code, 404)

    # =========================================================================
    # Test 9: Changing trek status invalidates relevant caches
    # =========================================================================
    def test_09_changing_trek_status_invalidates_caches(self):
        """Verify staff or admin changing status to Closed removes trek from trekker open catalog cache."""
        # Prime listing
        res_initial = self.client.get("/api/trekker/treks", headers=self._auth_header(self.trekker1_token))
        self.assertEqual(res_initial.headers.get("X-Cache"), "MISS")
        self.assertEqual(len(res_initial.get_json()["data"]["treks"]), 2)

        # Staff closes trek1
        res_close = self.client.patch(
            f"/api/staff/treks/{self.trek1.id}/status",
            json={"status": "Closed"},
            headers=self._auth_header(self.staff_token)
        )
        self.assertEqual(res_close.status_code, 200)

        # Listing cache must be invalidated and trek1 must not appear in open catalog
        res_after = self.client.get("/api/trekker/treks", headers=self._auth_header(self.trekker1_token))
        self.assertEqual(res_after.headers.get("X-Cache"), "MISS")
        active_ids = [x["id"] for x in res_after.get_json()["data"]["treks"]]
        self.assertNotIn(self.trek1.id, active_ids)

    # =========================================================================
    # Test 10: Updating available slots & booking invalidates relevant cached responses
    # =========================================================================
    def test_10_updating_slots_and_booking_invalidates_caches(self):
        """Verify slot update by staff or slot consumption by booking invalidates capacity caches."""
        # Prime trek detail cache
        res_before = self.client.get(f"/api/trekker/treks/{self.trek2.id}", headers=self._auth_header(self.trekker1_token))
        self.assertEqual(res_before.get_json()["data"]["remaining_slots"], 20)

        # Staff updates available slots to 25
        res_slots = self.client.patch(
            f"/api/staff/treks/{self.trek2.id}/slots",
            json={"available_slots": 25},
            headers=self._auth_header(self.staff_token)
        )
        self.assertEqual(res_slots.status_code, 200)

        # Detail query must be a MISS and reflect new capacity
        res_after_staff = self.client.get(f"/api/trekker/treks/{self.trek2.id}", headers=self._auth_header(self.trekker1_token))
        self.assertEqual(res_after_staff.headers.get("X-Cache"), "MISS")
        self.assertEqual(res_after_staff.get_json()["data"]["remaining_slots"], 25)

        # Trekker 1 books a slot
        res_book = self.client.post(
            "/api/trekker/bookings",
            json={"trek_id": self.trek2.id},
            headers=self._auth_header(self.trekker1_token)
        )
        self.assertEqual(res_book.status_code, 201)

        # Detail query must reflect remaining_slots decremented to 24
        res_after_book = self.client.get(f"/api/trekker/treks/{self.trek2.id}", headers=self._auth_header(self.trekker1_token))
        self.assertEqual(res_after_book.headers.get("X-Cache"), "MISS")
        self.assertEqual(res_after_book.get_json()["data"]["remaining_slots"], 24)
        self.assertTrue(res_after_book.get_json()["data"]["has_active_booking"])

        # Trekker 2 views same trek: sees 24 remaining slots but has_active_booking == False (NO DATA LEAKAGE)
        res_trekker2 = self.client.get(f"/api/trekker/treks/{self.trek2.id}", headers=self._auth_header(self.trekker2_token))
        self.assertEqual(res_trekker2.headers.get("X-Cache"), "HIT")
        self.assertEqual(res_trekker2.get_json()["data"]["remaining_slots"], 24)
        self.assertFalse(res_trekker2.get_json()["data"]["has_active_booking"])
        self.assertTrue(res_trekker2.get_json()["data"]["can_book"])

    # =========================================================================
    # Test 11: Redis unavailable - API still returns correct response using DB
    # =========================================================================
    def test_11_redis_unavailable_graceful_fallback(self):
        """Verify API continues functioning without crashing when Redis raises connection errors."""
        # Test when underlying Redis client raises ConnectionError
        client = cache_service.client
        if client is not None:
            with patch.object(client, "get", side_effect=redis.ConnectionError("Redis connection refused")):
                with patch.object(client, "set", side_effect=redis.ConnectionError("Redis connection refused")):
                    # Should not crash; must query DB and return HTTP 200
                    res = self.client.get("/api/trekker/treks", headers=self._auth_header(self.trekker1_token))
                    self.assertEqual(res.status_code, 200)
                    data = res.get_json()["data"]
                    self.assertIn("treks", data)
                    self.assertEqual(len(data["treks"]), 2)

                    # Detail endpoint also succeeds gracefully
                    res_det = self.client.get(f"/api/trekker/treks/{self.trek1.id}", headers=self._auth_header(self.trekker1_token))
                    self.assertEqual(res_det.status_code, 200)
                    self.assertEqual(res_det.get_json()["data"]["trek_name"], "Roopkund Mystery Lake")

        # Test when Redis client property is None (offline / uninitialized)
        with patch.object(type(cache_service), "client", new_callable=unittest.mock.PropertyMock) as mock_client:
            mock_client.return_value = None
            res_offline = self.client.get("/api/trekker/treks", headers=self._auth_header(self.trekker1_token))
            self.assertEqual(res_offline.status_code, 200)
            self.assertEqual(len(res_offline.get_json()["data"]["treks"]), 2)

    # =========================================================================
    # Test 12: Existing authentication and role-based access remain unaffected
    # =========================================================================
    def test_12_authentication_and_rbac_unaffected(self):
        """Verify unauthenticated requests return 401 and role mismatches return 403."""
        # Unauthenticated trekker treks
        res_no_auth = self.client.get("/api/trekker/treks")
        self.assertEqual(res_no_auth.status_code, 401)

        # Trek Staff cannot access admin treks
        res_staff_forbidden = self.client.get("/api/admin/treks", headers=self._auth_header(self.staff_token))
        self.assertEqual(res_staff_forbidden.status_code, 403)

        # Trekker cannot access admin treks
        res_trekker_forbidden = self.client.get("/api/admin/treks", headers=self._auth_header(self.trekker1_token))
        self.assertEqual(res_trekker_forbidden.status_code, 403)

    # =========================================================================
    # Test 13: Existing booking and overbooking behavior remains unaffected
    # =========================================================================
    def test_13_booking_and_overbooking_behavior_unaffected(self):
        """Verify duplicate active reservation rejection and capacity enforcement remain strictly intact."""
        # Trekker 1 books trek 1
        res1 = self.client.post(
            "/api/trekker/bookings",
            json={"trek_id": self.trek1.id},
            headers=self._auth_header(self.trekker1_token)
        )
        self.assertEqual(res1.status_code, 201)

        # Duplicate active reservation rejected with 409
        res_dup = self.client.post(
            "/api/trekker/bookings",
            json={"trek_id": self.trek1.id},
            headers=self._auth_header(self.trekker1_token)
        )
        self.assertEqual(res_dup.status_code, 409)


if __name__ == "__main__":
    unittest.main()

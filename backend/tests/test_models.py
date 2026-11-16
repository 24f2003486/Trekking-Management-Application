"""Automated unit tests for database models, constraints, and relationships."""
import os
import unittest
from datetime import date, datetime
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError
from backend.app import create_app
from backend.app.extensions import db
from backend.app.models import User, Trek, Booking, StaffProfile
from backend.scripts.create_admin import create_admin


class DatabaseModelTestCase(unittest.TestCase):
    """Test suite verifying database schema, models, constraints, and relationships."""

    def setUp(self):
        """Set up an isolated in-memory database before each test."""
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        """Clean up the database session and drop all tables after each test."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # 1. Database Initialization & Table Verification
    def test_database_initialization(self):
        """Verify that all four required tables are created successfully."""
        inspector = inspect(db.engine)
        tables = set(inspector.get_table_names())
        required_tables = {"users", "treks", "bookings", "staff_profiles"}
        self.assertTrue(
            required_tables.issubset(tables),
            f"Missing tables: {required_tables - tables}"
        )

    # 2. User Creation & Password Hashing
    def test_user_creation_and_password_hashing(self):
        """Verify password hashing, verification, and role checks."""
        user = User(
            full_name="John Doe",
            email="john@example.com",
            role="Trekker",
            status="Active",
            contact_number="+91-9876543210"
        )
        user.set_password("SecretPassword123!")
        db.session.add(user)
        db.session.commit()

        self.assertIsNotNone(user.id)
        self.assertNotEqual(user.password_hash, "SecretPassword123!")
        self.assertTrue(user.check_password("SecretPassword123!"))
        self.assertFalse(user.check_password("WrongPassword"))
        self.assertTrue(user.is_trekker)
        self.assertFalse(user.is_admin)

    # 3. User Email Uniqueness
    def test_user_email_uniqueness(self):
        """Verify that duplicate emails violate the unique constraint."""
        user1 = User(
            full_name="User One",
            email="duplicate@example.com",
            role="Trekker",
            status="Active"
        )
        user1.set_password("Pass123!")
        db.session.add(user1)
        db.session.commit()

        user2 = User(
            full_name="User Two",
            email="duplicate@example.com",
            role="Trekker",
            status="Active"
        )
        user2.set_password("Pass456!")
        db.session.add(user2)
        with self.assertRaises(IntegrityError):
            db.session.commit()
        db.session.rollback()

    # 4. User Role Validation
    def test_invalid_user_role_rejected(self):
        """Verify that invalid roles are rejected."""
        with self.assertRaises(ValueError):
            User(
                full_name="Bad Role",
                email="badrole@example.com",
                role="SuperAdmin",  # Not in allowed roles
                status="Active"
            )

    # 5. User Status Validation
    def test_invalid_user_status_rejected(self):
        """Verify that invalid account statuses are rejected."""
        with self.assertRaises(ValueError):
            User(
                full_name="Bad Status",
                email="badstatus@example.com",
                role="Trekker",
                status="Archived"  # Not in allowed statuses
            )

    # 6. Trek Creation & Validations
    def test_trek_creation_and_difficulty_validation(self):
        """Verify valid trek creation and invalid difficulty rejection."""
        trek = Trek(
            trek_name="Himalayan Pass",
            location="Himachal Pradesh",
            description="Scenic high-altitude trek.",
            difficulty="Moderate",
            duration_days=5,
            available_slots=20,
            status="Open",
            start_date=date(2027, 5, 1),
            end_date=date(2027, 5, 6)
        )
        db.session.add(trek)
        db.session.commit()
        self.assertIsNotNone(trek.id)

        # Invalid difficulty
        with self.assertRaises(ValueError):
            Trek(
                trek_name="Extreme Trek",
                location="Kashmir",
                difficulty="Extreme",  # Invalid
                duration_days=4,
                available_slots=10,
                status="Open",
                start_date=date(2027, 6, 1),
                end_date=date(2027, 6, 5)
            )

    def test_negative_duration_rejected(self):
        """Verify that trek duration must be strictly positive."""
        with self.assertRaises(ValueError):
            Trek(
                trek_name="Zero Day Trek",
                location="Uttarakhand",
                difficulty="Easy",
                duration_days=0,  # Invalid
                available_slots=10,
                status="Pending",
                start_date=date(2027, 4, 1),
                end_date=date(2027, 4, 1)
            )

    def test_negative_available_slots_rejected(self):
        """Verify that available slots cannot be negative."""
        with self.assertRaises(ValueError):
            Trek(
                trek_name="Negative Slots Trek",
                location="Uttarakhand",
                difficulty="Easy",
                duration_days=3,
                available_slots=-5,  # Invalid
                status="Pending",
                start_date=date(2027, 4, 1),
                end_date=date(2027, 4, 4)
            )

    def test_trek_end_date_before_start_date_rejected(self):
        """Verify that end date preceding start date is rejected on creation."""
        with self.assertRaises(ValueError):
            trek = Trek(
                trek_name="Backwards Trek",
                location="Uttarakhand",
                difficulty="Easy",
                duration_days=3,
                available_slots=15,
                status="Pending",
                start_date=date(2027, 7, 10),
                end_date=date(2027, 7, 5)  # Invalid: end precedes start
            )
            db.session.add(trek)
            db.session.commit()
        db.session.rollback()

    def test_trek_date_validation_on_update(self):
        """Verify date validation when updating an existing trek."""
        trek = Trek(
            trek_name="Date Update Trek",
            location="Sikkim",
            difficulty="Moderate",
            duration_days=6,
            available_slots=12,
            status="Open",
            start_date=date(2027, 6, 1),
            end_date=date(2027, 6, 6)
        )
        db.session.add(trek)
        db.session.commit()

        # Update end_date before start_date should fail on commit
        trek.end_date = date(2027, 5, 25)
        with self.assertRaises(ValueError):
            db.session.commit()
        db.session.rollback()

        # Shifting the entire window via set_dates should succeed
        trek = db.session.get(Trek, trek.id)
        trek.set_dates(date(2027, 6, 10), date(2027, 6, 16))
        db.session.commit()
        self.assertEqual(trek.start_date, date(2027, 6, 10))
        self.assertEqual(trek.end_date, date(2027, 6, 16))

    # 7. Staff Profile & User One-to-One Relationship
    def test_staff_profile_relationship_and_experience_validation(self):
        """Verify staff profile one-to-one relationship and non-negative experience."""
        staff_user = User(
            full_name="Jane Guide",
            email="jane@example.com",
            role="Trek Staff",
            status="Active"
        )
        staff_user.set_password("GuidePass123!")
        db.session.add(staff_user)
        db.session.commit()

        profile = StaffProfile(
            user_id=staff_user.id,
            specialization="High-Altitude Mountaineering",
            experience_years=7,
            emergency_contact="+91-9876543211"
        )
        db.session.add(profile)
        db.session.commit()

        self.assertIsNotNone(profile.id)
        self.assertEqual(staff_user.staff_profile.specialization, "High-Altitude Mountaineering")
        self.assertEqual(profile.user.email, "jane@example.com")

        # Negative experience rejected
        with self.assertRaises(ValueError):
            StaffProfile(
                user_id=staff_user.id,
                specialization="Wilderness Survival",
                experience_years=-2  # Invalid
            )

    def test_staff_profile_requires_trek_staff_role(self):
        """Verify that assigning a staff profile to a non-staff user is rejected via both user and user_id."""
        trekker = User(
            full_name="Normal Trekker",
            email="trekker@example.com",
            role="Trekker",
            status="Active"
        )
        trekker.set_password("Trekker123!")
        db.session.add(trekker)
        db.session.commit()

        # 1. Assignment via user relationship attribute
        with self.assertRaises(ValueError):
            StaffProfile(
                user=trekker,
                specialization="Climbing",
                experience_years=2
            )

        # 2. Assignment via user_id foreign key attribute
        profile = StaffProfile(
            user_id=trekker.id,
            specialization="Climbing",
            experience_years=2
        )
        db.session.add(profile)
        with self.assertRaises(ValueError):
            db.session.commit()
        db.session.rollback()

    # 8. Trek Staff to Trek Relationship & Assignment Validation
    def test_trek_assigned_staff_relationship(self):
        """Verify assigning a staff member to multiple treks."""
        staff = User(
            full_name="Alex Guide",
            email="alex@example.com",
            role="Trek Staff",
            status="Active"
        )
        staff.set_password("StaffPass123!")
        db.session.add(staff)
        db.session.commit()

        trek1 = Trek(
            trek_name="Roopkund Expedition",
            location="Uttarakhand",
            difficulty="Hard",
            duration_days=8,
            available_slots=15,
            status="Open",
            start_date=date(2027, 9, 1),
            end_date=date(2027, 9, 8),
            assigned_staff_id=staff.id
        )
        trek2 = Trek(
            trek_name="Kedarkantha Winter Trek",
            location="Uttarakhand",
            difficulty="Easy",
            duration_days=4,
            available_slots=25,
            status="Open",
            start_date=date(2027, 12, 10),
            end_date=date(2027, 12, 14),
            assigned_staff_id=staff.id
        )
        db.session.add_all([trek1, trek2])
        db.session.commit()

        self.assertEqual(staff.assigned_treks.count(), 2)
        self.assertEqual(trek1.assigned_staff.full_name, "Alex Guide")

    def test_trek_assignment_requires_trek_staff_role(self):
        """Verify that assigning a non-staff user to a trek is rejected via both staff object and staff_id."""
        trekker = User(
            full_name="Non Staff Trekker",
            email="nonstaff@example.com",
            role="Trekker",
            status="Active"
        )
        trekker.set_password("Pass123!")
        db.session.add(trekker)
        db.session.commit()

        # 1. Assignment via assigned_staff attribute
        with self.assertRaises(ValueError):
            Trek(
                trek_name="Invalid Staff Trek 1",
                location="Himachal",
                difficulty="Easy",
                duration_days=3,
                available_slots=10,
                status="Pending",
                start_date=date(2027, 8, 1),
                end_date=date(2027, 8, 3),
                assigned_staff=trekker
            )

        # 2. Assignment via assigned_staff_id FK
        invalid_trek = Trek(
            trek_name="Invalid Staff Trek 2",
            location="Himachal",
            difficulty="Easy",
            duration_days=3,
            available_slots=10,
            status="Pending",
            start_date=date(2027, 8, 1),
            end_date=date(2027, 8, 3),
            assigned_staff_id=trekker.id
        )
        db.session.add(invalid_trek)
        with self.assertRaises(ValueError):
            db.session.commit()
        db.session.rollback()

    # 9. Trek Staff Role Modification Safety
    def test_changing_trek_staff_role_with_profile_or_treks_rejected(self):
        """Verify that changing a Trek Staff role is blocked when they hold a profile or assigned treks."""
        staff = User(
            full_name="Safe Staff",
            email="safestaff@example.com",
            role="Trek Staff",
            status="Active"
        )
        staff.set_password("Staff123!")
        db.session.add(staff)
        db.session.commit()

        profile = StaffProfile(user=staff, specialization="Search & Rescue", experience_years=5)
        db.session.add(profile)
        db.session.commit()

        # Attempt to change role to Trekker while profile exists
        staff.role = "Trekker"
        with self.assertRaises(ValueError):
            db.session.commit()
        db.session.rollback()

        # Delete profile, then assign a trek
        staff = db.session.get(User, staff.id)
        db.session.delete(staff.staff_profile)
        db.session.commit()

        trek = Trek(
            trek_name="Staff Test Trek",
            location="Uttarakhand",
            difficulty="Moderate",
            duration_days=4,
            available_slots=15,
            status="Open",
            start_date=date(2027, 10, 1),
            end_date=date(2027, 10, 4),
            assigned_staff=staff
        )
        db.session.add(trek)
        db.session.commit()

        # Attempt to change role to Trekker while assigned to trek
        staff.role = "Trekker"
        with self.assertRaises(ValueError):
            db.session.commit()
        db.session.rollback()

        # Unassign trek, now role change should succeed cleanly
        staff = db.session.get(User, staff.id)
        trek = db.session.get(Trek, trek.id)
        trek.assigned_staff_id = None
        db.session.commit()

        staff.role = "Trekker"
        db.session.commit()
        self.assertEqual(staff.role, "Trekker")

    # 10. User and Trek Booking Relationships
    def test_booking_relationships(self):
        """Verify User <-> Booking and Trek <-> Booking relationships."""
        trekker = User(
            full_name="Alice Smith",
            email="alice@example.com",
            role="Trekker",
            status="Active"
        )
        trekker.set_password("AlicePass123!")

        trek = Trek(
            trek_name="Valley of Flowers",
            location="Uttarakhand",
            difficulty="Easy",
            duration_days=6,
            available_slots=30,
            status="Open",
            start_date=date(2027, 8, 1),
            end_date=date(2027, 8, 6)
        )
        db.session.add_all([trekker, trek])
        db.session.commit()

        booking = Booking(
            user=trekker,
            trek=trek,
            booking_status="Booked",
            payment_status="Paid"
        )
        db.session.add(booking)
        db.session.commit()

        self.assertIsNotNone(booking.id)
        self.assertEqual(trekker.bookings.count(), 1)
        self.assertEqual(trek.bookings.count(), 1)
        self.assertEqual(booking.user.full_name, "Alice Smith")
        self.assertEqual(booking.trek.trek_name, "Valley of Flowers")

    # 11. Partial Unique Index: Duplicate Active Bookings vs History
    def test_duplicate_active_booking_prevented_and_history_preserved(self):
        """Verify partial unique index: duplicate Booked fails, Cancelled/Completed allow new bookings."""
        trekker = User(
            full_name="Bob Brown",
            email="bob@example.com",
            role="Trekker",
            status="Active"
        )
        trekker.set_password("BobPass123!")

        trek = Trek(
            trek_name="Hampta Pass",
            location="Himachal Pradesh",
            difficulty="Moderate",
            duration_days=5,
            available_slots=20,
            status="Open",
            start_date=date(2027, 7, 1),
            end_date=date(2027, 7, 5)
        )
        db.session.add_all([trekker, trek])
        db.session.commit()

        # Step 1: First active booking succeeds
        booking1 = Booking(
            user_id=trekker.id,
            trek_id=trek.id,
            booking_status="Booked",
            payment_status="Paid"
        )
        db.session.add(booking1)
        db.session.commit()

        # Step 2: Second duplicate active booking fails with IntegrityError
        booking2 = Booking(
            user_id=trekker.id,
            trek_id=trek.id,
            booking_status="Booked",
            payment_status="Paid"
        )
        db.session.add(booking2)
        with self.assertRaises(IntegrityError):
            db.session.commit()
        db.session.rollback()

        # Step 3: Cancel booking1; subsequent new booking should succeed
        booking1 = db.session.get(Booking, booking1.id)
        booking1.booking_status = "Cancelled"
        db.session.commit()

        booking3 = Booking(
            user_id=trekker.id,
            trek_id=trek.id,
            booking_status="Booked",
            payment_status="Pending"
        )
        db.session.add(booking3)
        db.session.commit()
        self.assertIsNotNone(booking3.id)

        # Step 4: Complete booking3; another new booking should succeed
        booking3.booking_status = "Completed"
        db.session.commit()

        booking4 = Booking(
            user_id=trekker.id,
            trek_id=trek.id,
            booking_status="Booked",
            payment_status="Paid"
        )
        db.session.add(booking4)
        db.session.commit()
        self.assertIsNotNone(booking4.id)

        # Step 5: Duplicate active booking again must fail
        booking5 = Booking(
            user_id=trekker.id,
            trek_id=trek.id,
            booking_status="Booked",
            payment_status="Paid"
        )
        db.session.add(booking5)
        with self.assertRaises(IntegrityError):
            db.session.commit()
        db.session.rollback()

        # Step 6: Verify all historical records (Cancelled, Completed, Booked) remain intact
        user_bookings = Booking.query.filter_by(user_id=trekker.id, trek_id=trek.id).all()
        statuses = [b.booking_status for b in user_bookings]
        self.assertEqual(len(user_bookings), 3)
        self.assertEqual(statuses.count("Cancelled"), 1)
        self.assertEqual(statuses.count("Completed"), 1)
        self.assertEqual(statuses.count("Booked"), 1)

    # 12. SQLite Foreign Key Enforcement
    def test_sqlite_foreign_key_constraints(self):
        """Verify that SQLite foreign key constraints prevent orphan records."""
        # Inserting booking with non-existent user_id
        invalid_booking = Booking(
            user_id=9999,  # Does not exist
            trek_id=9999,  # Does not exist
            booking_status="Booked"
        )
        db.session.add(invalid_booking)
        with self.assertRaises(IntegrityError):
            db.session.commit()
        db.session.rollback()

        # Inserting staff profile with non-existent user_id
        invalid_profile = StaffProfile(
            user_id=8888,  # Does not exist
            specialization="First Aid",
            experience_years=3
        )
        db.session.add(invalid_profile)
        with self.assertRaises(IntegrityError):
            db.session.commit()
        db.session.rollback()

    # 13. Admin Creation & Duplicate Prevention
    def test_admin_creation_and_duplicate_prevention(self):
        """Verify programmatic admin creation and duplicate check."""
        admin = User(
            full_name="System Administrator",
            email="admin@trekkingapp.local",
            role="Admin",
            status="Active"
        )
        admin.set_password("AdminSecureKey2026!")
        db.session.add(admin)
        db.session.commit()

        self.assertTrue(admin.is_admin)

        # Check existing admin check logic
        existing_admin = User.query.filter_by(role="Admin").first()
        self.assertIsNotNone(existing_admin)
        self.assertEqual(existing_admin.email, "admin@trekkingapp.local")

    # 14. Admin Provisioning Email Conflict Handling
    def test_admin_provisioning_email_conflict_with_trekker(self):
        """Verify that an existing Trekker with admin email triggers conflict error instead of false Admin detected."""
        trekker = User(
            full_name="Intruder Trekker",
            email="admin@trekkingapp.local",
            role="Trekker",
            status="Active"
        )
        trekker.set_password("Pass123!")
        db.session.add(trekker)
        db.session.commit()

        # Running create_admin with this conflicting email should exit with code 1
        os.environ["ADMIN_INITIAL_PASSWORD"] = "TestAdminPass2026!"
        with self.assertRaises(SystemExit) as cm:
            create_admin(app=self.app)
        self.assertEqual(cm.exception.code, 1)


if __name__ == "__main__":
    unittest.main()

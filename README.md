# Trekking Management Application V2 (TMA)

**Course:** Modern Application Development II (MAD-II)  
**Institution:** Indian Institute of Technology Madras (IIT Madras)  
**Project Status:** Milestone 1 Completed (Database Models & Schema Setup)

---

## 1. Project Description

The **Trekking Management Application V2 (TMA)** is a multi-user, web-based platform designed to coordinate and streamline trekking expedition logistics, bookings, and operations. The platform facilitates collaboration and communication among three primary user roles: **Administrators**, **Trek Staff**, and **Trekkers (Users)**.

By integrating a responsive frontend with a scalable RESTful backend, TMA aims to provide end-to-end expedition scheduling, participant management, and real-time activity tracking.

> **Project Status Disclaimer:**  
> This repository currently includes the **Milestone 0 repository setup** and **Milestone 1 database models and schema**. REST API endpoints, user authentication (JWT/session), Vue.js frontend dashboards, Redis caching, and Celery background jobs are scheduled for subsequent milestones and are **not yet implemented**.

---

## 2. Problem Statement

Organizing outdoor trekking expeditions involves complex logistical coordination:
- Trek organizations often manage multiple concurrent trekking routes across diverse geographies with strict participant capacity limits and safety constraints.
- Managing staff assignments (guides, trek leaders, support crew) and tracking participant readiness across different stages is error-prone when conducted via disparate spreadsheets or manual communication channels.
- Trekkers frequently lack real-time visibility into itinerary details, seat availability, booking statuses, and automated trip reminders.
- Administrative teams spend significant manual effort generating monthly operational reports, tracking cancellations, and handling communication broadcasts.

Without a centralized, automated web management system, trekking organizations encounter operational bottlenecks, data inconsistencies, overbooking risks, and delayed notifications.

---

## 3. Main Objectives

The primary objectives of the Trekking Management Application V2 are:
1. **Centralized Expedition Management:** Provide an administrative portal to manage trek itineraries, batches, capacities, pricing, and assigned field staff.
2. **Role-Based Access Control (RBAC):** Deliver tailored interfaces and access privileges for Administrators, Trek Staff, and Trekkers.
3. **Streamlined Trek Booking Flow:** Allow trekkers to search, filter, and reserve trek slots with real-time seat availability verification.
4. **Staff & Participant Field Coordination:** Enable trek leaders and field staff to monitor participant lists, verify attendance, and update batch statuses across checkpoints.
5. **Asynchronous Background Processing & Caching:** Leverage Redis caching for responsive data retrieval and Celery workers for automated notifications, reminder emails, and monthly report generation.
6. **Modern, Responsive User Experience:** Deliver an intuitive Single Page Application (SPA) interface using Vue.js and Bootstrap.

---

## 4. User Roles & Responsibilities

The system is architected around three distinct user roles:

| Role | Responsibilities & Planned Capabilities |
| :--- | :--- |
| **Admin** | <ul><li>Create, update, and manage trekking routes, schedules, and pricing</li><li>Manage user accounts (Trekkers and Staff) and role assignments</li><li>Allocate Trek Staff to specific trek batches</li><li>Monitor overall bookings, system logs, and view aggregate analytics</li><li>Trigger and review monthly performance and activity reports</li></ul> |
| **Trek Staff** | <ul><li>View assigned upcoming and active treks</li><li>Access participant rosters and emergency contact information</li><li>Update checkpoint progress, weather alerts, and trek completion status</li><li>Record participant attendance and field notes</li></ul> |
| **Trekker (User)** | <ul><li>Browse and search the trek catalog by difficulty, duration, elevation, and price</li><li>View comprehensive trek details, itinerary, and packing checklists</li><li>Book available slots and manage personal booking history</li><li>Receive automated booking confirmations, preparation alerts, and status updates</li></ul> |

---

## 5. Planned Technology Stack

In strict compliance with the **MAD-II** project guidelines, the application utilizes the following stack:

- **Backend:** Python [Flask](https://flask.palletsprojects.com/) (RESTful API architecture)
- **Frontend:** [Vue.js](https://vuejs.org/) (Single Page Application architecture)
- **UI Styling:** [Bootstrap](https://getbootstrap.com/) (Responsive, component-driven CSS framework)
- **Database:** [SQLite](https://www.sqlite.org/) (Relational database managed via SQLAlchemy ORM)
- **Caching:** [Redis](https://redis.io/) (In-memory data store for caching high-traffic endpoints)
- **Background Jobs & Scheduling:** [Celery](https://docs.celeryq.dev/) with Redis as the message broker and result backend (handles async email dispatch and recurring batch reports)

---

## 6. Planned Major Functionalities

The planned functionalities for subsequent development stages include:

1. **Authentication & Authorization:** Secure session/token-based login and signup with role-based route protection.
2. **Trek Catalog & Discovery:** Route filtering, keyword search, difficulty rating indicators, and interactive itinerary views.
3. **Booking & Slot Management:** Batch capacity limits, booking confirmations, cancellation workflows, and real-time slot tracking.
4. **Staff Allocation & Field Checkpoints:** Assignment workflow linking trek leaders to specific batches, along with checkpoint status tracking.
5. **Asynchronous Notification System:** Automated booking confirmation emails, trek departure reminders, and alerts triggered by Celery.
6. **Scheduled Reporting (Celery Beat):** Monthly summary reports generated automatically and distributed to administrators.
7. **Performance Caching:** Redis caching applied to static and semi-static trek catalog queries to minimize database load.

---

## 7. Project Status & Development Milestones

Development is organized in incremental milestones:

- [x] **Milestone 0: Project Setup & Repository Initialization**
  - Initialized Git version control on branch `main`
  - Established `.gitignore` rules for Python, Flask, SQLite, Redis, Celery, and Vue/Node environments
  - Prepared repository for GitHub hosting
- [x] **Milestone 1: Database Models & Schema Setup (Completed)**
  - Application factory pattern (`create_app`) with SQLite configuration
  - SQLite foreign key constraint enforcement via connection hooks
  - Database models: `User`, `Trek`, `Booking`, `StaffProfile`
  - Automated database initialization via `flask init-db` CLI
  - Secure programmatic Admin account provisioning script (`backend/scripts/create_admin.py`)
  - Automated unit test suite using isolated in-memory SQLite database (`backend/tests/test_models.py`)
- [ ] **Milestone 2: Authentication & Frontend Foundation**
  - Role-based authentication backend
  - Vue.js project setup with Bootstrap styling and client-side routing
  - Login, registration, and role-based dashboard scaffolding
- [ ] **Milestone 3: Booking Engine & Staff Portal**
  - Trekker booking workflow with capacity enforcement
  - Staff assignment dashboard and participant tracking
- [ ] **Milestone 4: Redis Caching & Celery Background Tasks**
  - Redis integration for catalog caching
  - Celery asynchronous task pipeline (email alerts & monthly reports)
  - Celery Beat scheduled jobs
- [ ] **Milestone 5: Verification, Testing & Final Documentation**
  - End-to-end integration testing and bug fixes
  - API documentation, setup instructions, and deployment readiness

---

## 8. Milestone 1: Database Architecture & Schema Specification

### 8.1 Database Architecture Overview
The database uses **SQLite** through **Flask-SQLAlchemy** (SQLAlchemy ORM). SQLite foreign key enforcement is enabled via an engine connect listener (`PRAGMA foreign_keys=ON;`).

All database schema creation is completely **programmatic**; manual database modifications via external GUI applications are prohibited.

### 8.2 Models & Schema

#### 1. User Model (`users`)
- **`id`** (`Integer`, Primary Key, Autoincrement)
- **`full_name`** (`String(100)`, Required)
- **`email`** (`String(120)`, Required, Unique, Indexed)
- **`password_hash`** (`String(255)`, Required, Werkzeug hashed)
- **`contact_number`** (`String(20)`, Optional)
- **`role`** (`String(20)`, Required): Allowed values: `'Admin'`, `'Trek Staff'`, `'Trekker'`
- **`status`** (`String(20)`, Default `'Active'`): Allowed values: `'Active'`, `'Inactive'`, `'Blacklisted'`
- **`created_at`** (`DateTime`, Default `utcnow`)
- **`updated_at`** (`DateTime`, Default `utcnow`, OnUpdate `utcnow`)
- **Methods:** `set_password(password)`, `check_password(password)`
- **Relationships:**
  - `staff_profile`: One-to-One with `StaffProfile` (`back_populates="user"`, `uselist=False`)
  - `assigned_treks`: One-to-Many with `Trek` as assigned staff
  - `bookings`: One-to-Many with `Booking` (history preserved)

#### 2. Trek Model (`treks`)
- **`id`** (`Integer`, Primary Key, Autoincrement)
- **`trek_name`** (`String(100)`, Required)
- **`location`** (`String(100)`, Required)
- **`description`** (`Text`, Optional)
- **`difficulty`** (`String(20)`, Required): Allowed values: `'Easy'`, `'Moderate'`, `'Hard'`
- **`duration_days`** (`Integer`, Required): Strictly positive (> 0)
- **`available_slots`** (`Integer`, Required): Non-negative (>= 0)
- **`assigned_staff_id`** (`Integer`, Foreign Key `users.id`, Nullable, `ondelete='SET NULL'`)
- **`status`** (`String(20)`, Required, Default `'Pending'`): Allowed values: `'Pending'`, `'Approved'`, `'Open'`, `'Closed'`, `'Completed'`
- **`start_date`** (`Date`, Required)
- **`end_date`** (`Date`, Required): Validated `end_date >= start_date`
- **`created_at`** (`DateTime`, Default `utcnow`)
- **`updated_at`** (`DateTime`, Default `utcnow`, OnUpdate `utcnow`)
- **Relationships:**
  - `assigned_staff`: Relationship to `User` (validated to have role `'Trek Staff'`)
  - `bookings`: One-to-Many with `Booking`

#### 3. Booking Model (`bookings`)
- **`id`** (`Integer`, Primary Key, Autoincrement)
- **`user_id`** (`Integer`, Foreign Key `users.id`, Required, `ondelete='RESTRICT'`)
- **`trek_id`** (`Integer`, Foreign Key `treks.id`, Required, `ondelete='RESTRICT'`)
- **`booking_date`** (`DateTime`, Required, Default `utcnow`)
- **`booking_status`** (`String(20)`, Required, Default `'Booked'`): Allowed values: `'Booked'`, `'Cancelled'`, `'Completed'`
- **`payment_status`** (`String(20)`, Optional, Default `'Pending'`): Allowed values: `'Pending'`, `'Paid'`, `'Failed'`, `'Refunded'`
- **`created_at`** (`DateTime`, Default `utcnow`)
- **`updated_at`** (`DateTime`, Default `utcnow`, OnUpdate `utcnow`)
- **Constraints & Indexes:**
  - Partial unique index `uq_active_user_trek_booking` on `(user_id, trek_id)` where `booking_status = 'Booked'` to prevent duplicate active reservations.
- **Relationships:**
  - `user`: Belongs to `User`
  - `trek`: Belongs to `Trek`

#### 4. Staff Profile Model (`staff_profiles`)
- **`id`** (`Integer`, Primary Key, Autoincrement)
- **`user_id`** (`Integer`, Foreign Key `users.id`, Required, Unique, `ondelete='CASCADE'`)
- **`specialization`** (`String(100)`, Optional)
- **`experience_years`** (`Integer`, Default `0`): Validated non-negative (>= 0)
- **`emergency_contact`** (`String(20)`, Optional)
- **`created_at`** (`DateTime`, Default `utcnow`)
- **`updated_at`** (`DateTime`, Default `utcnow`, OnUpdate `utcnow`)
- **Validation:** Only users with role `'Trek Staff'` can hold a staff profile.
- **Relationships:**
  - `user`: One-to-One with `User`

---

### 8.3 Entity Relationships Summary

| Relationship | Cardinality | Parent Table | Child Table | Foreign Key | Cascade / Delete Rule |
| :--- | :---: | :--- | :--- | :--- | :--- |
| **User ↔ Staff Profile** | 1 : 1 | `users` | `staff_profiles` | `staff_profiles.user_id` | `CASCADE` (profile deleted if staff account deleted) |
| **Trek Staff ↔ Trek** | 1 : N | `users` | `treks` | `treks.assigned_staff_id` | `SET NULL` (trek preserved if staff unassigned) |
| **User ↔ Booking** | 1 : N | `users` | `bookings` | `bookings.user_id` | `RESTRICT` (booking history strictly preserved) |
| **Trek ↔ Booking** | 1 : N | `treks` | `bookings` | `bookings.trek_id` | `RESTRICT` (booking history strictly preserved) |

---

### 8.4 Setup and Verification Instructions (Windows PowerShell)

#### Step 1: Create and Activate Virtual Environment
```powershell
# Navigate to project root
cd "D:\iitm'\26t3 sep\MAD2\Trekking-Management-Application"

# Create virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1
```

#### Step 2: Install Dependencies
```powershell
pip install -r backend/requirements.txt
```

#### Step 3: Initialize Database Schema Programmatically
```powershell
$env:FLASK_APP = "backend/run.py"
flask init-db
```
*Output: `Database initialized successfully. All tables created.`*

#### Step 4: Provision Initial Admin Account
```powershell
# Set initial admin password in environment variable
$env:ADMIN_INITIAL_PASSWORD = "YourSecurePassword123!"

# Execute admin creation script
python backend/scripts/create_admin.py
```
*Output: `Success: Admin account created successfully.`*  
*(Rerunning the command will confirm duplicate prevention: `Notice: Admin account already exists...`)*

#### Step 5: Run Automated Unit Tests
```powershell
python -m unittest discover backend/tests
```
*All 16 test cases run against an isolated in-memory SQLite database.*

#### Step 6: Inspect Created Tables and Admin Record
```powershell
python -c "
import sqlite3
conn = sqlite3.connect('backend/instance/tma.db')
cursor = conn.cursor()
cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\";')
print('Tables:', cursor.fetchall())
cursor.execute('SELECT id, full_name, email, role, status FROM users;')
print('Users:', cursor.fetchall())
conn.close()
"
```

---

## 9. Repository Structure

```text
trekking-management-app/
├── .gitignore
├── README.md
├── .venv/                         # Virtual environment (git-ignored)
└── backend/
    ├── .env.example               # Environment variables template
    ├── requirements.txt           # Minimal backend dependencies
    ├── run.py                     # Application entry point & CLI context
    ├── instance/                  # SQLite DB storage directory (git-ignored)
    │   └── tma.db
    ├── app/
    │   ├── __init__.py            # Flask application factory (create_app)
    │   ├── config.py              # Environment configurations (Base, Dev, Test)
    │   ├── extensions.py          # SQLAlchemy extension instance
    │   └── models/
    │       ├── __init__.py        # Models export
    │       ├── user.py            # User model
    │       ├── trek.py            # Trek model
    │       ├── booking.py         # Booking model
    │       └── staff_profile.py   # StaffProfile model
    ├── scripts/
    │   └── create_admin.py        # Programmatic admin account provisioning
    └── tests/
        ├── __init__.py
        └── test_models.py         # 16 automated tests for schema & constraints
```

---

## 10. License & Academic Integrity

This project is submitted as coursework for the **Modern Application Development II (MAD-II)** course at **IIT Madras**. All work conforms to academic integrity guidelines established by the program.

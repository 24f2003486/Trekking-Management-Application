# Trekking Management Application V2 (TMA)

**Course:** Modern Application Development II (MAD-II)  
**Institution:** Indian Institute of Technology Madras (IIT Madras)  
**Project Status:** Milestone 2 Completed (Authentication & Role-Based Access Control)

---

## 1. Project Description

The **Trekking Management Application V2 (TMA)** is a multi-user, web-based platform designed to coordinate and streamline trekking expedition logistics, bookings, and operations. The platform facilitates collaboration and communication among three primary user roles: **Administrators**, **Trek Staff**, and **Trekkers (Users)**.

By integrating a responsive frontend with a scalable RESTful backend, TMA aims to provide end-to-end expedition scheduling, participant management, and real-time activity tracking.

> **Project Status Disclaimer:**  
> This repository currently includes **Milestone 0 (Project Setup)**, **Milestone 1 (Database Models & Schema)**, and **Milestone 2 (Authentication & Role-Based Access Control)**. Core expedition creation, booking flows, Redis caching, and Celery background workers are scheduled for subsequent milestones and are **not yet implemented**.

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
- **Authentication:** [Flask-JWT-Extended](https://flask-jwt-extended.readthedocs.io/) (JWT tokens with SQLite blocklist revocation)
- **Frontend:** [Vue.js 3](https://vuejs.org/) + [Vite](https://vitejs.dev/) (Single Page Application architecture)
- **UI Styling:** [Bootstrap 5](https://getbootstrap.com/) (Responsive, component-driven CSS framework)
- **Database:** [SQLite](https://www.sqlite.org/) (Relational database managed via SQLAlchemy ORM)
- **Caching:** [Redis](https://redis.io/) (In-memory data store for caching high-traffic endpoints — Planned: Milestone 4)
- **Background Jobs & Scheduling:** [Celery](https://docs.celeryq.dev/) with Redis broker (Planned: Milestone 4)

---

## 6. Planned Major Functionalities

The planned functionalities for subsequent development stages include:

1. **Authentication & Authorization (Completed):** Secure JWT login, Trekker registration, token blocklist logout, and role-based route protection.
2. **Trek Catalog & Discovery (Planned M3):** Route filtering, keyword search, difficulty rating indicators, and interactive itinerary views.
3. **Booking & Slot Management (Planned M3):** Batch capacity limits, booking confirmations, cancellation workflows, and real-time slot tracking.
4. **Staff Allocation & Field Checkpoints (Planned M3):** Assignment workflow linking trek leaders to specific batches, along with checkpoint status tracking.
5. **Asynchronous Notification System (Planned M4):** Automated booking confirmation emails, trek departure reminders, and alerts triggered by Celery.
6. **Scheduled Reporting (Celery Beat) (Planned M4):** Monthly summary reports generated automatically and distributed to administrators.
7. **Performance Caching (Planned M4):** Redis caching applied to static and semi-static trek catalog queries to minimize database load.

---

## 7. Project Status & Development Milestones

Development is organized in incremental milestones:

- [x] **Milestone 0: Project Setup & Repository Initialization**
  - Initialized Git version control on branch `main`
  - Established `.gitignore` rules for Python, Flask, SQLite, Redis, Celery, and Vue/Node environments
  - Prepared repository for GitHub hosting
- [x] **Milestone 1: Database Models & Schema Setup**
  - Application factory pattern (`create_app`) with SQLite configuration
  - SQLite foreign key constraint enforcement via connection hooks
  - Database models: `User`, `Trek`, `Booking`, `StaffProfile`
  - Automated database initialization via `flask init-db` CLI
  - Secure programmatic Admin account provisioning script (`backend/scripts/create_admin.py`)
  - Automated unit test suite using isolated in-memory SQLite database
- [x] **Milestone 2: Authentication & Role-Based Access Control (Completed)**
  - JWT-based authentication using `Flask-JWT-Extended` with configurable expiration
  - Backend RBAC decorators (`@role_required`) enforcing active account status and database role checks
  - Trekker self-registration with role-escalation prevention (`POST /api/auth/register`)
  - Multi-role login endpoint (`POST /api/auth/login`) with sanitized user payloads (no `password_hash` leaks)
  - Profile retrieval (`GET /api/auth/me`) and secure logout with SQLite token blocklist (`TokenBlocklist`)
  - Role-protected dashboard placeholder APIs for Admin, Trek Staff, and Trekker
  - Vue 3 + Vite frontend with Bootstrap 5 styling and Vue Router
  - Client-side navigation guards with automated role-based redirects (`/admin/dashboard`, `/staff/dashboard`, `/trekker/dashboard`)
  - 46 comprehensive automated unit tests covering models, auth, RBAC, and logout
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
- **`created_at`**, **`updated_at`** (`DateTime`)
- **Methods:** `set_password(password)`, `check_password(password)`, `to_dict()`
- **Relationships:**
  - `staff_profile`: One-to-One with `StaffProfile` (`back_populates="user"`, `uselist=False`)
  - `assigned_treks`: One-to-Many with `Trek` as assigned staff
  - `bookings`: One-to-Many with `Booking` (history preserved)

#### 2. Trek Model (`treks`)
- **`id`** (`Integer`, Primary Key, Autoincrement)
- **`trek_name`** (`String(100)`, Required)
- **`location`** (`String(100)`, Required)
- **`description`** (`Text`, Optional)
- **`difficulty`** (`String(20)`, Required): `'Easy'`, `'Moderate'`, `'Hard'`
- **`duration_days`** (`Integer`, Required): Strictly positive (> 0)
- **`available_slots`** (`Integer`, Required): Non-negative (>= 0)
- **`assigned_staff_id`** (`Integer`, Foreign Key `users.id`, Nullable, `ondelete='SET NULL'`)
- **`status`** (`String(20)`, Required, Default `'Pending'`): `'Pending'`, `'Approved'`, `'Open'`, `'Closed'`, `'Completed'`
- **`start_date`**, **`end_date`** (`Date`, Required): Validated `end_date >= start_date`
- **Relationships:**
  - `assigned_staff`: Relationship to `User` (validated to have role `'Trek Staff'`)
  - `bookings`: One-to-Many with `Booking`

#### 3. Booking Model (`bookings`)
- **`id`** (`Integer`, Primary Key, Autoincrement)
- **`user_id`** (`Integer`, Foreign Key `users.id`, Required, `ondelete='RESTRICT'`)
- **`trek_id`** (`Integer`, Foreign Key `treks.id`, Required, `ondelete='RESTRICT'`)
- **`booking_date`** (`DateTime`, Default `utcnow`)
- **`booking_status`** (`String(20)`, Required, Default `'Booked'`): `'Booked'`, `'Cancelled'`, `'Completed'`
- **`payment_status`** (`String(20)`, Optional, Default `'Pending'`): `'Pending'`, `'Paid'`, `'Failed'`, `'Refunded'`
- **Constraints & Indexes:**
  - Partial unique index `uq_active_user_trek_booking` on `(user_id, trek_id)` where `booking_status = 'Booked'` to prevent duplicate active reservations.

#### 4. Staff Profile Model (`staff_profiles`)
- **`id`** (`Integer`, Primary Key, Autoincrement)
- **`user_id`** (`Integer`, Foreign Key `users.id`, Required, Unique, `ondelete='CASCADE'`)
- **`specialization`** (`String(100)`, Optional)
- **`experience_years`** (`Integer`, Default `0`): Validated non-negative (>= 0)
- **`emergency_contact`** (`String(20)`, Optional)
- **Validation:** Only users with role `'Trek Staff'` can hold a staff profile.

#### 5. Token Blocklist Model (`token_blocklist`)
- **`id`** (`Integer`, Primary Key, Autoincrement)
- **`jti`** (`String(36)`, Required, Unique, Indexed): JWT unique identifier
- **`created_at`** (`DateTime`, Default `utcnow`)

---

## 9. Milestone 2: Authentication & Role-Based Access Control Specification

### 9.1 Authentication Architecture
- **JWT Framework:** `Flask-JWT-Extended` with RFC 7518-compliant HMAC keys.
- **Token Type:** Bearer Access Tokens issued via the `Authorization: Bearer <token>` header.
- **Revocation / Logout Strategy:** Database-backed token blocklist table (`token_blocklist`). On logout, the token's unique identifier (`jti`) is persisted. The `@jwt.token_in_blocklist_loader` checks incoming requests against SQLite, guaranteeing revoked tokens cannot be reused.
- **Password Security:** Salted hashes generated via `werkzeug.security.generate_password_hash` (`scrypt`/`pbkdf2:sha256`). Plaintext passwords and `password_hash` values are never stored or leaked.

### 9.2 API Endpoint Reference

| Method | Endpoint | Access Level | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/auth/register` | Public | Trekker self-registration (role strictly hardcoded to `Trekker`) |
| `POST` | `/api/auth/login` | Public | Authenticates credentials and returns JWT access token + sanitized user object |
| `GET` | `/api/auth/me` | Authenticated | Returns currently authenticated user profile |
| `POST` | `/api/auth/logout` | Authenticated | Revokes current JWT by adding its `jti` to `token_blocklist` |
| `GET` | `/api/admin/dashboard` | Role: Admin | Admin portal placeholder endpoint |
| `GET` | `/api/staff/dashboard` | Role: Trek Staff | Trek Staff portal placeholder endpoint |
| `GET` | `/api/trekker/dashboard` | Role: Trekker | Trekker portal placeholder endpoint |

### 9.3 Standard Response Format

All API endpoints return standardized JSON payloads:

**Success Response (HTTP 200 / 201):**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "access_token": "eyJhbGciOi...",
    "user": {
      "id": 1,
      "full_name": "System Administrator",
      "email": "admin@trekkingapp.local",
      "role": "Admin",
      "status": "Active"
    }
  }
}
```

**Error Response (HTTP 400 / 401 / 403 / 409):**
```json
{
  "success": false,
  "message": "Invalid email or password.",
  "errors": {}
}
```

### 9.4 Role-Based Access Control (RBAC) & Route Protection

Backend enforcement is implemented via `@role_required(*allowed_roles)`:
1. Validates JWT signature, structure, and expiration.
2. Checks token against the SQLite `token_blocklist`.
3. Retrieves user record from the database (never trusts unverified claims or frontend role data).
4. Verifies that `user.status == 'Active'` (rejects `Inactive` or `Blacklisted` with HTTP 403).
5. Verifies that `user.role` matches the route requirements (rejects unauthorized roles with HTTP 403).

### 9.5 Frontend Architecture & Pages (Vue 3 + Vite + Bootstrap)

- **Login Page (`/login`):** Built following web standards (`autofill-sign-in-form`), with semantic markup, proper input types (`type="email"` with `autocomplete="username"`), password visibility toggle, loading indicators, and field-level validation feedback.
- **Trekker Registration Page (`/register`):** Built following web standards (`autofill-sign-up-form`), with single-name input (`autocomplete="name"`), password confirmation verification, and no role selector (strictly registers Trekkers).
- **Admin Dashboard (`/admin/dashboard`):** Role-guarded dashboard placeholder displaying authenticated admin details and confirming backend authorization via `/api/admin/dashboard`.
- **Trek Staff Dashboard (`/staff/dashboard`):** Role-guarded dashboard placeholder displaying staff profile details and confirming backend authorization via `/api/staff/dashboard`.
- **Trekker Dashboard (`/trekker/dashboard`):** Role-guarded dashboard placeholder displaying trekker details and confirming backend authorization via `/api/trekker/dashboard`.
- **Unauthorized Page (`/unauthorized`):** Explanatory access denied page with automated redirect to the user's authorized role dashboard.

**Automated Role-Based Navigation:**
- `Admin` &rarr; `/admin/dashboard`
- `Trek Staff` &rarr; `/staff/dashboard`
- `Trekker` &rarr; `/trekker/dashboard`
- Unauthenticated &rarr; `/login?redirect=...`

---

## 10. Repository Structure

```text
trekking-management-app/
├── .gitignore
├── README.md
├── .venv/                         # Python virtual environment (git-ignored)
├── backend/
│   ├── .env.example               # Environment variables template
│   ├── requirements.txt           # Minimal backend dependencies
│   ├── run.py                     # Application entry point & CLI context
│   ├── instance/                  # SQLite DB storage directory (git-ignored)
│   │   └── tma.db
│   ├── app/
│   │   ├── __init__.py            # Application factory, extensions, JWT callbacks, blueprints
│   │   ├── config.py              # Environment configurations (Base, Dev, Test)
│   │   ├── extensions.py          # SQLAlchemy, JWTManager, CORS instances
│   │   ├── models/
│   │   │   ├── __init__.py        # Models export
│   │   │   ├── user.py            # User model
│   │   │   ├── trek.py            # Trek model
│   │   │   ├── booking.py         # Booking model
│   │   │   ├── staff_profile.py   # StaffProfile model
│   │   │   └── token_blocklist.py # TokenBlocklist model for revoked JWTs
│   │   ├── routes/
│   │   │   ├── __init__.py        # Blueprints export
│   │   │   ├── auth.py            # /api/auth routes (register, login, me, logout)
│   │   │   ├── admin.py           # /api/admin routes (dashboard)
│   │   │   ├── staff.py           # /api/staff routes (dashboard)
│   │   │   └── trekker.py         # /api/trekker routes (dashboard)
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── decorators.py      # @role_required, @active_user_required
│   │       └── responses.py       # success_response, error_response helpers
│   ├── scripts/
│   │   └── create_admin.py        # Programmatic admin account provisioning
│   └── tests/
│       ├── __init__.py
│       ├── test_models.py         # 20 automated tests for schema & constraints
│       ├── test_auth.py           # 15 automated tests for registration, login & profile
│       ├── test_rbac.py           # 9 automated tests for RBAC & token expiration
│       └── test_logout.py         # 2 automated tests for logout & token blocklist
└── frontend/
    ├── package.json               # Vue 3, Vue Router, Bootstrap, Axios
    ├── vite.config.js             # Vite config with backend API proxy
    ├── index.html                 # HTML entry point
    └── src/
        ├── main.js                # App bootstrapping & Bootstrap imports
        ├── App.vue                # Root component layout & footer
        ├── router/
        │   └── index.js           # Vue Router with role-based navigation guards
        ├── services/
        │   ├── api.js             # Axios instance with JWT request/response interceptors
        │   └── auth.js            # Centralized authentication state management
        ├── components/
        │   └── Navbar.vue         # Responsive Bootstrap navigation bar
        └── views/
            ├── LoginView.vue      # Sign-in page
            ├── RegisterView.vue   # Trekker registration page
            ├── AdminDashboardView.vue    # Admin portal placeholder
            ├── StaffDashboardView.vue    # Trek Staff portal placeholder
            ├── TrekkerDashboardView.vue  # Trekker portal placeholder
            └── UnauthorizedView.vue      # HTTP 403 Access Denied view
```

---

## 11. Instructions to Run and Verify (Windows PowerShell)

### Step 1: Backend Setup & Automated Tests

```powershell
# Navigate to project root
cd "D:\iitm'\26t3 sep\MAD2\Trekking-Management-Application"

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install backend dependencies
pip install -r backend/requirements.txt

# Run all 46 automated unit tests
python -m unittest discover backend/tests -v
```

### Step 2: Initialize Database and Provision Admin Account

```powershell
# Set Flask app entry point and initialize database
$env:FLASK_APP = "backend/run.py"
flask init-db

# Provision initial Admin account
$env:ADMIN_INITIAL_PASSWORD = "YourSecurePassword123!"
python backend/scripts/create_admin.py
```

### Step 3: Run the Flask Backend Server

```powershell
# Start Flask development server on port 5000
python backend/run.py
```

### Step 4: Run the Vue Frontend Server

In a second PowerShell terminal:

```powershell
# Navigate to frontend directory
cd "D:\iitm'\26t3 sep\MAD2\Trekking-Management-Application\frontend"

# Install frontend dependencies (if not already installed)
npm install

# Start Vite development server on port 5173
npm run dev
```

Open your browser at `http://localhost:5173` to interact with the application.

---

## 12. License & Academic Integrity

This project is submitted as coursework for the **Modern Application Development II (MAD-II)** course at **IIT Madras**. All work conforms to academic integrity guidelines established by the program.

# Trekking Management Application V2 (TMA)

**Course:** Modern Application Development II (MAD-II)  
**Institution:** Indian Institute of Technology Madras (IIT Madras)  
**Project Status:** Milestone 4 Completed (Trek Staff Dashboard and Trek Operations)

---

## 1. Project Description

The **Trekking Management Application V2 (TMA)** is a multi-user, web-based platform designed to coordinate and streamline trekking expedition logistics, bookings, and operations. The platform facilitates collaboration and communication among three primary user roles: **Administrators**, **Trek Staff**, and **Trekkers (Users)**.

By integrating a responsive frontend with a scalable RESTful backend, TMA aims to provide end-to-end expedition scheduling, participant management, and real-time activity tracking.

> **Project Status Disclaimer:**  
> This repository currently includes **Milestone 0 (Project Setup)**, **Milestone 1 (Database Models & Schema)**, **Milestone 2 (Authentication & Role-Based Access Control)**, **Milestone 3 (Admin Dashboard and Management)**, and **Milestone 4 (Trek Staff Dashboard and Trek Operations)**. Trekker booking self-service workflows, Redis caching, and Celery background workers belong to subsequent milestones.

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
- [x] **Milestone 3: Admin Dashboard and Management (Completed)**
  - Strict Admin authorization enforcing `role == 'Admin'` and `status == 'Active'` across all management endpoints
  - Real database aggregate overview endpoint (`GET /api/admin/dashboard`) returning live counts
  - Complete Trek Management REST APIs (`GET/POST /api/admin/treks`, `GET/PUT/DELETE /api/admin/treks/<id>`)
  - Safe trek deletion strictly preventing data loss if historical bookings exist (HTTP 400 with descriptive guidance)
  - Staff Assignment API (`PUT /api/admin/treks/<id>/assign-staff`) and active staff dropdown endpoint (`GET /api/admin/staff/available`)
  - Staff Management REST APIs (`GET/POST /api/admin/staff`, `GET/PUT /api/admin/staff/<id>`, `PATCH /api/admin/staff/<id>/status`) with atomic User + StaffProfile creation in transaction
  - Trekker User Management REST APIs (`GET /api/admin/users`, `GET/PUT /api/admin/users/<id>`, `PATCH /api/admin/users/<id>/status`) with role mutation forbidden
  - Read-Only Booking Management & History REST APIs (`GET /api/admin/bookings`, `GET /api/admin/bookings/<id>`)
  - Database-derived Reporting & Statistics REST API (`GET /api/admin/reports`)
  - 10 responsive Vue 3 + Bootstrap 5 Admin views with reusable components (`AdminSidebar`, `StatCard`, `Pagination`, `ConfirmationModal`)
  - 80 automated unit tests passing across 8 test suites with isolated in-memory SQLite databases
- [x] **Milestone 4: Trek Staff Dashboard and Trek Operations (Completed)**
  - Strict Trek Staff authorization enforcing `role == 'Trek Staff'` and `status == 'Active'`
  - Absolute data isolation binding queries and operations to `trek.assigned_staff_id == current_user.id` (HTTP 403 on unassigned or foreign treks)
  - Real-time database metrics dashboard (`GET /api/staff/dashboard`) with assigned trek highlights and specialization summary
  - Assigned treks directory (`GET /api/staff/treks`, `GET /api/staff/treks/<id>`) with status, progress, and capacity metrics
  - Capacity management (`PATCH /api/staff/treks/<id>/slots`) strictly preventing slot reduction below active confirmed bookings
  - Booking availability toggle (`PATCH /api/staff/treks/<id>/status`) allowing Open/Closed states while rejecting administrative statuses and modifications to completed expeditions
  - Unidirectional operational progress lifecycle state machine (`PATCH /api/staff/treks/<id>/progress`): `Not Started` -> `Started` -> `Ongoing` -> `Completed` with auto-closing of booking status upon completion
  - Sanitized participant roster API (`GET /api/staff/treks/<id>/participants`) with status filtering, search, and zero exposure of user credentials
  - Responsive Vue 3 + Bootstrap 5 Staff views (`StaffDashboardView.vue`, `StaffTreksView.vue`, `StaffTrekDetailsView.vue`, `StaffParticipantsView.vue`) and `StaffSidebar.vue`
  - 108 automated unit tests passing across 12 test suites
- [ ] **Milestone 5: Trekker Portal, Redis Caching & Celery Background Tasks**
  - Trekker booking & self-service cancellation workflow
  - Redis caching integration for high-traffic catalog queries
  - Celery asynchronous notification pipeline (email alerts & departure reminders)
  - Celery Beat scheduled jobs and monthly reporting
- [ ] **Milestone 6: Verification, Testing & Final Documentation**
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

## 10. Milestone 3: Admin Dashboard & Management Specification

### 10.1 Administrative Authorization & Security
All administrative endpoints are protected under the URL prefix `/api/admin/*` and require:
1. Valid JWT Bearer token in the `Authorization` header.
2. Verified claims checked against the SQLite database: `user.role == "Admin"` and `user.status == "Active"`.
3. Unauthenticated requests receive HTTP 401; non-admin users (Trek Staff, Trekkers) or deactivated/blacklisted admin accounts strictly receive HTTP 403.

### 10.2 REST API Specification

| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/admin/dashboard` | Admin | Real-time database metrics: total treks, users, staff, bookings, open/pending/completed treks, active/blacklisted users |
| `GET` | `/api/admin/treks` | Admin | Paginated list of treks with search by name/ID, filters by difficulty, status, and location |
| `GET` | `/api/admin/treks/<id>` | Admin | Retrieve complete details of a single trek route |
| `POST` | `/api/admin/treks` | Admin | Create a new trek route with capacity, difficulty, dates, and optional assigned staff |
| `PUT` | `/api/admin/treks/<id>` | Admin | Update existing trek details, dates, capacity, or assigned leader |
| `DELETE` | `/api/admin/treks/<id>` | Admin | Safe deletion: permanently removes trek only if 0 bookings exist; returns HTTP 400 if booking history exists |
| `PUT` | `/api/admin/treks/<id>/assign-staff` | Admin | Assign, reassign, or unassign an active Trek Staff user to an expedition |
| `GET` | `/api/admin/staff` | Admin | Paginated list of Trek Staff accounts with search, status filters, and assigned treks count |
| `GET` | `/api/admin/staff/<id>` | Admin | Retrieve staff profile details, contact info, qualifications, and assigned treks |
| `POST` | `/api/admin/staff` | Admin | Atomically provision a new Trek Staff account and associated `StaffProfile` in a database transaction |
| `PUT` | `/api/admin/staff/<id>` | Admin | Update staff user details, contact number, specialization, experience, and emergency contact |
| `PATCH` | `/api/admin/staff/<id>/status` | Admin | Update staff account status (`Active`, `Inactive`, `Blacklisted`) |
| `GET` | `/api/admin/staff/available` | Admin | Retrieve active Trek Staff members for trek creation/assignment dropdowns |
| `GET` | `/api/admin/users` | Admin | Paginated list of registered Trekkers with search by name/email/ID and status filters |
| `GET` | `/api/admin/users/<id>` | Admin | Retrieve single Trekker profile details |
| `PUT` | `/api/admin/users/<id>` | Admin | Update permitted profile fields (`full_name`, `contact_number`); strictly rejects role modification |
| `PATCH` | `/api/admin/users/<id>/status` | Admin | Update Trekker status (`Active`, `Inactive`, `Blacklisted`); blocks modification of Admin accounts |
| `GET` | `/api/admin/bookings` | Admin | Read-only audit log of participant reservations with status filters and search |
| `GET` | `/api/admin/bookings/<id>` | Admin | Retrieve single booking details with associated user and trek metadata |
| `GET` | `/api/admin/reports` | Admin | Live database-aggregated reporting metrics: difficulty & status distributions, popular treks, monthly activity |

### 10.3 Safe Deletion & Data Integrity
To preserve complete financial and operational audit trails:
- **Trek Deletion:** An expedition cannot be hard-deleted if any booking records (active, cancelled, or completed) exist in SQLite. The API returns HTTP 400 with actionable advice to set the trek status to `'Closed'` or `'Completed'` instead.
- **Atomic Staff Provisioning:** Both `User` and `StaffProfile` records are committed inside a unified database transaction. If profile creation fails, the user is rolled back, preventing orphaned accounts.
- **Role Escalation Prevention:** Role mutation through user management endpoints is strictly forbidden (HTTP 400). Admin accounts cannot be deactivated via general user routes.

### 10.4 Frontend Admin Interface (Vue 3 + Bootstrap 5)
The administrative frontend is implemented as a cohesive Single Page Application with 10 dedicated views and reusable modular components:

1. **`AdminDashboardView.vue` (`/admin/dashboard`):** Real-time metric cards, operational distributions, health indicators, and quick-action links.
2. **`ManageTreksView.vue` (`/admin/treks`):** Comprehensive trek catalog table, search toolbar, difficulty & status filters, pagination, and safe deletion modal.
3. **`CreateTrekView.vue` (`/admin/treks/create`):** Full trek route creation form with available staff dropdown selector and date validation.
4. **`EditTrekView.vue` (`/admin/treks/:id/edit`):** Expedition configuration form supporting date adjustments and staff allocation.
5. **`ManageStaffView.vue` (`/admin/staff`):** Staff guide directory displaying specializations, experience, assigned treks count, and one-click status toggle actions.
6. **`CreateStaffView.vue` (`/admin/staff/create`):** Staff account provisioning form with initial credentials and field specialization details.
7. **`EditStaffView.vue` (`/admin/staff/:id/edit`):** Staff profile modification form with real-time assigned trek roster sidebar.
8. **`ManageUsersView.vue` (`/admin/users`):** Trekker directory with search, booking counts, inline profile editing modal, and account status management.
9. **`ManageBookingsView.vue` (`/admin/bookings`):** Read-only booking audit table with status filtering and detailed reservation modal dialog.
10. **`ReportsView.vue` (`/admin/reports`):** Live analytics dashboard displaying difficulty breakdowns, status distributions, popular trek rankings, and monthly activity progress bars.

**Reusable Components:**
- **`AdminSidebar.vue`:** Sleek sidebar navigation with active route highlights.
- **`StatCard.vue`:** Configurable metric card with colored icons and subtitles.
- **`Pagination.vue`:** Reusable pagination controls with previous/next and dynamic page number buttons.
- **`ConfirmationModal.vue`:** Modal dialog for action confirmation.

---

## 11. Milestone 4: Trek Staff Dashboard and Trek Operations

### 11.1 Authorization & Strict Data Isolation
All staff endpoints enforce strict role-based access control and tenant-level data isolation:
- **RBAC Enforcement:** Access is granted strictly to authenticated users with role `'Trek Staff'` and active status `'Active'`. Incomplete profiles (missing associated `StaffProfile`) or inactive accounts receive HTTP 403 Forbidden.
- **Ownership Binding:** The backend extracts the authenticated staff member's ID exclusively from the verified JWT identity (`g.current_user.id`). Never trusts staff IDs supplied by client payloads.
- **Data Isolation:** All trek queries automatically filter by `Trek.assigned_staff_id == current_user.id`. Any direct attempt to inspect, operate, or view participants of a trek not assigned to the authenticated staff member immediately returns HTTP 403 Forbidden with `"You are not authorized to access this trek."`. Unassigned treks cannot be accessed by staff.

### 11.2 Status Architecture Separation
TMA strictly separates administrative booking availability from on-ground field execution:
- **Booking Availability (`status`):**
  - Allowed values: `'Pending'`, `'Approved'`, `'Open'`, `'Closed'`, `'Completed'`.
  - Staff permissions: Staff can only toggle between `'Open'` (accepting bookings) and `'Closed'` (temporarily halting bookings).
  - Restrictions: Staff cannot set administrative statuses (`'Pending'`, `'Approved'`). Completed treks cannot be reopened by staff.
- **Operational Progress Lifecycle (`operational_progress` / `progress`):**
  - Allowed stages: `'Not Started'`, `'Started'`, `'Ongoing'`, `'Completed'`.
  - State machine rules:
    - `'Not Started'` &rarr; `'Started'`, `'Ongoing'`
    - `'Started'` &rarr; `'Ongoing'`, `'Completed'`
    - `'Ongoing'` &rarr; `'Completed'`
    - `'Completed'` &rarr; Terminal stage (no further transitions permitted)
  - Backwards transitions (e.g. `'Ongoing'` &rarr; `'Not Started'`) are rejected with HTTP 400 Bad Request.
  - Automatic side-effect: Transitioning to `'Completed'` automatically closes booking availability (`status = 'Closed'`).

### 11.3 Trek Staff REST API Endpoints

| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/staff/dashboard` | Trek Staff | Aggregate live metrics: total assigned treks, open/closed counts, ongoing/completed counts, active participants, and assigned trek summaries |
| `GET` | `/api/staff/treks` | Trek Staff | Paginated list of assigned treks with search, status filter, progress filter, and capacity tracking |
| `GET` | `/api/staff/treks/<id>` | Trek Staff | Detailed overview of an assigned trek with capacity and participant counts (returns 403 if unassigned) |
| `PATCH` | `/api/staff/treks/<id>/slots` | Trek Staff | Update available slots; strictly rejects reducing capacity below current active confirmed bookings (`booking_status == 'Booked'`) |
| `PATCH` | `/api/staff/treks/<id>/status` | Trek Staff | Toggle booking availability between `'Open'` and `'Closed'` only; rejects administrative statuses and completed trek edits |
| `PATCH` | `/api/staff/treks/<id>/progress` | Trek Staff | Advance operational lifecycle following unidirectional state machine rules; auto-closes booking status upon completion |
| `GET` | `/api/staff/treks/<id>/participants` | Trek Staff | Participant roster with active vs cancelled counts, status filtering, and zero exposure of user passwords |

### 11.4 Participant Privacy & Safety Guards
- **Zero Credential Leaks:** Queries and responses for participant rosters explicitly exclude `password_hash` and sensitive auth tokens.
- **Active vs Cancelled Distinction:** Cleanly separates active confirmed reservations (`booking_status == 'Booked'`) from cancelled reservations (`booking_status == 'Cancelled'`), providing accurate headcounts for field logistics.

### 11.5 Frontend Staff Portal (Vue 3 + Bootstrap 5)
The Trek Staff interface includes 4 dedicated views and navigation components:
1. **`StaffSidebar.vue`:** Staff navigation sidebar highlighting active routes and displaying staff profile summary.
2. **`StaffDashboardView.vue` (`/staff/dashboard`):** Real-time metric cards (assigned treks, open for booking, active participants, completed treks), staff credentials summary, and active expedition table with direct operational links.
3. **`StaffTreksView.vue` (`/staff/treks`):** Comprehensive table of assigned expeditions with live search, status and progress filters, visual capacity bars, and quick slot editing modal.
4. **`StaffTrekDetailsView.vue` (`/staff/treks/:id`):** Mission control view featuring an interactive visual stepper for operational progress transitions, one-click booking status toggle, capacity adjustment form, and direct link to participant rosters.
5. **`StaffParticipantsView.vue` (`/staff/treks/:id/participants`):** Participant roster view featuring active/cancelled breakdown cards, search toolbar, status filter, and privacy-shielded contact cards.

---

## 12. Repository Structure

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
│   │   │   ├── user.py            # User model with role validation & serialization
│   │   │   ├── trek.py            # Trek model with capacity, progress & date validation
│   │   │   ├── booking.py         # Booking model with partial unique index
│   │   │   ├── staff_profile.py   # StaffProfile model for Trek Staff users
│   │   │   └── token_blocklist.py # TokenBlocklist model for revoked JWTs
│   │   ├── routes/
│   │   │   ├── __init__.py        # Blueprint registrations
│   │   │   ├── auth.py            # /api/auth routes (register, login, me, logout)
│   │   │   ├── admin.py           # /api/admin/dashboard overview route
│   │   │   ├── admin_treks.py     # /api/admin/treks CRUD & staff assignment routes
│   │   │   ├── admin_staff.py     # /api/admin/staff CRUD & status management routes
│   │   │   ├── admin_users.py     # /api/admin/users trekker management routes
│   │   │   ├── admin_bookings.py  # /api/admin/bookings read-only audit routes
│   │   │   ├── admin_reports.py   # /api/admin/reports aggregate analytics routes
│   │   │   ├── staff.py           # /api/staff routes (dashboard, treks, operations, participants)
│   │   │   └── trekker.py         # /api/trekker routes (dashboard)
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── decorators.py      # @role_required, @active_user_required
│   │       └── responses.py       # success_response, error_response helpers
│   ├── scripts/
│   │   └── create_admin.py        # Programmatic admin account provisioning
│   └── tests/
│       ├── __init__.py
│       ├── test_models.py             # 20 automated tests for schema & constraints
│       ├── test_auth.py               # 15 automated tests for registration, login & profile
│       ├── test_rbac.py               # 9 automated tests for RBAC & token expiration
│       ├── test_logout.py             # 2 automated tests for logout & token blocklist
│       ├── test_admin_dashboard.py    # 3 automated tests for admin dashboard statistics
│       ├── test_admin_treks.py        # 7 automated tests for trek CRUD & safe deletion
│       ├── test_admin_staff.py        # 6 automated tests for staff creation, hashing & status
│       ├── test_admin_users.py        # 6 automated tests for trekker management & escalation guards
│       ├── test_admin_assignments.py  # 3 automated tests for staff allocation & reassignments
│       ├── test_admin_bookings.py     # 3 automated tests for read-only booking history
│       ├── test_admin_reports.py      # 3 automated tests for database aggregates & rankings
│       ├── test_admin_auth.py         # 3 automated tests for 401/403 authorization enforcement
│       ├── test_staff_dashboard.py    # 5 automated tests for staff metrics, isolation & RBAC
│       ├── test_staff_treks.py        # 7 automated tests for assigned trek listing & 403 isolation
│       ├── test_staff_operations.py   # 11 automated tests for slots, status, and progress state machine
│       └── test_staff_participants.py  # 5 automated tests for roster retrieval & privacy
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
        │   ├── Navbar.vue             # Responsive Bootstrap navigation bar
        │   ├── AdminSidebar.vue       # Administrative navigation sidebar
        │   ├── StaffSidebar.vue       # Trek Staff navigation sidebar
        │   ├── StatCard.vue           # Reusable metric card component
        │   ├── Pagination.vue         # Reusable table pagination component
        │   └── ConfirmationModal.vue  # Reusable action confirmation dialog
        └── views/
            ├── LoginView.vue          # Sign-in page
            ├── RegisterView.vue       # Trekker registration page
            ├── AdminDashboardView.vue # Admin overview portal
            ├── ManageTreksView.vue    # Trek catalog management view
            ├── CreateTrekView.vue     # New trek route creation form
            ├── EditTrekView.vue       # Trek route modification form
            ├── ManageStaffView.vue    # Trek staff directory & status view
            ├── CreateStaffView.vue    # Staff provisioning form
            ├── EditStaffView.vue      # Staff profile editing form
            ├── ManageUsersView.vue    # Trekker account management view
            ├── ManageBookingsView.vue # Read-only booking audit view
            ├── ReportsView.vue        # Administrative analytics view
            ├── StaffDashboardView.vue # Trek Staff metrics dashboard view
            ├── StaffTreksView.vue     # Trek Staff assigned expeditions list view
            ├── StaffTrekDetailsView.vue # Trek Staff operations & lifecycle view
            ├── StaffParticipantsView.vue # Trek Staff participant roster view
            ├── TrekkerDashboardView.vue # Trekker portal placeholder
            └── UnauthorizedView.vue   # HTTP 403 Access Denied view
```

---

## 13. Instructions to Run and Verify (Windows PowerShell)

### Step 1: Backend Setup & Automated Tests

```powershell
# Navigate to project root
cd "D:\iitm'\26t3 sep\MAD2\Trekking-Management-Application"

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install backend dependencies (if needed)
pip install -r backend/requirements.txt

# Run all 108 automated unit tests (Milestone 1, 2, 3, and 4)
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

### Step 4: Build and Run the Vue Frontend

In a second PowerShell terminal:

```powershell
# Navigate to frontend directory
cd "D:\iitm'\26t3 sep\MAD2\Trekking-Management-Application\frontend"

# Build production bundle (confirms zero compile errors)
npm run build

# Start Vite development server on port 5173
npm run dev
```

Open your browser at `http://localhost:5173` and log in with your Admin credentials to access the Admin Management Suite.

---

## 14. License & Academic Integrity

This project is submitted as coursework for the **Modern Application Development II (MAD-II)** course at **IIT Madras**. All work conforms to academic integrity guidelines established by the program.

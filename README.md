# Trekking Management Application V2 (TMA)

**Course:** Modern Application Development II (MAD-II)  
**Institution:** Indian Institute of Technology Madras (IIT Madras)  
**Project Status:** Initial Setup (Milestone 0)

---

## 1. Project Description

The **Trekking Management Application V2 (TMA)** is a multi-user, web-based platform designed to coordinate and streamline trekking expedition logistics, bookings, and operations. The platform facilitates collaboration and communication among three primary user roles: **Administrators**, **Trek Staff**, and **Trekkers (Users)**.

By integrating a responsive frontend with a scalable RESTful backend, TMA aims to provide end-to-end expedition scheduling, participant management, and real-time activity tracking.

> **Project Status Disclaimer:**  
> This repository represents the **initial project setup (Milestone 0)**. Core application features, database models, business logic, and authentication mechanisms are planned for development in subsequent milestones and are **not yet implemented**.

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

- [x] **Milestone 0: Project Setup & Repository Initialization (Current)**
  - Initialize Git version control on branch `main`
  - Establish `.gitignore` rules for Python, Flask, SQLite, Redis, Celery, and Vue/Node environments
  - Document system architecture, objectives, and technology stack in `README.md`
  - Prepare repository for GitHub hosting
- [ ] **Milestone 1: Database Architecture & Core REST API**
  - Schema design with SQLAlchemy (Users, Roles, Treks, Batches, Bookings)
  - Core CRUD endpoints for trek routes and schedules
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

## 8. Repository Structure (Planned)

```text
trekking-management-app/
├── .gitignore
├── README.md
├── backend/                  # (To be added in future milestones)
│   ├── app/
│   │   ├── models/           # SQLAlchemy models
│   │   ├── routes/           # Flask API blueprints
│   │   ├── tasks/            # Celery background workers
│   │   └── utils/
│   ├── instance/             # SQLite DB files (git-ignored)
│   ├── config.py
│   ├── requirements.txt
│   └── run.py
└── frontend/                 # (To be added in future milestones)
    ├── public/
    ├── src/
    │   ├── assets/
    │   ├── components/
    │   ├── views/
    │   ├── router/
    │   └── App.vue
    └── package.json
```

---

## 9. License & Academic Integrity

This project is submitted as coursework for the **Modern Application Development II (MAD-II)** course at **IIT Madras**. All work conforms to academic integrity guidelines established by the program.


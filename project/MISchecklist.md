# MIS & Admin Site Checklist

This checklist focuses on the **Management Information System (MIS)**, including the Django Admin panel, RBAC permissions, and the custom Staff/Manager portals (`/portal/`).

## 1. User & Access Management (RBAC)
- [x] **Role definitions**:
  - `Superuser`: Full system access.
  - `Manager`: Can view all tasks (`Team View`), manage campaigns/projects, assign tasks.
  - `Staff`: Can only view assigned tasks and update their status.
- [x] **Group Configuration**: Created "Managers" group with elevated permissions.
- [x] **Staff Profiles**: Extended `User` model to include contact details (`StaffProfile`).
- [x] **Auto-Setup**: Scripts to auto-create demo users (`manager1`, `staff1`) and Groups on initialization.

## 2. Admin Panel Configuration (`/admin`)
### General Configuration
- [x] **Filters & Search**: Added `list_filter` and `search_fields` to all major models (`Task`, `BloodDonor`, `Project`).
- [x] **Inlines**:
  - [x] `SubTask` inline within `Task`.
  - [x] `StaffProfile` inline within `User`.
- [x] **Many-to-Many Widgets**: Used `filter_horizontal` for Project Managers for better UI.
- [x] **Rich Text/Slugs**: configured `prepopulated_fields` for Projects.

### Module-Specific Admin Features
- [x] **Task Management**: Admins can bulk-assign tasks or change priorities.
- [x] **Content Management**: Full CRUD for `Campaigns`, `Projects`, and `Announcements`.
- [x] **Donor Management**: View and filter donor registry by Blood Group and City.

## 3. MIS Portals (`/portal`)
### Staff Dashboard (My Views)
- [x] **Kanban/Grid View**: Visual card layout for tasks.
- [x] **Status Workflow**: One-click status toggling (`To Do` -> `Done`).
- [x] **Bulletin Board**: Read-only view of active `Announcements`.
- [x] **Impact Stats**: Personal or System-wide impact counters (e.g., Total Donors).

### Manager Dashboard (Team Views)
- [x] **Global Task View**: See tasks assigned to *anyone*, sorted by priority/status.
- [x] **Critical Alerts**: Highlight `Critical` priority tasks at the top.
- [x] **Statistics**: Quick summary of `Pending` vs `Completed` tasks.
- [x] **Workload Visualizer**: (Pending) Charts showing tasks per staff member.

## 4. Reporting & Analytics
- [x] **Operational Reports**:
  - [x] Blood Request fulfillment status (via filtering).
  - [x] Active Project timelines.
- [ ] **Advanced MIS Reports** (Pending):
  - [x] **Export to CSV/PDF**: Button to download Donor Registry or Task logs.
  - [ ] **Audit Logs**: Who changed what (using `django-simple-history` or similar).
  - [ ] **Trend Analysis**: "Donations per Month" charts.

## 5. System Health & Automation
- [x] **Email Automation**:
  - [x] Alerts on Task Assignment.
  - [x] Alerts on New Blood Requests (to Managers).
- [x] **Database Integrity**:
  - [x] Unique constraints (e.g., Phone Numbers).
  - [x] ForeignKey protections (`on_delete` policies).
- [ ] **Backup & Maintenance**:
  - [ ] Automated daily database backups.
  - [ ] Log rotation for server logs.

# Portal Overhaul & Enhancements Checklist

This checklist covers the recent major updates to the Staff & Manager Portal (Phases 10 & 11) to create a dedicated "UDAAN Workspace".

## 1. Portal Overhaul (Phase 10)
- [x] **URL Restructuring**: Moved portal from `/portal/` to `/admin/portal/` for better integration.
- [x] **Dedicated Layout**: Created `portal_layout.html` with a modern sidebar and no public website headers.
- [x] **New Visual Theme**: Implemented a "Glassmorphism" design with brand colors (Red/Blue/White) and `outfit` font.
- [x] **Personal Notes**:
    - [x] Created `PersonalNote` model (User-specific scratchpad).
    - [x] Added a slide-out drawer on the right side for taking notes.
    - [x] Enabled auto-saving logic via API.

## 2. Global Access & Enhancements (Phase 11)
- [x] **Global Access Button**: Added a floating "My Workspace" button to the public site (visible only to logged-in users).
- [x] **UI Polish**:
    - [x] **Fade-in Animation**: Added smooth page load transitions.
    - [x] **Hover Effects**: Cards on the dashboard lift and shadow on hover.
    - [x] **Dynamic Greeting**: Dashboard greets users with "Good Morning/Afternoon/Evening".
- [x] **Recent Activity Widget**: Added a section to the Staff Dashboard showing the last 5 updated tasks.

## 3. Profile Management (Phase 14)
- [x] **Profile Form**: User and StaffProfile editing (Phone, Email, Name).
- [x] **Sidebar Link**: "Edit Profile" link added to the portal sidebar.

## 4. Automated Workflows (Phase 15)
- [x] **Donor Eligibility**: Automatic 90-day check for blood donors.
- [x] **Process Enforcement**: Strict status lifecycle for Blood Requests.
- [x] **Star Donors**: Automated scoring system to identify top contributors.

## 5. Advanced Reporting & Visualization (Phase 16)
- [x] **Data Export**: CSV export for Donors and Blood Requests (Manager Only).
- [x] **Visual Calendar**: FullCalendar integration in Staff Dashboard for Tasks/Appointments.
- [x] **Smart Heuristics**: "Best Time to Call" insight on Donor Detail page.

## 6. Team Spaces & Kanban (Phase 17)
- [x] **Team Management**: Manager can create teams and add members.
- [x] **Kanban Board**: Interactive Drag-and-Drop tasks between columns.
- [x] **Team Visibility**: Shared board for all team members.
- [x] **Manager Overview**: Aggregated Kanban board for all tasks in "Team Overview".

## 7. Jira-Style Navigation & Workspaces (Phase 22)
- [x] **Quick Switcher**: Ctrl+K style quick navigation added to the Sidebar search icon.
- [x] **Quick Add FAB**: Floating button added to create Tasks, Notes, and Teams instantly.
- [x] **Unified Timeline View**: Merged visual interaction history inside Donor Details page.
- [x] **Sub-Tasks UI**: Checkable checklist format integrated into the Task detailed modal overlay.

## 8. Verification
- [x] **Staff Access**: Verified `staff1` can access the new layout and features.
- [x] **Manager Access**: Verified `manager1` sees the "Team Overview" in the sidebar.
- [x] **Responsiveness**: Verified layout works on mobile (hamburger menu for sidebar).

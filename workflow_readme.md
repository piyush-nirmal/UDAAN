# Udaan Society Web Portal - Workflow Documentation

This document outlines the core workflows, data architectures, and operational procedures of the Udaan Society Web Portal. 

## 1. Blood Donation & Request Workflow

The blood request management system is built on a Finite State Machine (FSM) to ensure structured operations.

### Blood Request Lifecycle
1. **Received**: A new blood request is initiated either by a patient/hospital via the public portal or internally by staff.
2. **Verified**: Staff verifies the details, ensuring the request is genuine and the required units and blood group are correctly documented.
3. **Fulfilling**: The search for suitable donors begins. The system tracks this active fulfillment phase.
4. **Closed**: The request is marked as completed (blood arranged) or cancelled.

### Donor Management Workflow
- **Registration**: Donors register with their blood group, location, and contact details.
- **Heuristic Call Timing**: The system automatically suggests the "Best Time to Call" based on the donor's location (e.g., Metro cities default to Evening, others to Morning).
- **Donation Tracking**: Every donation is logged, updating the donor's `last_donation_date`, `donation_count`, and a calculated `score`.

## 2. Fundraising & Campaign Workflow

Campaigns undergo a structured approval and verification process to ensure transparency and compliance.

### Campaign Creation & Verification
1. **Drafting**: Users or staff create a campaign draft (`CampaignDraft`), saving steps iteratively.
2. **Submission**: Upon submission, the campaign enters a status (e.g., `Pending Review` or `Under Verification`).
3. **Documentation**:
   - **Beneficiary Details**: Linked to specify who receives the funds (Myself, Someone Else, Organization).
   - **Medical Details**: Includes hospital name, diagnosis, estimated cost, and required documents (prescriptions, hospital letters).
   - **Bank Account**: Beneficiary bank details are captured. IFSC codes are verified via an external API.
   - **KYC Document**: Contains Aadhaar, PAN, Passport, and Selfie. A biometric face match score and verification status (`Pending`, `Verified`, `Rejected`) track KYC compliance.
4. **Approval**: Once all documents are verified, the campaign status becomes `Approved` and goes live.

### Donation & Updates
- **Fund Tracking**: Tracks `goal_amount` versus `raised_amount` with visual progress indicators.
- **Updates**: Campaign organizers can post updates (`CampaignUpdate`) with images to keep donors informed.

## 3. Internal Workspace & Task Management (HR & Ops)

The internal portal functions as an ERP/CRM for staff and volunteers, structured hierarchically.

### Workspaces & Teams
- **Workspaces**: High-level organizational units (e.g., "Operations", "Marketing") owned by specific users.
- **Teams**: Sub-groups within workspaces for granular member management.
- **Roles**: Access is governed by roles (`Admin`, `Member`, `Viewer`).

### Task Management Workflow
- **Task Creation**: Tasks are created within projects or assigned directly. They track `status` (To Do, In Progress, Review, Done) and `priority`.
- **Advanced Features**:
  - **Dependencies**: Tasks can block other tasks. A task cannot progress if its dependencies are unmet.
  - **Recurrence**: Tasks can be set to recur (Daily, Weekly, Monthly).
  - **GPS Tagging**: Completion of field tasks can capture GPS coordinates and timestamps.
  - **Subtasks & Comments**: Granular tracking and team communication on tasks.
- **Automations**: Trigger-action rule engines streamline operations (e.g., auto-assigning or sending notifications).

### Knowledge Base (Notion-style)
- **Shared Notes**: Collaborative wikis where notes can be nested under parent notes and shared across teams or individual users.

## 4. CRM & MIS Analytics

### Interaction Tracking
- **Generic Logging**: Interactions (Calls, Meetings, Emails, Visits) can be linked dynamically to any entity (Donors, Campaigns, Projects) using Generic Foreign Keys.
- **Follow-ups**: Interactions log outcomes (`Interested`, `Follow-up Scheduled`, etc.) and can automatically trigger follow-up tasks if a `next_followup_date` is set.
- **Appointments**: Scheduled meetings linked to staff and external entities.

### Expense Management
- **Expense Logging**: Operational, Marketing, or Medical expenses are logged and linked to specific Campaigns or Projects.
- **Receipts**: Staff upload receipt images and categorize the spending for financial auditing.

## 5. AI Chatbot Integration Workflow

The portal incorporates an advanced RAG (Retrieval-Augmented Generation) Chatbot as a microservice.

- **Architecture**: Runs independently on FastAPI, separate from the core Django monolith.
- **Routing**: The Nginx reverse proxy routes frontend widget requests (`/chatbot_api/`) to the AI microservice.
- **Context Handling**: The chatbot maintains session history locally, providing contextual and intelligent responses to public queries regarding policies, donations, and campaigns.
- **WhatsApp Integration**: Contains webhook listeners for Twilio to serve the same AI responses via WhatsApp.

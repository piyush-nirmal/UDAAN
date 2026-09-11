# Udaan Society Web Portal

![Udaan Society Portal](https://via.placeholder.com/1200x400.png?text=Udaan+Society+Web+Portal)

## 📖 About the Project

The **Udaan Society Web Portal** is a comprehensive, full-stack enterprise platform built to manage all digital and operational aspects of the Udaan NGO. What started as a platform to manage blood donation requests has rapidly evolved into a monolithic ERP/CRM system supported by an advanced AI microservice.

This platform seamlessly handles external public engagement (blogs, donations, campaigns) and internal organizational management (task management, human resources, workspaces, and analytics).

---

## ✨ Key Features & Modules

### 1. 🩸 Core Operations (Blood Donation & Campaigns)
- **Blood Requests & FSM Tracking**: State-machine-based tracking of blood requests (Received → Verified → Fulfilling → Closed).
- **Donor Management**: Intelligent donor profiling with heuristic algorithms suggesting the "Best Time to Call" based on donor location and history.
- **Fundraising Campaigns**: Track financial goals, raised amounts, and linked expenses.

### 2. 🏢 Internal Workspaces & HR (Monday.com / Notion Clone)
- **Workspaces & Teams**: Hierarchical role-based access control with distinct Workspaces and Teams for internal coordination.
- **Task Management**: Monday.com-style task tracking with subtasks, comments, recurring deadlines, dependencies, and GPS tagging.
- **Task Automations**: Trigger-action rule engine (e.g., "When Task is Done, Send Email to Manager").
- **Shared Notes**: Notion-style collaborative wikis that can be nested and shared across teams.

### 3. 🤝 CRM & MIS Analytics
- **Interaction Tracking**: Keep logs of calls, emails, and meetings linked generically to donors, volunteers, or partners.
- **MIS Expense Tracking**: Monitor operational, marketing, and logistical expenses linked directly to ongoing campaigns.
- **Job & Ambassador Portals**: Manage full-time hiring, internships, and Campus Ambassador applications.
- **Rich Content Management (CMS)**: Manage dynamic blogs, policies, news clippings, and reports utilizing CKEditor 5.

### 4. 🤖 NEW: Advanced AI Chatbot Integration
We have integrated a state-of-the-art **Retrieval-Augmented Generation (RAG) AI Chatbot** powered by Google Gemini. 
- **Standalone Microservice**: Built on **FastAPI**, it runs in complete isolation from the Django monolith, ensuring high performance.
- **Context-Aware Memory**: Remembers session history via a local SQLite database, allowing for contextual, human-like conversations.
- **Web UI Widget**: A highly responsive frontend widget seamlessly communicates with the AI backend.
- **WhatsApp Webhook Ready**: Contains Twilio webhook integrations (`/api/whatsapp`) to serve users directly on WhatsApp via TwiML responses.

---

## 🏗️ System Architecture & Tech Stack

The production environment is 100% containerized using Docker, orchestrating four distinct services:

1. **`web` (Django/Gunicorn)**: The core backend framework handling ORM, routing, and all NGO business logic (Python).
2. **`ai_chatbot` (FastAPI/Uvicorn)**: The dedicated Python microservice handling AI processing and Twilio webhook routing.
3. **`db` (PostgreSQL 15)**: The robust relational database storing all core application data.
4. **`nginx` (Reverse Proxy)**: The traffic cop. It serves static/media files directly, routes standard web traffic to Django, and securely proxies `/chatbot_api/` requests to the FastAPI service.

---

## 💻 Local Development Setup

For local testing and feature development, we have simplified the process:

1. Create Python Virtual Environments and install dependencies for both the main app (`requirements.txt`) and the chatbot (`ai_chatbot/requirements.txt`).
2. Add your `.env` variables (including `GEMINI_API_KEY` inside `ai_chatbot/.env`).
3. Double click the **`start_dev.bat`** file (Windows). 
   - This automatically spins up **Django on Port 8000** and **FastAPI on Port 8001** in separate terminal windows.
   - The chatbot widget is configured to intelligently detect local environments and connect to 8001 directly.

---

## 🚀 Production Deployment Guide

Deploying to a VPS (Hostinger, DigitalOcean, AWS EC2) is incredibly simple thanks to our Docker configuration.

### 1. Server Setup
SSH into your Ubuntu server and install Docker:
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

### 2. Environment Variables
Clone the repository and create a `.env` file in the root directory:
```env
DEBUG=False
SECRET_KEY=your_secure_random_string
DJANGO_ALLOWED_HOSTS=yourdomain.com,your_vps_ip
DATABASE_URL=postgres://postgres:postgres@db:5432/postgres
GEMINI_API_KEY=your_google_gemini_api_key
```

### 3. Build and Launch
Run the following command to download images, build the custom FastAPI/Django containers, and launch the network in detached mode:
```bash
docker compose up --build -d
```

### 4. Database Seeding & Admin Creation
Because the production Postgres database starts empty, run the migrations:
```bash
docker compose exec web python manage.py migrate
```
Generate the master admin user (`mail@udaansociety.org` / `udaanpassword123`):
```bash
docker compose exec web python manage.py init_admin
```
*(⚠️ **CRITICAL**: Log into `yourdomain.com/admin` immediately to change the default password!)*

---

## 🛠️ Routine Maintenance Commands

- **View Live Logs** (for debugging web or AI traffic):
  ```bash
  docker compose logs -f
  ```
- **Stop the Servers** (safely preserves data):
  ```bash
  docker compose down
  ```
- **🛑 Factory Reset (DANGER)**: Wipes the entire database and uploaded media to start completely fresh:
  ```bash
  docker compose down -v
  ```

---
*Developed & Maintained for Udaan Society.*

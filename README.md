# Placement Portal (MAD2)

A modern, high-performance web application for managing institute campus recruitment, placement drives, candidate applications, automated reporting, and background job processing.

Built with **Flask (RESTful JSON API)**, **Vue.js 3 (Single Page Application)**, **Flask-JWT-Extended**, **Redis Caching**, and **Celery & Celery Beat**.

---

## Key Features

- **Role-Based Access & Authentication**: Unified role claims via JWT (`Admin`, `Company`, `Student`). Gated company approval flow and programmatic single admin account.
- **Admin Dashboard & Controls**: Platform metrics, company & drive approval queues, student/company blacklisting, fuzzy search across all entities, and broadcast notifications.
- **Company Portal**: Profile management, drive creation (gated by admin approval), applicant tracking, candidate shortlisting, interview scheduling, offer management, and CSV data export.
- **Student Dashboard**: Browse approved drives, CGPA eligibility checking, 1-click application submission, application status timeline tracking, placement history, and application CSV export.
- **Asynchronous Background Jobs (Celery & Redis)**:
  - **Daily Scheduled Job**: Automated interview reminders via email & in-app notifications (Celery Beat at 8:00 AM daily).
  - **Monthly Activity Report**: Automated HTML email & PDF report generation for Admin & Companies on the 1st of every month at 6:00 AM.
  - **User-Triggered Async Export**: Background CSV export for student application history & company placement analytics.
- **Redis Caching & Performance**: Standardized Redis caching with 5-minute TTL, write-invalidation namespaces, fallback safety, and dynamic response timing (`X-Response-Time` headers).

---

## Architecture & Tech Stack

- **Backend**: Python 3, Flask 3.x, Flask-RESTful, Flask-SQLAlchemy (SQLite / PostgreSQL ready), Flask-JWT-Extended, Flask-CORS
- **Frontend**: Vue.js 3 (SPA), Vue Router, Bootstrap 5, Vanilla CSS
- **Caching & Async Queue**: Redis (DB 0 for Celery broker/backend, DB 1 for Flask-Caching)
- **Background Tasks**: Celery 5.x & Celery Beat
- **PDF Generation**: `fpdf2`

---

## Setup Instructions

### 1. Prerequisites
- Python 3.8+
- Redis Server (`redis-server`) installed and running on `localhost:6379`

### 2. Virtual Environment & Dependencies
```bash
# Create & activate virtual environment
python -m venv venv
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 3. Initialize & Seed Database
```bash
python init_db.py
```
*This creates the database schema (`placement_portal.db`) and populates realistic demo data (Admin, approved/pending/rejected/blacklisted companies, drives across all states, student applications with full status log chains, interviews, and placements).*

---

## Running the Application

For full functionality (including background jobs and caching), open **3 terminal windows**:

### Terminal 1: Flask Web App (Frontend + API)
```bash
python app.py
```
> App runs at: `http://127.0.0.1:5000`

### Terminal 2: Celery Worker (Background Tasks)
```bash
celery -A celery_worker.celery worker --loglevel=info
```

### Terminal 3: Celery Beat (Scheduled Jobs)
```bash
celery -A celery_worker.celery beat --loglevel=info
```

*(Note: Ensure Redis is running in the background via `redis-server`)*

---

## Default Test Credentials

Running `init_db.py` creates pre-configured demo accounts for all states:

### 1. Admin Account
* **Role**: Admin
* **Email**: `admin@placementportal.com`
* **Password**: `admin123`

### 2. Company Accounts
* **Approved Company**: `hr@technova.com` | Password: `password123`
* **Approved Company 2**: `careers@globalfinance.com` | Password: `password123`
* **Pending Approval Company**: `contact1@startup.com` | Password: `password123` *(Blocked from login until approved)*
* **Rejected Company**: `admin@sketchy.com` | Password: `password123`
* **Blacklisted Company**: `hr@technova.com` *(Blacklisted state demo)*

### 3. Student Accounts
* **Student 1 (Empty Profile)**: `student1@test.com` | Password: `password123` *(Tests missing resume/CGPA UI)*
* **Student 2 (Active Applicant)**: `student2@test.com` | Password: `password123` *(Has applications, interview, and offer)*
* **Student 3 (Blacklisted)**: `student3@test.com` | Password: `password123` *(Blocked from login)*
* **Students 4–9**: `student4@test.com` through `student9@test.com` | Password: `password123`
* **Student 10 (Zero Applications)**: `student10@test.com` | Password: `password123` *(Tests empty dashboard state)*

---

## Quick Testing Commands & Demo Shortcuts

### 1. Test Daily Reminders Task (Instant)
```bash
python -c "from tasks import send_interview_reminders; print(send_interview_reminders())"
```

### 2. Test Monthly Activity Report Job (Instant)
```bash
python -c "from tasks import send_monthly_report; print(send_monthly_report())"
```
*Generates HTML and PDF reports under `static/reports/` for Admin and Companies.*

### 3. Redis Caching Demo
1. Clear cache (Cold Cache): Open browser to `http://localhost:5000/cacheremove`
2. Open Student Dashboard $\rightarrow$ **Browse Drives** (`http://localhost:5000/#/student/drives`) $\rightarrow$ Visibly takes ~2s (Cache Miss & DB query).
3. Reload page (F5) $\rightarrow$ Loads **instantly < 5ms** (Cache Hit served from Redis).

---

## Project Structure

```text
mad2P-og/
├── app.py               # Flask Application Factory & Vue SPA routes
├── config.py            # Central Configuration (DB, Redis, Celery, Mail)
├── models.py            # SQLAlchemy Database Models (9 tables)
├── init_db.py           # Database seeder with realistic demo data
├── tasks.py             # Celery background tasks (Reminders, Reports, Exports)
├── reports.py           # Monthly Report HTML renderers & PDF engine (fpdf2)
├── cache_keys.py        # Redis cache helpers & namespace invalidation
├── celery_worker.py     # Celery worker entry point
├── routes/              # Modular API Blueprints
│   ├── auth.py          # JWT Login & Registration
│   ├── admin.py         # Admin management endpoints
│   ├── company.py       # Company drive & candidate endpoints
│   ├── student.py       # Student drive & application endpoints
│   └── api.py           # Flask-RESTful API resources
├── static/              # Frontend Assets
│   ├── js/              # Vue.js Components & Router
│   ├── reports/         # Generated Monthly PDF Reports
│   └── exports/         # Generated CSV Data Exports
└── templates/
    └── index.html       # Single Page Application HTML root
```

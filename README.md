# Placement Portal

Placement management web application for students, companies, and admin. Built with Flask, Vue.js, SQLite, Celery, and Redis.

## Features

- **Authentication & Roles**: JWT-based login for Admin, Company, and Student roles.
- **Admin Dashboard**: Approve companies/drives, manage users, and broadcast announcements.
- **Company Portal**: Post job drives, view applications, shortlist candidates, and schedule interviews.
- **Student Dashboard**: Browse eligible drives, apply for jobs, and track application status.
- **Background Tasks**: Scheduled reminders and activity reports via Celery & Redis.

## Tech Stack

- **Backend**: Python, Flask, Flask-SQLAlchemy, Flask-JWT-Extended
- **Frontend**: Vue.js 3, Vue Router, Bootstrap 5
- **Database**: SQLite (`placement_portal.db`)
- **Queue / Caching**: Redis, Celery, Celery Beat

## Setup & Running

### 1. Install Dependencies
```bash
python -m venv venv
# PowerShell (Windows):
.\venv\Scripts\Activate.ps1
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Initialize Database
```bash
python init_db.py
```

### 3. Run Application
Ensure Redis is running (`redis-server`), then start the servers in separate terminals:

**Terminal 1 (Flask Backend & Vue Frontend)**
```bash
python app.py
```
App runs at `http://127.0.0.1:5000`

**Terminal 2 (Celery Worker)**
```bash
celery -A celery_worker.celery worker --loglevel=info
```

**Terminal 3 (Celery Beat Scheduler)**
```bash
celery -A celery_worker.celery beat --loglevel=info
```

## Demo Credentials

- **Admin**: `admin@placementportal.com` / `admin123`
- **Company**: `hr@technova.com` / `password123`
- **Student**: `student2@test.com` / `password123`

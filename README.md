# Placement Portal

A placement management web app for students, companies, and admins — built with Flask, Vue.js, Celery, and Redis.

## Tech Stack

- **Backend:** Flask, Flask-SQLAlchemy, Flask-JWT-Extended
- **Frontend:** Vue.js 3, Vue Router, Bootstrap 5
- **Database:** SQLite
- **Jobs / Cache:** Redis, Celery, Celery Beat

## Setup

```bash
# 1. Create and activate virtual environment
python -m venv venv
source venv/bin/activate          # Windows: .\venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt

# 3. Seed the database
python init_db.py
```

## Running

Start all services before launching the app. Each in its own terminal:

```bash
# 1. Redis (Celery broker + cache)
redis-server

# 2. Mailhog (fake SMTP — catches all outgoing email locally)
docker run -d -p 1025:1025 -p 8025:8025 mailhog/mailhog

# 3. Celery worker
celery -A celery_worker.celery worker --loglevel=info

# 4. Celery beat (scheduled tasks)
celery -A celery_worker.celery beat --loglevel=info

# 5. Flask app
python app.py
```

| Service  | URL                    |
|----------|------------------------|
| App      | http://127.0.0.1:5000  |
| Mailhog  | http://localhost:8025  |

## Demo Credentials

| Role    | Email                        | Password    |
|---------|------------------------------|-------------|
| Admin   | admin@placementportal.com    | admin123    |
| Company | hr@technova.com              | password123 |
| Student | student2@test.com            | password123 |

## Features

- JWT auth with three roles: Admin, Company, Student
- Students can browse drives and apply; companies can post drives and shortlist candidates
- Admin can approve companies, manage users, and broadcast announcements
- API response caching via Redis (hit `/cacheremove` to flush during dev)
- Background tasks: interview reminders and monthly reports via Celery Beat
- Local email testing via Mailhog (`localhost:8025`)
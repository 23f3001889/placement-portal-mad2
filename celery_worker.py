"""
celery_worker.py — Entry point for Celery worker/beat processes.

Run with:
    celery -A celery_worker.celery worker --loglevel=info
    celery -A celery_worker.celery beat --loglevel=info

Reuses the Celery instance created in tasks.py. 
Creating another Flask/Celery instance here wud leave this worker with an empty task registry.
"""
from tasks import celery, flask_app  # noqa: F401 -- flask_app kept for parity/debugging

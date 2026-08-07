"""Celery application for background work: document generation, export
rendering, embedding backfills, scheduled review sweeps. Kept minimal
in Phase 0/1 — real tasks land in later phases (Document Generator,
Review Engine) — but the worker boots and is wired into Compose now so
later phases only need to add tasks, not infrastructure.
"""
from celery import Celery

from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "srs",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
)


@celery_app.task(name="srs.healthcheck")
def healthcheck() -> str:
    return "ok"

import uuid

from app.db import SessionLocal
from app.models.document import Document
from app.services.document_ai_service import process_document
from app.tasks.celery_app import celery_app


@celery_app.task(name='app.tasks.document_tasks.process_document_task')
def process_document_task(document_id: str) -> None:
    db = SessionLocal()
    try:
        row = db.get(Document, uuid.UUID(document_id))
        if row is None:
            return
        process_document(db, row)
    finally:
        db.close()

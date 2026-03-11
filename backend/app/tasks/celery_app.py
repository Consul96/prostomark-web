from celery import Celery

from app.config import settings

celery_app = Celery('prostomark', broker=settings.redis_url, backend=settings.redis_url, include=['app.tasks.document_tasks'])
celery_app.conf.task_routes = {'app.tasks.document_tasks.process_document_task': {'queue': 'documents'}}

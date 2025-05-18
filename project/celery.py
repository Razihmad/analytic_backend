# import logging
import os
from celery import Celery

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", os.getenv("DJANGO_SETTINGS_MODULE", default="project.settings")
)
app = Celery("project", broker=os.getenv("CELERY_BROKER_URL"))


app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()

# logger = logging.getLogger(__name__)
# app.log.setup_task_logger(logger=logger, level=logging.INFO)

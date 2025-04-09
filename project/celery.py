import os
from celery import Celery
from celery.signals import setup_logging

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", os.getenv("DJANGO_SETTINGS_MODULE", default="project.settings")
)
app = Celery("project", broker=os.getenv("CELERY_BROKER_URL"))


@setup_logging.connect
def config_loggers(*args, **kwargs):
    from logging.config import dictConfig
    from django.conf import settings

    dictConfig(settings.LOGGING)


app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()

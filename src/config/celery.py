from celery import Celery
from decouple import config
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('celeryapp')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

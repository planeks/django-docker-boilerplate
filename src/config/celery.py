from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.prod')

app = Celery('celeryapp')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

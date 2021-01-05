from celery import Celery
from decouple import config
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{{project_name}}.settings')

app = Celery(config('PROJECT_NAME', default='{{project_name}}'))
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

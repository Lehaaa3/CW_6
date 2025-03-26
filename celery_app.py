import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery(os.getenv('APP_NAME'))

app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.update(
    broker_connection_retry_on_startup=True,
)

app.autodiscover_tasks(['distribution'])

app.conf.beat_schedule = {
    'daily_tasks': {
        'task': 'distribution.tasks.daily_tasks',
        'schedule': crontab(minute='*/1'),
        'options': {'queue': 'mailing_queue'}
    },
    'weekly_tasks': {
        'task': 'distribution.tasks.weekly_tasks',
        'schedule': crontab(day_of_week='6'),
        'options': {'queue': 'mailing_queue'}
    },
    'monthly_tasks': {
        'task': 'distribution.tasks.monthly_tasks',
        'schedule': crontab(day_of_month='6'),
        'options': {'queue': 'mailing_queue'}
    },
}
app.conf.task_default_queue = 'mailing_queue'

"""
Celery application configuration.
"""
from celery import Celery
from celery.schedules import crontab

from app.core.config import settings


# Create Celery app
celery_app = Celery(
    "insurance_saas",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

# Configure Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
)

# Periodic task schedule
celery_app.conf.beat_schedule = {
    # Check and expire quotes daily at midnight
    'check-expired-quotes': {
        'task': 'app.tasks.quote_tasks.check_expired_quotes',
        'schedule': crontab(hour=0, minute=0),
    },
    # Send payment reminders twice daily
    'send-payment-reminders': {
        'task': 'app.tasks.payment_tasks.send_payment_reminders',
        'schedule': crontab(hour='8,16', minute=0),  # 8 AM and 4 PM
    },
    # Send overdue reminders daily
    'send-overdue-reminders': {
        'task': 'app.tasks.payment_tasks.send_overdue_reminders',
        'schedule': crontab(hour=9, minute=0),  # 9 AM daily
    },
    # Check policy renewals daily
    'check-policy-renewals': {
        'task': 'app.tasks.policy_tasks.check_policy_renewals',
        'schedule': crontab(hour=10, minute=0),  # 10 AM daily
    },
    # Auto-lapse unpaid policies daily
    'auto-lapse-policies': {
        'task': 'app.tasks.policy_tasks.auto_lapse_policies',
        'schedule': crontab(hour=1, minute=0),  # 1 AM daily
    },
    # Generate daily financial report
    'generate-daily-report': {
        'task': 'app.tasks.report_tasks.generate_daily_report',
        'schedule': crontab(hour=23, minute=0),  # 11 PM daily
    },
}

# Auto-discover tasks
celery_app.autodiscover_tasks(['app.tasks'])

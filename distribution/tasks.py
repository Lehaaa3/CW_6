from django.core.exceptions import ObjectDoesNotExist
from distribution.services import send_mailing
from celery import shared_task
import logging
from celery import Celery

from users.models import User

logger = logging.getLogger(__name__)


@shared_task(bind=True, retry_backoff=True, retry_kwargs={'max_retries': 5})
def start_distribution_task(self, user_id):
    """
    Filter mailing settings, set them is_active=True and starts all celery mailing tasks for current user
    :param user_id: user_id of current user authorised
    """
    logger.info('start_distribution_task started')
    from distribution.models import MailingSettings
    try:
        user = User.objects.get(pk=user_id)
        MailingSettings.objects.filter(owner=user).update(is_active=True)
        logger.info(f'MailingSettings of user {user.username} updated successfully (start mailings)')
    except ObjectDoesNotExist:
        logger.error(f"User with ID {user_id} was not found.")
    except Exception as e:
        logger.error(f'Error in start_distribution_task occurred: {e}')


@shared_task(bind=True, retry_backoff=True, retry_kwargs={'max_retries': 5})
def stop_distribution_task(self, user_id):
    """
    Filter mailing settings, set them is_active=False and stops all celery mailing tasks for current user
    :param user_id: user_id of current user authorised
    """
    logger.info('stop_distribution_task started')
    from distribution.models import MailingSettings
    try:
        user = User.objects.get(pk=user_id)
        MailingSettings.objects.filter(owner=user).update(is_active=False)
        logger.info(f'MailingSettings of user {user.username} updated successfully (stop mailings)')
    except ObjectDoesNotExist:
        logger.error(f"User with ID {user_id} was not found.")
    except Exception as e:
        logger.error(f'Error in stop_distribution_task occurred: {e}')


@shared_task(bind=True)
def daily_tasks(self):
    """
    Celery task. Filter mailing settings with periodicity="Раз в день" and starts sending messages
    """
    logger.info("daily task is running!!")
    from distribution.models import MailingSettings
    try:
        mailings = MailingSettings.objects.filter(periodicity="Раз в день", status="Запущена", is_active=True)
        if mailings.exists():
            for mailing in mailings:
                send_mailing(mailing)
    except Exception as e:
        logger.error(f"While sending messages error occurred: {e}")


@shared_task(bind=True)
def weekly_tasks(self):
    """
    Celery task. Filter mailing settings with periodicity="Раз в неделю" and starts sending messages
    """
    logger.info("weekly task is running!!")
    from distribution.models import MailingSettings
    mailings = MailingSettings.objects.filter(periodicity="Раз в неделю", status="Запущена", is_active=True)
    if mailings.exists():
        for mailing in mailings:
            try:
                send_mailing(mailing)
            except Exception as e:
                logger.error(f"While sending messages error occurred: {e}")


@shared_task(bind=True)
def monthly_tasks(self):
    """
    Celery task. Filter mailing settings with periodicity="Раз в месяц" and starts sending messages
    """
    logger.info("monthly task is running!!")
    from distribution.models import MailingSettings
    mailings = MailingSettings.objects.filter(periodicity="Раз в месяц", status="Запущена", is_active=True)
    if mailings.exists():
        for mailing in mailings:
            try:
                send_mailing(mailing)
            except Exception as e:
                logger.error(f"While sending messages error occurred: {e}")

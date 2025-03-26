import logging

from django.core.exceptions import ObjectDoesNotExist
from django.core.management import BaseCommand

from users.models import User
from ...tasks import stop_distribution_task

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Stop Celery beat schedule for a specific user.
    """

    def add_arguments(self, parser):

        parser.add_argument('user_id', type=int)

    def handle(self, *args, **options):
        """
        Handles the execution of the command.
        Stops a Celery tasks for a specified user.

        Args:
            options: user_id

        Raises:
            ObjectDoesNotExist: If the user with the given ID does not exist.
        """
        user_id = options['user_id']
        stop_distribution_task.delay(user_id)

        try:
            user = User.objects.get(id=user_id)
            stop_distribution_task.delay(user_id)
            logger.info(f'Tasks stoped for user: {user.username}')
        except ObjectDoesNotExist:
            logger.error(f"User with id - {user_id} doesn't exist")

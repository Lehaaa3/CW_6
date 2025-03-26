import logging

from django.core.exceptions import ObjectDoesNotExist
from django.core.management import BaseCommand

from users.models import User
from ...tasks import start_distribution_task

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Runs Celery beat schedule for a specific user.
    """

    def add_arguments(self, parser):
        """
        Adds command-line argument to the parser.

        Args:
            parser: parser argument
        """
        parser.add_argument('user_id', type=int)

    def handle(self, *args, **options):
        """
        Handles the execution of the command.
        Starts a Celery task to run the beat schedule for the specified user.

        Args:
            options: user_id

        Raises:
            ObjectDoesNotExist: If the user with the given ID doesn't exist.
        """
        user_id = options['user_id']
        start_distribution_task.delay(user_id)

        try:
            user = User.objects.get(id=user_id)
            start_distribution_task.delay(user_id)
            logger.info(f'Tasks is running for the user: {user.username}')
        except ObjectDoesNotExist:
            logger.error(f"User with id - {user_id} doesn't exist")

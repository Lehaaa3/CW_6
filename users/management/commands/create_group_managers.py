from django.core.management import BaseCommand
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission


class Command(BaseCommand):
    """
    Command for Managers group creation and set appropriate permissions.
    """

    def handle(self, *args, **options):
        managers_group = Group.objects.create(name='Managers')

        can_see_all_clients = Permission.objects.get(codename='can_see_all_clients')
        can_see_all_messages = Permission.objects.get(codename='can_see_all_messages')
        can_see_all_mailing_settings = Permission.objects.get(codename='can_see_all_mailing_settings')
        can_see_all_logs = Permission.objects.get(codename='can_see_all_logs')
        can_see_all_users = Permission.objects.get(codename='can_see_all_users')

        managers_group.permissions.add(can_see_all_clients, can_see_all_messages, can_see_all_mailing_settings,
                                       can_see_all_logs, can_see_all_users)

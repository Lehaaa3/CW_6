import logging
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.contrib.auth.models import Group, User

logger = logging.getLogger(__name__)


@receiver(m2m_changed, sender=User.groups.through)
def user_groups_changed(sender, instance, action, reverse, model, pk_set, **kwargs):
    """
    This signal needs for automatic change of user's 'is_staff' field when he was added to Manager group
    or removed from it.
    :param sender:
    :param instance: current user
    :param action: post_add or post_remove
    :param reverse:
    :param model:
    :param pk_set: pk set
    :param kwargs:
    """
    logger.info(f"Signal triggered: action={action}, instance={instance}, pk_set={pk_set}")
    if not isinstance(instance, User):
        logger.info("Signal triggered for non-User instance. Ignoring.")
        return

    if action == "post_add":
        try:
            managers_group = Group.objects.get(name="Managers")
        except Exception as e:
            logger.error(f"При получении группы произошла ошибка: '{e}'")
            return

        for pk in pk_set:
            group = Group.objects.get(pk=pk)
            if group == managers_group:
                user = instance
                if not user.is_staff:
                    user.is_staff = True
                    user.save()

    if action == "post_remove":
        try:
            managers_group = Group.objects.get(name="Managers")
        except Exception as e:
            logger.error(f"При получении группы произошла ошибка: '{e}'")
            return
        for pk in pk_set:
            group = Group.objects.get(pk=pk)
            if group == managers_group:
                user = instance
                if user.is_staff:
                    user.is_staff = False
                    user.save()

import logging
from smtplib import SMTPException
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from distribution.models import MailingSettings, Log

logger = logging.getLogger(__name__)


def send_mailing(mailing):
    """
    Checks if current date is between start and end dates of mailing settings.
    If true - send message and create log instance after it.
    If false - set mailing setting status on .COMPLETED.
    :param mailing: mailing settings instance
    """
    now = timezone.localtime(timezone.now())
    if mailing.start_time <= now <= mailing.end_time:
        client_list = []

        for client in mailing.clients.all():
            client_list.append(client.email)
        for client in client_list:
            try:
                result = send_mail(
                    subject=mailing.message.title,
                    message=mailing.message.text,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[client],
                    fail_silently=False
                )
                log = Log.objects.create(
                    time=mailing.start_time,
                    status=result,
                    server_response='OK',
                    mailing_list=mailing,
                    recipient=client,
                    owner=mailing.owner
                )
                log.save()
                logger.info(f"Message with id: {mailing.message.pk} was successfully sent to {client}")
            except SMTPException as error:
                log = Log.objects.create(
                    time=mailing.start_time,
                    status=False,
                    server_response=str(error),
                    mailing_list=mailing,
                    recipient=client,
                    owner = mailing.owner
                )
                log.save()
                logger.error(f"While sending message with id: {mailing.message.pk} to {client} error occurred: {error}")

    else:
        mailing.status = MailingSettings.COMPLETED
        mailing.save()
        logger.info(f"Mailing with id {mailing.pk} was finished")

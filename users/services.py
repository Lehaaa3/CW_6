import logging
import random
from smtplib import SMTPException
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)

def send_greeting_email(username, user_email):
    """
    Send greeting message to the new user.
    :param username: username
    :param user_email: user email
    """
    try:
        send_mail(
            subject='LehStore',
            message=f"Поздравляю, {username}, вы успешно зарегестрировались. "
                    f"Теперь вы можете пользоваться услугами нашего магазина!",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user_email],
            fail_silently=False
        )
    except SMTPException as e:
        logger.error(f"При отправке приветственного письма возникла ошибка: {e}")


def send_verification_email(verification_link, user_email):
    """
    Send verification message to user after registration.
    :param verification_link: verification link
    :param user_email: user email
    """
    try:
        send_mail(
            subject='LehStore',
            message=f"Для подтверждения email и активации аккаунта перейдите по ссылке: {verification_link}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user_email],
            fail_silently=False
        )
    except SMTPException as e:
        logger.error(f"При отправке письма с ссылкой для подтверждения email возникла ошибка: {e}")


def create_verification_code():
    """
    Create random code.
    :returns: str
    """
    return ''.join([str(random.randint(0, 9)) for i in range(13)])


def send_restore_password_email(restore_link, user_email):
    """
    Send message to user with link for restore password.
    :param restore_link: restore link
    :param user_email: user email
    """
    try:
        send_mail(
            subject='LehStore',
            message=f"Для восстановления пароля перейдите по ссылке: {restore_link}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user_email],
            fail_silently=False
        )
    except SMTPException as e:
        logger.error(f"При отправке письма с ссылкой для восстановления пароля возникла ошибка: {e}")

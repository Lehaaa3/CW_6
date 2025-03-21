from django.contrib.auth.models import AbstractUser
from django.db import models
from django_countries.fields import CountryField

NULLABLE = {'null': True, 'blank': True}


class User(AbstractUser):
    avatar = models.ImageField(upload_to='users/', verbose_name='аватар', **NULLABLE)
    email = models.EmailField(unique=True, verbose_name='почта')
    phone = models.CharField(max_length=35, verbose_name='телефон', **NULLABLE)
    country = CountryField(verbose_name='страна', **NULLABLE)
    email_verification = models.CharField(max_length=35, verbose_name='код верификации email', **NULLABLE)
    restore_password_verification = models.CharField(max_length=35, verbose_name='код верификации email', **NULLABLE)
    is_blocked = models.BooleanField(default=False, verbose_name='флаг блокировки')

    def __str__(self):
        return self.email

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'
        permissions = [
            ("can_see_all_users", "Can see all users"),
        ]

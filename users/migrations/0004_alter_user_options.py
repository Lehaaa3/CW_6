# Generated by Django 5.1.6 on 2025-03-11 14:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_user_restore_password_verification'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'permissions': [('can_see_all_users', 'Can see all users')], 'verbose_name': 'пользователь', 'verbose_name_plural': 'пользователи'},
        ),
    ]

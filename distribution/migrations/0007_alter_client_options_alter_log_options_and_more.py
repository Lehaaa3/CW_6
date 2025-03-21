# Generated by Django 5.1.6 on 2025-03-13 12:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('distribution', '0006_alter_client_options_alter_log_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='client',
            options={'ordering': ['owner', 'id'], 'permissions': [('can_see_all_clients', 'Can see all clients')], 'verbose_name': 'клиент', 'verbose_name_plural': 'клиенты'},
        ),
        migrations.AlterModelOptions(
            name='log',
            options={'ordering': ['-time'], 'permissions': [('can_see_all_logs', 'Can see all logs')], 'verbose_name': 'лог', 'verbose_name_plural': 'логи'},
        ),
        migrations.AlterModelOptions(
            name='mailingsettings',
            options={'ordering': ['owner', 'id'], 'permissions': [('can_see_all_mailing_settings', 'Can see all mailing settings')], 'verbose_name': 'настройки рассылки', 'verbose_name_plural': 'настройки рассылки'},
        ),
        migrations.AlterModelOptions(
            name='message',
            options={'ordering': ['owner', 'id'], 'permissions': [('can_see_all_messages', 'Can see all messages')], 'verbose_name': 'сообщение', 'verbose_name_plural': 'сообщения'},
        ),
    ]

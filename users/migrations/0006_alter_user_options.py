# Generated by Django 5.1.6 on 2025-03-13 12:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_user_is_blocked'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'ordering': [models.Case(models.When(is_superuser=True, then=0), models.When(is_staff=True, then=1), models.When(is_blocked=False, then=2), default=3, output_field=models.IntegerField())], 'permissions': [('can_see_all_users', 'Can see all users')], 'verbose_name': 'пользователь', 'verbose_name_plural': 'пользователи'},
        ),
    ]

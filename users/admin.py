from django.contrib import admin

from users.models import User


@admin.register(User)
class USerAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'is_staff', 'country', 'avatar')

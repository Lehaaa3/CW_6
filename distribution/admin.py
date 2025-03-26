from django.contrib import admin

from distribution.models import Client, MailingSettings, Message, Log


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'email', 'FIO')
    list_filter = ('FIO',)
    search_fields = ('email', 'FIO', 'comment',)


@admin.register(MailingSettings)
class MailingListSettingsAdmin(admin.ModelAdmin):
    list_display = ('pk', 'start_time', 'end_time', 'periodicity', 'status', 'message')
    list_filter = ('start_time', 'end_time', 'periodicity', 'status',)
    search_fields = ('start_time', 'end_time',)


@admin.register(Message)
class MessageListSettingsAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title',)
    search_fields = ['title', 'text', ]


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ['pk', 'mailing_list', 'time', 'status', 'server_response', ]
    list_filter = ['mailing_list', 'status', ]
    search_fields = ['mailing_list', 'time', 'status', ]

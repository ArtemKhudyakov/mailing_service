from django.contrib import admin
from .models import Client, Message, Mailing, MailingAttempt

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('email', 'full_name', 'owner')
    search_fields = ('email', 'full_name')
    list_filter = ('owner',)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'owner')
    search_fields = ('subject', 'body')
    list_filter = ('owner',)

@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ('id', 'start_time', 'end_time', 'status', 'owner')
    list_filter = ('status', 'owner')
    filter_horizontal = ('clients',)

@admin.register(MailingAttempt)
class MailingAttemptAdmin(admin.ModelAdmin):
    list_display = ('id', 'attempt_time', 'status', 'mailing')
    list_filter = ('status', 'mailing__owner')
    readonly_fields = ('attempt_time',)
from django.contrib import admin
from .models import Audit, Finding


@admin.register(Audit)
class AuditAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'created_by', 'created_at')
    list_filter = ('status', 'created_at')


@admin.register(Finding)
class FindingAdmin(admin.ModelAdmin):
    list_display = ('title', 'audit', 'severity', 'resolved', 'created_at')
    list_filter = ('severity', 'resolved')

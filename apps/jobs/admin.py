from django.contrib import admin
from .models import Job


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display  = (
        'id', 'title', 'company', 'status', 'job_type',
        'experience_level', 'view_count', 'application_count', 'deadline', 'created_at',
    )
    list_filter   = ('status', 'job_type', 'experience_level')
    search_fields = ('title', 'company__name', 'location')
    readonly_fields = ('id', 'view_count', 'application_count', 'created_at', 'updated_at')
    ordering = ('-created_at',)
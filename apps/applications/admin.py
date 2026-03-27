from django.contrib import admin
from .models import Application, SavedJob


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display  = ('id', 'candidate', 'job', 'status', 'created_at')
    list_filter   = ('status',)
    search_fields = ('candidate__email', 'job__title')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('-created_at',)


@admin.register(SavedJob)
class SavedJobAdmin(admin.ModelAdmin):
    list_display  = ('id', 'candidate', 'job', 'created_at')
    search_fields = ('candidate__email', 'job__title')
    readonly_fields = ('id', 'created_at', 'updated_at')

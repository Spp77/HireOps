from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display  = ('id', 'email', 'username', 'role', 'is_active', 'date_joined')
    list_filter   = ('role', 'is_active', 'is_staff')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    readonly_fields = ('id', 'pkid', 'date_joined', 'last_login')
    ordering = ('-date_joined',)

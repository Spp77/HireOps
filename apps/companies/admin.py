from django.contrib import admin
from .models import Company, CompanyFollow


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display  = ('id', 'name', 'recruiter', 'location', 'industry', 'created_at')
    list_filter   = ('industry',)
    search_fields = ('name', 'email', 'location', 'recruiter__email')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('name',)


@admin.register(CompanyFollow)
class CompanyFollowAdmin(admin.ModelAdmin):
    list_display  = ('id', 'candidate', 'company', 'created_at')
    search_fields = ('candidate__email', 'company__name')
    readonly_fields = ('id', 'created_at', 'updated_at')
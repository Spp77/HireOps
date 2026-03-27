from django.contrib import admin
from .models import CandidateProfile, WorkExperience, Education


class WorkExperienceInline(admin.TabularInline):
    model = WorkExperience
    extra = 0
    readonly_fields = ('id', 'created_at', 'updated_at')


class EducationInline(admin.TabularInline):
    model = Education
    extra = 0
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(CandidateProfile)
class CandidateProfileAdmin(admin.ModelAdmin):
    list_display  = ('id', 'user', 'headline', 'location', 'experience_years', 'created_at')
    search_fields = ('user__email', 'headline', 'location')
    readonly_fields = ('id', 'created_at', 'updated_at')
    inlines = [WorkExperienceInline, EducationInline]

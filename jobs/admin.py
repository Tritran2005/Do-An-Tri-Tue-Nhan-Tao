from django.contrib import admin
from .models import JobPosting, Application

@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ('title', 'hr', 'min_experience', 'salary_range', 'location', 'job_type', 'is_active', 'created_at')
    list_filter = ('is_active', 'job_type', 'min_experience', 'created_at')
    search_fields = ('title', 'description', 'required_skills', 'hr__username', 'hr__company_name')

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'job', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('candidate__username', 'candidate__email', 'job__title', 'parsed_text')
    readonly_fields = ('parsed_text', 'extracted_skills', 'created_at', 'updated_at')

from django.contrib import admin
from .models import JobDescription, JobMatch


@admin.register(JobDescription)
class JobDescriptionAdmin(admin.ModelAdmin):
    list_display = ["title", "company", "user", "created_at"]
    search_fields = ["title", "company", "user__email"]


@admin.register(JobMatch)
class JobMatchAdmin(admin.ModelAdmin):
    list_display = ["resume", "job", "user", "match_score", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["user__email"]

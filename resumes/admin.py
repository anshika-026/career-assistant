from django.contrib import admin
from .models import Resume


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ["original_filename", "user", "file_type", "parsing_status", "word_count", "uploaded_at"]
    list_filter = ["parsing_status", "file_type"]
    search_fields = ["original_filename", "user__email"]
    readonly_fields = ["parsed_text", "word_count", "parsing_status", "parsing_error", "uploaded_at"]

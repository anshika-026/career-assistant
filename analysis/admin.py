from django.contrib import admin
from .models import AnalysisResult


@admin.register(AnalysisResult)
class AnalysisResultAdmin(admin.ModelAdmin):
    list_display = ["resume", "user", "ats_score", "word_count", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["user__email", "resume__original_filename"]
    readonly_fields = [f.name for f in AnalysisResult._meta.fields]

from django.contrib import admin
from .models import InterviewSession, LearningRecommendation


@admin.register(InterviewSession)
class InterviewSessionAdmin(admin.ModelAdmin):
    list_display = ["resume", "job", "user", "created_at"]
    search_fields = ["user__email"]


@admin.register(LearningRecommendation)
class LearningRecommendationAdmin(admin.ModelAdmin):
    list_display = ["job_match", "user", "created_at"]
    search_fields = ["user__email"]

from rest_framework import serializers
from .models import InterviewSession, LearningRecommendation


class InterviewSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewSession
        fields = ["id", "resume", "job", "questions", "created_at"]
        read_only_fields = ["id", "questions", "created_at"]


class LearningRecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningRecommendation
        fields = ["id", "job_match", "recommendations", "created_at"]
        read_only_fields = ["id", "recommendations", "created_at"]

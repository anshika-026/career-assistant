from rest_framework import serializers
from .models import AnalysisResult


class AnalysisResultSerializer(serializers.ModelSerializer):
    resume_filename = serializers.CharField(source="resume.original_filename", read_only=True)

    class Meta:
        model = AnalysisResult
        fields = [
            "id", "resume", "resume_filename", "ats_score", "word_count",
            "sections_found", "contact_info", "skills_found",
            "score_breakdown", "issues", "created_at",
        ]
        read_only_fields = fields

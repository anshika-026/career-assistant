from rest_framework import serializers
from .models import JobDescription, JobMatch


class JobDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobDescription
        fields = ["id", "title", "company", "raw_text", "required_skills", "created_at"]
        read_only_fields = ["id", "required_skills", "created_at"]


class JobMatchSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source="job.title", read_only=True)
    resume_filename = serializers.CharField(source="resume.original_filename", read_only=True)

    class Meta:
        model = JobMatch
        fields = [
            "id", "resume", "resume_filename", "job", "job_title",
            "match_score", "matched_skills", "missing_skills", "created_at",
        ]
        read_only_fields = ["id", "match_score", "matched_skills", "missing_skills", "created_at"]

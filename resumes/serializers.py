from rest_framework import serializers
from .models import Resume


class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = [
            "id", "file", "original_filename", "file_type",
            "parsed_text", "parsing_status", "parsing_error",
            "word_count", "uploaded_at", "is_active",
        ]
        read_only_fields = [
            "id","original_filename", "file_type", "parsed_text", "parsing_status", "parsing_error",
            "word_count", "uploaded_at",
        ]


class ResumeListSerializer(serializers.ModelSerializer):
    """Lighter serializer for list views -- omits full parsed_text."""
    class Meta:
        model = Resume
        fields = [
            "id", "original_filename", "file_type", "parsing_status",
            "word_count", "uploaded_at", "is_active",
        ]

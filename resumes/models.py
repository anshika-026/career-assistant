from django.conf import settings
from django.db import models


def resume_upload_path(instance, filename):
    return f"resumes/user_{instance.user_id}/{filename}"


class Resume(models.Model):
    class ParsingStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        PARSED = "parsed", "Parsed"
        FAILED = "failed", "Failed"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="resumes")
    file = models.FileField(upload_to=resume_upload_path)
    original_filename = models.CharField(max_length=255)
    file_type = models.CharField(max_length=10)  # pdf / docx
    parsed_text = models.TextField(blank=True)
    parsing_status = models.CharField(
        max_length=10, choices=ParsingStatus.choices, default=ParsingStatus.PENDING
    )
    parsing_error = models.CharField(max_length=500, blank=True)
    word_count = models.PositiveIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"{self.original_filename} ({self.user.email})"

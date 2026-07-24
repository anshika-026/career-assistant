from django.conf import settings
from django.db import models
from resumes.models import Resume


class JobDescription(models.Model):
    """A job posting the user pastes in to match their resume against."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="job_descriptions")
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255, blank=True)
    raw_text = models.TextField()
    required_skills = models.JSONField(default=dict)  # {skill: category}, extracted on save
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} @ {self.company or 'Unknown'}"


class JobMatch(models.Model):
    """Result of comparing one resume against one job description."""
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name="job_matches")
    job = models.ForeignKey(JobDescription, on_delete=models.CASCADE, related_name="matches")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="job_matches")

    match_score = models.PositiveSmallIntegerField()  # 0-100
    matched_skills = models.JSONField(default=list)
    missing_skills = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Match<{self.resume.original_filename} vs {self.job.title}, {self.match_score}%>"

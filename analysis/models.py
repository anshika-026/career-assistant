from django.conf import settings
from django.db import models
from resumes.models import Resume


class AnalysisResult(models.Model):
    """One ATS scoring run against a specific resume."""
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name="analyses")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="analyses")

    ats_score = models.PositiveSmallIntegerField()
    word_count = models.PositiveIntegerField()

    sections_found = models.JSONField(default=dict)
    contact_info = models.JSONField(default=dict)
    skills_found = models.JSONField(default=dict)   # {skill: category}
    score_breakdown = models.JSONField(default=dict)
    issues = models.JSONField(default=list)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Analysis<{self.resume.original_filename}, score={self.ats_score}>"

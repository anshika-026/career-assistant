from django.conf import settings
from django.db import models
from resumes.models import Resume
from jobs.models import JobDescription


class InterviewSession(models.Model):
    """A generated set of interview questions for a resume + (optional) job."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="interview_sessions")
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name="interview_sessions")
    job = models.ForeignKey(JobDescription, on_delete=models.SET_NULL, null=True, blank=True, related_name="interview_sessions")
    questions = models.JSONField(default=list)  # [{question, category, difficulty}]
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"InterviewSession<{self.resume.original_filename}>"


class LearningRecommendation(models.Model):
    """Learning suggestions generated from a job match's missing skills."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="learning_recommendations")
    job_match = models.ForeignKey("jobs.JobMatch", on_delete=models.CASCADE, related_name="learning_recommendations")
    recommendations = models.JSONField(default=list)  # [{skill, why_it_matters, how_to_learn}]
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"LearningRecommendation<match={self.job_match_id}>"

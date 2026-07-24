"""
Sends a notification email when a resume analysis finishes.
Runs synchronously via Django's EMAIL_BACKEND (console backend in dev,
so emails just print to the terminal instead of actually sending).

For production scale, swap this to a Celery task (celery.py is already
scaffolded) so email sending doesn't block the request/response cycle.
"""
import logging

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings

from .models import AnalysisResult

logger = logging.getLogger(__name__)


@receiver(post_save, sender=AnalysisResult)
def notify_analysis_complete(sender, instance, created, **kwargs):
    if not created:
        return

    user = instance.user
    if not user.email:
        return

    subject = "Your resume analysis is ready"
    message = (
        f"Hi {user.username},\n\n"
        f"Your ATS score is {instance.ats_score}/100.\n"
        f"We found {len(instance.skills_found)} recognizable skills on your resume.\n\n"
        f"Top things to improve:\n"
        + "\n".join(f"- {issue}" for issue in instance.issues[:5])
        + "\n\nLog in to your dashboard to see the full breakdown."
    )

    try:
        send_mail(
            subject, message,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@careerassistant.local"),
            recipient_list=[user.email],
            fail_silently=True,
        )
    except Exception:
        logger.exception("Failed to send analysis-complete email")

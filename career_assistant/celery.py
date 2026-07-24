"""
Celery app config. Not required to run the project (email sends
synchronously by default) -- this is here so you can move slow tasks
(email, AI calls, large-file parsing) off the request/response cycle
later without restructuring anything.

To use it:
  1. Run Redis locally (or point CELERY_BROKER_URL at your broker).
  2. Run a worker: `celery -A career_assistant worker -l info`
  3. Convert a function to a task with the @shared_task decorator and
     call `.delay(...)` instead of calling it directly.
"""
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "career_assistant.settings")

app = Celery("career_assistant")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

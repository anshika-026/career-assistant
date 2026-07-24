from django.urls import path
from .views import (
    JobDescriptionListCreateView, JobDescriptionDetailView,
    MatchResumeToJobView, JobMatchListView,
)

urlpatterns = [
    path("", JobDescriptionListCreateView.as_view(), name="job-list-create"),
    path("<int:pk>/", JobDescriptionDetailView.as_view(), name="job-detail"),
    path("matches/", JobMatchListView.as_view(), name="job-match-list"),
    path("<int:job_id>/match/<int:resume_id>/", MatchResumeToJobView.as_view(), name="job-match-create"),
]

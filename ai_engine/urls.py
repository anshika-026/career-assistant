from django.urls import path
from .views import (
    GenerateInterviewQuestionsView, InterviewSessionListView,
    GenerateLearningRecommendationsView, LearningRecommendationListView,
)

urlpatterns = [
    path("interview-questions/<int:resume_id>/", GenerateInterviewQuestionsView.as_view(), name="generate-interview-questions"),
    path("interview-questions/", InterviewSessionListView.as_view(), name="interview-session-list"),
    path("learning-recommendations/<int:job_match_id>/", GenerateLearningRecommendationsView.as_view(), name="generate-learning-recommendations"),
    path("learning-recommendations/", LearningRecommendationListView.as_view(), name="learning-recommendation-list"),
]

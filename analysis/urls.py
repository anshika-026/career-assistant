from django.urls import path
from .views import AnalyzeResumeView, AnalysisListView, AnalysisDetailView

urlpatterns = [
    path("", AnalysisListView.as_view(), name="analysis-list"),
    path("<int:pk>/", AnalysisDetailView.as_view(), name="analysis-detail"),
    path("analyze/<int:resume_id>/", AnalyzeResumeView.as_view(), name="analyze-resume"),
]

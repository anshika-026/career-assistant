from django.urls import path
from .views import ResumeListCreateView, ResumeDetailView, ResumeReparseView

urlpatterns = [
    path("", ResumeListCreateView.as_view(), name="resume-list-create"),
    path("<int:pk>/", ResumeDetailView.as_view(), name="resume-detail"),
    path("<int:pk>/reparse/", ResumeReparseView.as_view(), name="resume-reparse"),
]

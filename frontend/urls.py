from django.urls import path
from django.views.generic import RedirectView
from .views import LoginPageView, DashboardPageView

urlpatterns = [
    path("", RedirectView.as_view(url="/login/", permanent=False)),
    path("login/", LoginPageView.as_view(), name="login-page"),
    path("dashboard/", DashboardPageView.as_view(), name="dashboard-page"),
]

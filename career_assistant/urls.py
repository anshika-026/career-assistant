from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("accounts.urls")),
    path("api/resumes/", include("resumes.urls")),
    path("api/analysis/", include("analysis.urls")),
    path("api/jobs/", include("jobs.urls")),
    path("api/ai/", include("ai_engine.urls")),
    path("api/dashboard/", include("dashboard.urls")),
    path("", include("frontend.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

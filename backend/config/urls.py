from django.contrib import admin
from django.urls import path, re_path, include
from django.conf import settings
from django.conf.urls.static import static
from dashboard import views as dashboard_views

urlpatterns = [
    path("admin/", admin.site.urls),

    path("api/", include("dashboard.urls")),
    path("api/accounts/", include("accounts.urls")),

    path("", dashboard_views.dashboard_home, name="dashboard_home"),
    re_path(r"^(?!api/|admin/|media/|static/).*", dashboard_views.dashboard_home),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
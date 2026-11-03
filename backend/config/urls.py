from django.contrib import admin
from django.urls import path, re_path, include
from django.conf import settings
from django.conf.urls.static import static
from dashboard import views as dashboard_views
from utilities import views as utility_views
from utilities.licensing import check_indicator_license, check_license

urlpatterns = [
    path("admin/", admin.site.urls),

    path("api/licenses/indicator/", check_indicator_license, name="indicator-license-check"),
    path("api/licenses/check/", check_license, name="ea-license-check"),
    path("api/utilities/", include("utilities.urls")),
    path("utilities", utility_views.library_page, name="utility-library"),
    path("utilities/", utility_views.library_page),
    path("api/", include("dashboard.urls")),

    path("", dashboard_views.dashboard_home, name="dashboard_home"),
    re_path(r"^(?!api/|admin/|accounts/|media/|static/).*", dashboard_views.dashboard_home),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
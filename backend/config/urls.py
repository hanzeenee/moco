from django.contrib import admin
from django.urls import path, re_path, include
from dashboard import views as dashboard_views

urlpatterns = [
    path("admin/", admin.site.urls),

    path("api/", include("dashboard.urls")),
    path("api/accounts/", include("accounts.urls")),

    path("", dashboard_views.dashboard_home, name="dashboard_home"),
    re_path(r"^(?!api/|admin/).*", dashboard_views.dashboard_home),
]
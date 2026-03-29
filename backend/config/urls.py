from django.contrib import admin
from django.urls import path, re_path, include
from django.views.generic import TemplateView

urlpatterns = [
    path("admin/", admin.site.urls),

    # API 연결
    path("api/", include("dashboard.urls")),

    # SPA 캐치올: api/ 로 시작하지 않는 경로만 home.html
    re_path(r"^(?!api/).*", TemplateView.as_view(template_name="home.html")),
]
# root/backend/config/urls.py
from django.contrib import admin
from django.urls import path, re_path
from django.views.generic import TemplateView

urlpatterns = [
    path("admin/", admin.site.urls),

    # API가 있다면 아래처럼 "캐치올보다 위"에 먼저 등록
    # path("api/", include("api.urls")),

    # SPA 캐치올: api/ 로 시작하는 경로만 제외하고 전부 home.html로 보냄
    re_path(r"^(?!api/).*", TemplateView.as_view(template_name="home.html")),
]
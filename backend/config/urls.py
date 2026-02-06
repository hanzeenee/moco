from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),

    # 대시보드 홈 (허브)
    path("dashboard/", include("dashboard.urls")),

    # 강의 도메인
    path("lectures/", include("lectures.urls")),

    # 상단바 단순 링크 redirect (home / youtube / cafe / EA / PT)
    path("", include("nav.urls")),
]

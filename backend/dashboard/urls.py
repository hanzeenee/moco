from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard_home, name="dashboard_home"),
    path("api/dashboard/", views.dashboard_data, name="dashboard_data"),
    path("api/comments/", views.comments_api, name="comments_api"),
]
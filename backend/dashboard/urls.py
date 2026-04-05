from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.dashboard_data, name="dashboard_data"),
    path("comments/", views.comments_api, name="comments_api"),
]
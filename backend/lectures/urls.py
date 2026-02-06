from django.urls import path
from . import views

urlpatterns = [
    path("", views.lecture_list, name="lecture_list"),
]

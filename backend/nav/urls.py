from django.urls import path
from . import views

urlpatterns = [
    path("go/<str:key>/", views.go, name="nav_go"),
]

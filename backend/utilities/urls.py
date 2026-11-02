from django.urls import path
from . import views

urlpatterns = [
    path("session/", views.session_status, name="utility-session"),
    path("login/", views.login, name="utility-login"),
    path("logout/", views.logout, name="utility-logout"),
    path("library/", views.library_data, name="utility-library-data"),
]

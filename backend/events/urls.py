from django.urls import path
from . import views

urlpatterns = [
    path("<str:event_type>/", views.event_list, name="event_list"),
]

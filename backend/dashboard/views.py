from django.shortcuts import render
from django.http import JsonResponse
from .models import NavLink, Lecture, Event


def dashboard_home(request):
    return render(request, "home.html")


def dashboard_data(request):
    nav_links = list(NavLink.objects.values())
    lectures = list(Lecture.objects.values())
    events = list(Event.objects.values())

    data = {
        "nav_links": nav_links,
        "lectures": lectures,
        "events": events,
    }

    return JsonResponse(data)
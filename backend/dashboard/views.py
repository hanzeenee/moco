# dashboard/views.py
from django.shortcuts import render
from .models import Lecture


def dashboard_home(request):
    lectures = Lecture.objects.all().order_by("-id")
    return render(
        request,
        "home.html",
        {"lectures": lectures}
    )
